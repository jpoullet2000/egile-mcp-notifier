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

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


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
        
        self._calendar_service = None

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
