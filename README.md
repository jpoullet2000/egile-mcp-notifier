# Egile MCP Notifier

MCP server providing notification capabilities including email sending and Google Calendar event management.

## Features

- **Email Notifications**: Send emails via SMTP
- **Google Calendar Integration**: Create, update, and manage calendar events
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

## License

MIT
