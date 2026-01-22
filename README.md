# Egile MCP Notifier

MCP server providing notification capabilities including email sending, Google Calendar event management, and Microsoft To-Do task management.

## Features

- **Email Notifications**: Send emails via SMTP
- **Google Calendar Integration**: Create, update, and manage calendar events
- **Microsoft To-Do Integration**: Create, update, and manage tasks and to-do lists
- **Flexible Configuration**: Support for multiple email providers and calendar accounts

## Installation

```bash
pip install -e .
```

## Configuration

Create a `.env` file with the following variables:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.json
DEFAULT_CALENDAR_ID=primary

# Microsoft To-Do Configuration
MS_TODO_CLIENT_ID=your-azure-app-client-id
MS_TODO_TENANT_ID=common
MS_TODO_TOKEN_FILE=ms_token_cache.json
```

### Gmail Setup

1. Enable 2-factor authentication in your Google account
2. Generate an App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Use the app password in your `.env` file

### Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials and save as `credentials.json`
6. On first run, you'll be prompted to authorize the application

### Microsoft To-Do Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Enter a name for your app (e.g., "Egile Notifier")
5. Under "Supported account types", select "Accounts in any organizational directory and personal Microsoft accounts"
6. Leave "Redirect URI" blank for now
7. Click "Register"
8. Copy the "Application (client) ID" - this is your `MS_TODO_CLIENT_ID`
9. Go to "API permissions" > "Add a permission" > "Microsoft Graph" > "Delegated permissions"
10. Add the following permissions:
    - `Tasks.ReadWrite`
    - `offline_access`
11. Click "Add permissions"
12. On first run, you'll be prompted to authenticate using a device code

**Detailed setup instructions**: See [MS_TODO_SETUP.md](MS_TODO_SETUP.md) for a complete step-by-step guide.

## Usage

### As MCP Server

```bash
egile-mcp-notifier
```

### Available Tools

#### send_email

Send an email notification.

```python
{
    "to": "recipient@example.com",
    "subject": "Hello",
    "body": "This is a test email",
    "cc": ["cc@example.com"],  # optional
    "bcc": ["bcc@example.com"],  # optional
    "html": True  # optional, default False
}
```

#### create_calendar_event

Create a Google Calendar event.

```python
{
    "summary": "Meeting with Team",
    "start_time": "2026-01-20T10:00:00",
    "end_time": "2026-01-20T11:00:00",
    "description": "Discuss project updates",  # optional
    "location": "Conference Room A",  # optional
    "attendees": ["attendee@example.com"],  # optional
    "calendar_id": "primary"  # optional
}
```

#### list_calendar_events

List upcoming calendar events.

```python
{
    "max_results": 10,  # optional, default 10
    "calendar_id": "primary",  # optional
    "time_min": "2026-01-17T00:00:00",  # optional
    "time_max": "2026-01-31T23:59:59"  # optional
}
```

#### update_calendar_event

Update an existing calendar event.

```python
{
    "event_id": "event123",
    "summary": "Updated Meeting",  # optional
    "start_time": "2026-01-20T10:30:00",  # optional
    "end_time": "2026-01-20T11:30:00",  # optional
    "description": "Updated description",  # optional
    "location": "New location",  # optional
    "calendar_id": "primary"  # optional
}
```

#### delete_calendar_event

Delete a calendar event.

```python
{
    "event_id": "event123",
    "calendar_id": "primary"  # optional
}
```

#### create_todo

Create a Microsoft To-Do task.

```python
{
    "title": "Complete project documentation",
    "body": "Add examples and API reference",  # optional
    "due_date": "2026-01-25",  # optional, ISO format
    "importance": "high",  # optional: "low", "normal", "high"
    "list_id": "list-id-123",  # optional, uses default list
    "reminder_date": "2026-01-24T09:00:00"  # optional, ISO format
}
```

#### list_todos

List Microsoft To-Do tasks.

```python
{
    "list_id": "list-id-123",  # optional, uses default list
    "filter_status": "notStarted",  # optional: "notStarted", "inProgress", "completed"
    "max_results": 50  # optional, default 50
}
```

#### update_todo

Update a Microsoft To-Do task.

```python
{
    "task_id": "task-id-123",
    "list_id": "list-id-123",  # optional
    "title": "Updated task title",  # optional
    "body": "Updated notes",  # optional
    "status": "completed",  # optional: "notStarted", "inProgress", "completed"
    "importance": "low",  # optional: "low", "normal", "high"
    "due_date": "2026-01-26"  # optional
}
```

#### delete_todo

Delete a Microsoft To-Do task.

```python
{
    "task_id": "task-id-123",
    "list_id": "list-id-123"  # optional
}
```

#### list_todo_lists

List all Microsoft To-Do lists.

```python
{}
```

## License

MIT
