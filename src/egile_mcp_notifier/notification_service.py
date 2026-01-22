"""Notification service providing email and calendar capabilities."""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Any, Optional
import logging
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import msal
import requests

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Microsoft Graph API scopes
MS_SCOPES = ['Tasks.ReadWrite', 'offline_access']


class NotificationService:
    """Service for sending notifications via email and managing Google Calendar."""

    def __init__(self):
        """Initialize the notification service."""
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.default_from_email = os.getenv("DEFAULT_FROM_EMAIL", self.smtp_username)
        
        # Google Calendar configuration
        self.credentials_file = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
        self.token_file = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")
        self.default_calendar_id = os.getenv("DEFAULT_CALENDAR_ID", "primary")
        
        # Microsoft To-Do configuration
        self.ms_client_id = os.getenv("MS_TODO_CLIENT_ID")
        self.ms_tenant_id = os.getenv("MS_TODO_TENANT_ID", "common")
        self.ms_token_cache_file = os.getenv("MS_TODO_TOKEN_FILE", "ms_token_cache.json")
        
        self._calendar_service = None
        self._ms_token_cache = None

    def _get_calendar_service(self):
        """Get or create Google Calendar service."""
        if self._calendar_service:
            return self._calendar_service

        creds = None
        token_path = Path(self.token_file)
        
        # Load existing credentials
        if token_path.exists():
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not Path(self.credentials_file).exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please follow the Google Calendar setup instructions in README.md"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self._calendar_service = build('calendar', 'v3', credentials=creds)
        return self._calendar_service

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        cc: Optional[list[str]] = None,
        bcc: Optional[list[str]] = None,
        html: bool = False,
        from_email: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send an email notification.

        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body content
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html: Whether body is HTML (default: False)
            from_email: Sender email (default: from config)

        Returns:
            Dictionary with send status and details
        """
        if not self.smtp_username or not self.smtp_password:
            raise ValueError(
                "SMTP credentials not configured. "
                "Please set SMTP_USERNAME and SMTP_PASSWORD in .env file"
            )

        from_addr = from_email or self.default_from_email
        
        # Convert single recipient to list
        if isinstance(to, str):
            to = [to]

        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_addr
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        # Add body
        if html:
            part = MIMEText(body, 'html')
        else:
            part = MIMEText(body, 'plain')
        msg.attach(part)

        # Collect all recipients
        all_recipients = to[:]
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        try:
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg, from_addr, all_recipients)

            return {
                "success": True,
                "message": f"Email sent successfully to {len(all_recipients)} recipient(s)",
                "recipients": to,
                "cc": cc,
                "bcc_count": len(bcc) if bcc else 0,
                "subject": subject
            }

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipients": to,
                "subject": subject
            }

    def _normalize_datetime(self, dt_string: str) -> str:
        """
        Normalize datetime string to ISO 8601 format.
        
        Accepts formats like:
        - 20260120T10:00:00 (compact)
        - 2026-01-20T10:00:00 (ISO)
        - 2026-01-20T10:00:00Z (ISO with timezone)
        - 2026-01-20T10:00:00+02:00 (ISO with timezone offset)
        """
        from dateutil import parser
        
        try:
            # Try to parse the datetime string
            dt = parser.isoparse(dt_string)
            # Return in ISO format without timezone (Google Calendar will use the event timezone)
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            # If that fails, try parsing various formats
            try:
                dt = parser.parse(dt_string)
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                # If all else fails, return the original string
                # and let Google Calendar API return the error
                return dt_string

    def create_calendar_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        calendar_id: Optional[str] = None,
        timezone: str = "Europe/Brussels",
    ) -> dict[str, Any]:
        """
        Create a Google Calendar event.

        Args:
            summary: Event title
            start_time: Start time in ISO format (e.g., "2026-01-20T10:00:00" or "20260120T10:00:00")
            end_time: End time in ISO format
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee email addresses (optional)
            calendar_id: Calendar ID (default: primary)
            timezone: Timezone (default: Europe/Brussels)

        Returns:
            Dictionary with event details and link
        """
        try:
            service = self._get_calendar_service()
            cal_id = calendar_id or self.default_calendar_id

            # Normalize datetime formats
            normalized_start = self._normalize_datetime(start_time)
            normalized_end = self._normalize_datetime(end_time)

            event = {
                'summary': summary,
                'start': {
                    'dateTime': normalized_start,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': normalized_end,
                    'timeZone': timezone,
                },
            }

            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = service.events().insert(calendarId=cal_id, body=event).execute()

            return {
                "success": True,
                "event_id": created_event['id'],
                "summary": created_event.get('summary'),
                "start": created_event['start'].get('dateTime', created_event['start'].get('date')),
                "end": created_event['end'].get('dateTime', created_event['end'].get('date')),
                "html_link": created_event.get('htmlLink'),
                "message": "Calendar event created successfully"
            }

        except HttpError as e:
            logger.error(f"Failed to create calendar event: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": summary
            }

    def list_calendar_events(
        self,
        max_results: int = 10,
        calendar_id: Optional[str] = None,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        List upcoming calendar events.

        Args:
            max_results: Maximum number of events to return (default: 10)
            calendar_id: Calendar ID (default: primary)
            time_min: Lower bound (inclusive) for event start time (ISO format)
            time_max: Upper bound (exclusive) for event start time (ISO format)

        Returns:
            Dictionary with list of events
        """
        try:
            service = self._get_calendar_service()
            cal_id = calendar_id or self.default_calendar_id

            # Default to now if no time_min specified
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'

            events_result = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'html_link': event.get('htmlLink', '')
                })

            return {
                "success": True,
                "count": len(formatted_events),
                "events": formatted_events
            }

        except HttpError as e:
            logger.error(f"Failed to list calendar events: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def update_calendar_event(
        self,
        event_id: str,
        calendar_id: Optional[str] = None,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: str = "Europe/Brussels",
    ) -> dict[str, Any]:
        """
        Update an existing calendar event.

        Args:
            event_id: Event ID to update
            calendar_id: Calendar ID (default: primary)
            summary: New event title (optional)
            start_time: New start time in ISO format (optional)
            end_time: New end time in ISO format (optional)
            description: New description (optional)
            location: New location (optional)
            timezone: Timezone (default: Europe/Brussels)

        Returns:
            Dictionary with updated event details
        """
        try:
            service = self._get_calendar_service()
            cal_id = calendar_id or self.default_calendar_id

            # Get existing event
            event = service.events().get(calendarId=cal_id, eventId=event_id).execute()

            # Update fields if provided
            if summary:
                event['summary'] = summary
            
            if start_time:
                event['start'] = {
                    'dateTime': start_time,
                    'timeZone': timezone,
                }
            
            if end_time:
                event['end'] = {
                    'dateTime': end_time,
                    'timeZone': timezone,
                }
            
            if description is not None:
                event['description'] = description
            
            if location is not None:
                event['location'] = location

            updated_event = service.events().update(
                calendarId=cal_id,
                eventId=event_id,
                body=event
            ).execute()

            return {
                "success": True,
                "event_id": updated_event['id'],
                "summary": updated_event.get('summary'),
                "start": updated_event['start'].get('dateTime', updated_event['start'].get('date')),
                "end": updated_event['end'].get('dateTime', updated_event['end'].get('date')),
                "html_link": updated_event.get('htmlLink'),
                "message": "Calendar event updated successfully"
            }

        except HttpError as e:
            logger.error(f"Failed to update calendar event: {e}")
            return {
                "success": False,
                "error": str(e),
                "event_id": event_id
            }

    def delete_calendar_event(
        self,
        event_id: str,
        calendar_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Delete a calendar event.

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID (default: primary)

        Returns:
            Dictionary with deletion status
        """
        try:
            service = self._get_calendar_service()
            cal_id = calendar_id or self.default_calendar_id

            service.events().delete(calendarId=cal_id, eventId=event_id).execute()

            return {
                "success": True,
                "event_id": event_id,
                "message": "Calendar event deleted successfully"
            }

        except HttpError as e:
            logger.error(f"Failed to delete calendar event: {e}")
            return {
                "success": False,
                "error": str(e),
                "event_id": event_id
            }

    # Microsoft To-Do methods
    
    def _get_ms_token_cache(self):
        """Get or create Microsoft token cache."""
        if self._ms_token_cache is not None:
            return self._ms_token_cache
            
        self._ms_token_cache = msal.SerializableTokenCache()
        
        # Load existing cache if it exists
        if Path(self.ms_token_cache_file).exists():
            try:
                with open(self.ms_token_cache_file, 'r') as f:
                    self._ms_token_cache.deserialize(f.read())
            except Exception as e:
                logger.warning(f"Failed to load MS token cache: {e}")
        
        return self._ms_token_cache
    
    def _save_ms_token_cache(self):
        """Save Microsoft token cache to file."""
        if self._ms_token_cache and self._ms_token_cache.has_state_changed:
            try:
                with open(self.ms_token_cache_file, 'w') as f:
                    f.write(self._ms_token_cache.serialize())
            except Exception as e:
                logger.error(f"Failed to save MS token cache: {e}")
    
    def _get_ms_access_token(self) -> str:
        """Get Microsoft Graph API access token."""
        if not self.ms_client_id:
            raise ValueError(
                "Microsoft To-Do not configured. "
                "Please set MS_TODO_CLIENT_ID in .env file"
            )
        
        cache = self._get_ms_token_cache()
        
        app = msal.PublicClientApplication(
            self.ms_client_id,
            authority=f"https://login.microsoftonline.com/{self.ms_tenant_id}",
            token_cache=cache
        )
        
        # Try to get token from cache
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(MS_SCOPES, account=accounts[0])
            if result and "access_token" in result:
                return result["access_token"]
        
        # If no cached token, do interactive login
        flow = app.initiate_device_flow(scopes=MS_SCOPES)
        
        if "user_code" not in flow:
            raise ValueError(f"Failed to create device flow: {flow.get('error_description')}")
        
        print(flow["message"])
        
        result = app.acquire_token_by_device_flow(flow)
        
        if "access_token" not in result:
            raise ValueError(f"Failed to acquire token: {result.get('error_description')}")
        
        self._save_ms_token_cache()
        return result["access_token"]
    
    def _ms_graph_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make a request to Microsoft Graph API."""
        token = self._get_ms_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        
        # DELETE requests may not return content
        if response.status_code == 204:
            return {}
        
        return response.json()
    
    def create_todo(
        self,
        title: str,
        body: Optional[str] = None,
        due_date: Optional[str] = None,
        importance: str = "normal",
        list_id: Optional[str] = None,
        reminder_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a Microsoft To-Do task.
        
        Args:
            title: Task title
            body: Task body/notes (optional)
            due_date: Due date in ISO format (e.g., "2026-01-25") (optional)
            importance: Task importance - "low", "normal", or "high" (default: "normal")
            list_id: To-Do list ID (optional, uses default list if not specified)
            reminder_date: Reminder date/time in ISO format (optional)
        
        Returns:
            Dictionary with task details
        """
        try:
            # Get list ID if not provided
            if not list_id:
                lists = self._ms_graph_request("GET", "/me/todo/lists")
                if not lists.get("value"):
                    raise ValueError("No To-Do lists found")
                list_id = lists["value"][0]["id"]
            
            task_data = {
                "title": title,
                "importance": importance,
            }
            
            if body:
                task_data["body"] = {
                    "content": body,
                    "contentType": "text"
                }
            
            if due_date:
                task_data["dueDateTime"] = {
                    "dateTime": due_date,
                    "timeZone": "UTC"
                }
            
            if reminder_date:
                task_data["reminderDateTime"] = {
                    "dateTime": reminder_date,
                    "timeZone": "UTC"
                }
                task_data["isReminderOn"] = True
            
            result = self._ms_graph_request(
                "POST",
                f"/me/todo/lists/{list_id}/tasks",
                task_data
            )
            
            return {
                "success": True,
                "task_id": result["id"],
                "title": result["title"],
                "status": result.get("status"),
                "importance": result.get("importance"),
                "created_at": result.get("createdDateTime"),
                "web_link": result.get("webUrl"),
                "message": "To-Do task created successfully"
            }
        
        except Exception as e:
            logger.error(f"Failed to create To-Do task: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": title
            }
    
    def list_todos(
        self,
        list_id: Optional[str] = None,
        filter_status: Optional[str] = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """
        List Microsoft To-Do tasks.
        
        Args:
            list_id: To-Do list ID (optional, uses default list if not specified)
            filter_status: Filter by status - "notStarted", "inProgress", "completed" (optional)
            max_results: Maximum number of tasks to return (default: 50)
        
        Returns:
            Dictionary with list of tasks
        """
        try:
            # Get list ID if not provided
            if not list_id:
                lists = self._ms_graph_request("GET", "/me/todo/lists")
                if not lists.get("value"):
                    return {
                        "success": True,
                        "count": 0,
                        "tasks": [],
                        "message": "No To-Do lists found"
                    }
                list_id = lists["value"][0]["id"]
            
            endpoint = f"/me/todo/lists/{list_id}/tasks?$top={max_results}"
            
            if filter_status:
                endpoint += f"&$filter=status eq '{filter_status}'"
            
            result = self._ms_graph_request("GET", endpoint)
            
            tasks = []
            for task in result.get("value", []):
                tasks.append({
                    "id": task["id"],
                    "title": task["title"],
                    "status": task.get("status"),
                    "importance": task.get("importance"),
                    "body": task.get("body", {}).get("content", ""),
                    "due_date": task.get("dueDateTime", {}).get("dateTime"),
                    "created_at": task.get("createdDateTime"),
                    "completed_at": task.get("completedDateTime", {}).get("dateTime"),
                    "web_link": task.get("webUrl")
                })
            
            return {
                "success": True,
                "count": len(tasks),
                "tasks": tasks
            }
        
        except Exception as e:
            logger.error(f"Failed to list To-Do tasks: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_todo(
        self,
        task_id: str,
        list_id: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        status: Optional[str] = None,
        importance: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Update a Microsoft To-Do task.
        
        Args:
            task_id: Task ID to update
            list_id: To-Do list ID (optional, uses default list if not specified)
            title: New task title (optional)
            body: New task body (optional)
            status: New status - "notStarted", "inProgress", "completed" (optional)
            importance: New importance - "low", "normal", "high" (optional)
            due_date: New due date in ISO format (optional)
        
        Returns:
            Dictionary with updated task details
        """
        try:
            # Get list ID if not provided
            if not list_id:
                lists = self._ms_graph_request("GET", "/me/todo/lists")
                if not lists.get("value"):
                    raise ValueError("No To-Do lists found")
                list_id = lists["value"][0]["id"]
            
            update_data = {}
            
            if title:
                update_data["title"] = title
            
            if body is not None:
                update_data["body"] = {
                    "content": body,
                    "contentType": "text"
                }
            
            if status:
                update_data["status"] = status
            
            if importance:
                update_data["importance"] = importance
            
            if due_date:
                update_data["dueDateTime"] = {
                    "dateTime": due_date,
                    "timeZone": "UTC"
                }
            
            result = self._ms_graph_request(
                "PATCH",
                f"/me/todo/lists/{list_id}/tasks/{task_id}",
                update_data
            )
            
            return {
                "success": True,
                "task_id": result["id"],
                "title": result["title"],
                "status": result.get("status"),
                "importance": result.get("importance"),
                "message": "To-Do task updated successfully"
            }
        
        except Exception as e:
            logger.error(f"Failed to update To-Do task: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def delete_todo(
        self,
        task_id: str,
        list_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Delete a Microsoft To-Do task.
        
        Args:
            task_id: Task ID to delete
            list_id: To-Do list ID (optional, uses default list if not specified)
        
        Returns:
            Dictionary with deletion status
        """
        try:
            # Get list ID if not provided
            if not list_id:
                lists = self._ms_graph_request("GET", "/me/todo/lists")
                if not lists.get("value"):
                    raise ValueError("No To-Do lists found")
                list_id = lists["value"][0]["id"]
            
            self._ms_graph_request(
                "DELETE",
                f"/me/todo/lists/{list_id}/tasks/{task_id}"
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "message": "To-Do task deleted successfully"
            }
        
        except Exception as e:
            logger.error(f"Failed to delete To-Do task: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def list_todo_lists(self) -> dict[str, Any]:
        """
        List all Microsoft To-Do lists.
        
        Returns:
            Dictionary with list of To-Do lists
        """
        try:
            result = self._ms_graph_request("GET", "/me/todo/lists")
            
            lists = []
            for todo_list in result.get("value", []):
                lists.append({
                    "id": todo_list["id"],
                    "name": todo_list["displayName"],
                    "is_owner": todo_list.get("isOwner", False),
                    "is_shared": todo_list.get("isShared", False),
                })
            
            return {
                "success": True,
                "count": len(lists),
                "lists": lists
            }
        
        except Exception as e:
            logger.error(f"Failed to list To-Do lists: {e}")
            return {
                "success": False,
                "error": str(e)
            }
