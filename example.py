"""Example usage of the Notifier MCP server."""

import asyncio
from dotenv import load_dotenv

from egile_mcp_notifier import NotificationService


async def main():
    """Demonstrate notification capabilities."""
    # Load environment variables
    load_dotenv()
    
    service = NotificationService()
    
    print("=== Egile Notifier Service Demo ===\n")
    
    # Example 1: Send a simple email
    print("1. Sending a test email...")
    email_result = service.send_email(
        to="recipient@example.com",
        subject="Test Email from Egile Notifier",
        body="This is a test email sent via the Egile Notifier service.",
    )
    print(f"Result: {email_result}\n")
    
    # Example 2: Send HTML email with CC
    print("2. Sending HTML email with CC...")
    html_email = service.send_email(
        to=["primary@example.com"],
        cc=["cc@example.com"],
        subject="Meeting Summary",
        body="""
        <html>
            <body>
                <h1>Meeting Summary</h1>
                <p>Here are the key points from today's meeting:</p>
                <ul>
                    <li>Project timeline updated</li>
                    <li>Budget approved</li>
                    <li>Next meeting scheduled</li>
                </ul>
            </body>
        </html>
        """,
        html=True,
    )
    print(f"Result: {html_email}\n")
    
    # Example 3: Create a calendar event
    print("3. Creating a calendar event...")
    event_result = service.create_calendar_event(
        summary="Team Meeting",
        start_time="2026-01-20T14:00:00",
        end_time="2026-01-20T15:00:00",
        description="Discuss project updates and timeline",
        location="Conference Room A",
        attendees=["team@example.com"],
    )
    print(f"Result: {event_result}\n")
    
    # Example 4: List upcoming events
    print("4. Listing upcoming calendar events...")
    events_result = service.list_calendar_events(max_results=5)
    print(f"Found {events_result.get('count', 0)} events:")
    for event in events_result.get('events', []):
        print(f"  - {event['summary']} at {event['start']}")
    print()
    
    # Example 5: Update a calendar event (if one was created)
    if event_result.get('success') and event_result.get('event_id'):
        print("5. Updating the created event...")
        update_result = service.update_calendar_event(
            event_id=event_result['event_id'],
            summary="Team Meeting - Updated",
            location="Conference Room B",
        )
        print(f"Result: {update_result}\n")
    
    # Example 6: Delete a calendar event (if one was created)
    # Uncomment to test deletion
    # if event_result.get('success') and event_result.get('event_id'):
    #     print("6. Deleting the created event...")
    #     delete_result = service.delete_calendar_event(
    #         event_id=event_result['event_id']
    #     )
    #     print(f"Result: {delete_result}\n")


if __name__ == "__main__":
    asyncio.run(main())
