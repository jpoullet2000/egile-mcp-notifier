# Microsoft To-Do Quick Reference

Quick reference guide for using Microsoft To-Do features in egile-agent-notifier and egile-mcp-notifier.

## Natural Language Examples (for egile-agent-notifier)

The agent can understand natural language commands for managing your to-do tasks:

### Creating Tasks

```bash
"Add a task to review the quarterly report"
"Create a high-priority to-do to call the client by Friday"
"Add a reminder to submit the timesheet tomorrow at 9 AM"
"Create a task with deadline January 30th to prepare the presentation"
```

### Viewing Tasks

```bash
"Show me my to-do list"
"What tasks do I have?"
"List all my pending tasks"
"Show me only high-priority tasks"
"What tasks are not started?"
```

### Updating Tasks

```bash
"Mark the quarterly report task as in progress"
"Complete the task about calling the client"
"Change the priority of the presentation task to high"
"Update the deadline for the timesheet task to next Monday"
```

### Deleting Tasks

```bash
"Delete the task about the presentation"
"Remove the completed tasks"
```

### Managing Lists

```bash
"Show me all my to-do lists"
"What lists do I have?"
```

## Programmatic Usage (MCP Server)

### Create a Task

```python
{
    "name": "create_todo",
    "arguments": {
        "title": "Review project documentation",
        "body": "Check all examples and update API references",
        "due_date": "2026-01-25",
        "importance": "high",
        "reminder_date": "2026-01-24T09:00:00"
    }
}
```

### List Tasks

```python
{
    "name": "list_todos",
    "arguments": {
        "filter_status": "notStarted",
        "max_results": 20
    }
}
```

### Update Task

```python
{
    "name": "update_todo",
    "arguments": {
        "task_id": "task-id-123",
        "status": "completed",
        "importance": "normal"
    }
}
```

### Delete Task

```python
{
    "name": "delete_todo",
    "arguments": {
        "task_id": "task-id-123"
    }
}
```

### List All To-Do Lists

```python
{
    "name": "list_todo_lists",
    "arguments": {}
}
```

## Task Properties

### Status Values
- `notStarted` - Task not yet started (default)
- `inProgress` - Task is in progress
- `completed` - Task is completed

### Importance Values
- `low` - Low priority
- `normal` - Normal priority (default)
- `high` - High priority

### Date Format

All dates should be in ISO 8601 format:
- Date only: `2026-01-25`
- Date and time: `2026-01-25T14:30:00`
- With timezone: `2026-01-25T14:30:00Z`

## Integration with Other Features

You can combine To-Do tasks with emails and calendar events:

```bash
# Create event and task
"Schedule a client meeting for next Tuesday at 2 PM and add a task to prepare the agenda"

# Send email and create task
"Send a meeting summary email to the team and add a task to follow up next week"

# Create task with calendar reference
"Add a task to review meeting notes from today's team sync"
```

## Tips

1. **Default List**: If you don't specify a list ID, the system uses your default to-do list
2. **Reminders**: Set reminder dates to get notifications before due dates
3. **Filtering**: Use `filter_status` to view only specific types of tasks
4. **Batch Operations**: You can create multiple tasks in one conversation
5. **Task Updates**: You can update any combination of fields in a single update call

## Common Workflows

### Daily Planning
```bash
"Show me my tasks for today"
"Create a task to review emails, priority high"
"Add a task to prepare for tomorrow's presentation"
```

### Project Management
```bash
"Create tasks for the new project: design, development, and testing"
"Mark design task as completed"
"Show me all in-progress tasks"
```

### Follow-ups
```bash
"Add a task to follow up with the client in 2 days"
"Create a reminder to check on the proposal status next week"
```

## Troubleshooting

**Task not appearing**: Wait a few seconds and list tasks again - there may be a sync delay

**Can't find a task**: Use `list_todos` without filters to see all tasks

**Authentication error**: Delete `ms_token_cache.json` and authenticate again

**Wrong list**: Specify the `list_id` parameter explicitly

For detailed setup instructions, see [MS_TODO_SETUP.md](MS_TODO_SETUP.md)
