"""Egile MCP Notifier - Email and Calendar Notification Server."""

from .notification_service import NotificationService
from .server import NotificationMCPServer, main

__version__ = "0.1.0"
__all__ = ["NotificationService", "NotificationMCPServer", "main"]
