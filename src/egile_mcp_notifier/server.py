"""MCP server for notification capabilities."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from .notification_service import NotificationService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class NotificationMCPServer:
    """MCP Server wrapping the notification service."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("egile-mcp-notifier")
        self.service = NotificationService()
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available notification tools."""
            return [
                Tool(
                    name="send_email",
                    description="Send an email notification via SMTP",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": ["string", "array"],
                                "items": {"type": "string"},
                                "description": "Recipient email address(es)",
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject",
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content",
                            },
                            "cc": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "CC recipients (optional)",
                            },
                            "bcc": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "BCC recipients (optional)",
                            },
                            "html": {
                                "type": "boolean",
                                "description": "Whether body is HTML (default: False)",
                            },
                            "from_email": {
                                "type": "string",
                                "description": "Sender email (optional, uses config default)",
                            },
                        },
                        "required": ["to", "subject", "body"],
                    },
                ),
                Tool(
                    name="create_calendar_event",
                    description="Create a Google Calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "Event title/summary",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Start time in ISO format (e.g., 2026-01-20T10:00:00)",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "End time in ISO format",
                            },
                            "description": {
                                "type": "string",
                                "description": "Event description (optional)",
                            },
                            "location": {
                                "type": "string",
                                "description": "Event location (optional)",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of attendee email addresses (optional)",
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone (default: Europe/Brussels)",
                            },
                        },
                        "required": ["summary", "start_time", "end_time"],
                    },
                ),
                Tool(
                    name="list_calendar_events",
                    description="List upcoming Google Calendar events",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of events to return (default: 10)",
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                            },
                            "time_min": {
                                "type": "string",
                                "description": "Lower bound for event start time in ISO format (optional)",
                            },
                            "time_max": {
                                "type": "string",
                                "description": "Upper bound for event start time in ISO format (optional)",
                            },
                        },
                    },
                ),
                Tool(
                    name="update_calendar_event",
                    description="Update an existing Google Calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "Event ID to update",
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                            },
                            "summary": {
                                "type": "string",
                                "description": "New event title (optional)",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "New start time in ISO format (optional)",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "New end time in ISO format (optional)",
                            },
                            "description": {
                                "type": "string",
                                "description": "New event description (optional)",
                            },
                            "location": {
                                "type": "string",
                                "description": "New event location (optional)",
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone (default: Europe/Brussels)",
                            },
                        },
                        "required": ["event_id"],
                    },
                ),
                Tool(
                    name="delete_calendar_event",
                    description="Delete a Google Calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "event_id": {
                                "type": "string",
                                "description": "Event ID to delete",
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                            },
                        },
                        "required": ["event_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "send_email":
                    result = self.service.send_email(
                        to=arguments["to"],
                        subject=arguments["subject"],
                        body=arguments["body"],
                        cc=arguments.get("cc"),
                        bcc=arguments.get("bcc"),
                        html=arguments.get("html", False),
                        from_email=arguments.get("from_email"),
                    )
                    
                elif name == "create_calendar_event":
                    result = self.service.create_calendar_event(
                        summary=arguments["summary"],
                        start_time=arguments["start_time"],
                        end_time=arguments["end_time"],
                        description=arguments.get("description"),
                        location=arguments.get("location"),
                        attendees=arguments.get("attendees"),
                        calendar_id=arguments.get("calendar_id"),
                        timezone=arguments.get("timezone", "Europe/Brussels"),
                    )
                    
                elif name == "list_calendar_events":
                    result = self.service.list_calendar_events(
                        max_results=arguments.get("max_results", 10),
                        calendar_id=arguments.get("calendar_id"),
                        time_min=arguments.get("time_min"),
                        time_max=arguments.get("time_max"),
                    )
                    
                elif name == "update_calendar_event":
                    result = self.service.update_calendar_event(
                        event_id=arguments["event_id"],
                        calendar_id=arguments.get("calendar_id"),
                        summary=arguments.get("summary"),
                        start_time=arguments.get("start_time"),
                        end_time=arguments.get("end_time"),
                        description=arguments.get("description"),
                        location=arguments.get("location"),
                        timezone=arguments.get("timezone", "Europe/Brussels"),
                    )
                    
                elif name == "delete_calendar_event":
                    result = self.service.delete_calendar_event(
                        event_id=arguments["event_id"],
                        calendar_id=arguments.get("calendar_id"),
                    )
                    
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main():
    """Main entry point for the MCP server."""
    server = NotificationMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
