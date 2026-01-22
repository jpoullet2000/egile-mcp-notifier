"""Example script demonstrating Microsoft To-Do functionality."""

import os
from dotenv import load_dotenv
from egile_mcp_notifier.notification_service import NotificationService

# Load environment variables
load_dotenv()

def main():
    """Run Microsoft To-Do examples."""
    service = NotificationService()
    
    print("=== Microsoft To-Do Examples ===\n")
    
    # Example 1: List all to-do lists
    print("1. Listing all To-Do lists...")
    result = service.list_todo_lists()
    if result["success"]:
        print(f"   Found {result['count']} lists:")
        for todo_list in result["lists"]:
            print(f"   - {todo_list['name']} (ID: {todo_list['id']})")
    else:
        print(f"   Error: {result['error']}")
    print()
    
    # Example 2: Create a new task
    print("2. Creating a new task...")
    result = service.create_todo(
        title="Review project documentation",
        body="Check all examples and update API references",
        due_date="2026-01-25",
        importance="high"
    )
    if result["success"]:
        print(f"   ✓ Task created: {result['title']}")
        print(f"     Task ID: {result['task_id']}")
        print(f"     Importance: {result['importance']}")
        task_id = result['task_id']
    else:
        print(f"   Error: {result['error']}")
        return
    print()
    
    # Example 3: List tasks
    print("3. Listing tasks...")
    result = service.list_todos(max_results=10)
    if result["success"]:
        print(f"   Found {result['count']} tasks:")
        for task in result["tasks"]:
            status = task.get('status', 'unknown')
            importance = task.get('importance', 'normal')
            print(f"   - [{status}] {task['title']} (Priority: {importance})")
    else:
        print(f"   Error: {result['error']}")
    print()
    
    # Example 4: Update the task
    print("4. Updating task status...")
    result = service.update_todo(
        task_id=task_id,
        status="inProgress"
    )
    if result["success"]:
        print(f"   ✓ Task updated: {result['title']}")
        print(f"     New status: {result['status']}")
    else:
        print(f"   Error: {result['error']}")
    print()
    
    # Example 5: Create a task with reminder
    print("5. Creating a task with reminder...")
    result = service.create_todo(
        title="Prepare presentation for client meeting",
        body="Include Q4 results and roadmap",
        due_date="2026-01-23",
        importance="high",
        reminder_date="2026-01-22T09:00:00"
    )
    if result["success"]:
        print(f"   ✓ Task created with reminder: {result['title']}")
        print(f"     Task ID: {result['task_id']}")
    else:
        print(f"   Error: {result['error']}")
    print()
    
    # Example 6: Filter tasks by status
    print("6. Listing only not started tasks...")
    result = service.list_todos(filter_status="notStarted")
    if result["success"]:
        print(f"   Found {result['count']} not started tasks:")
        for task in result["tasks"]:
            print(f"   - {task['title']}")
    else:
        print(f"   Error: {result['error']}")
    print()
    
    # Example 7: Complete a task
    print("7. Marking task as completed...")
    result = service.update_todo(
        task_id=task_id,
        status="completed"
    )
    if result["success"]:
        print(f"   ✓ Task completed: {result['title']}")
    else:
        print(f"   Error: {result['error']}")
    print()
    
    # Example 8: Delete a task (optional - uncomment to delete)
    # print("8. Deleting task...")
    # result = service.delete_todo(task_id=task_id)
    # if result["success"]:
    #     print(f"   ✓ Task deleted: {result['task_id']}")
    # else:
    #     print(f"   Error: {result['error']}")
    # print()
    
    print("=== Examples completed ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have configured MS_TODO_CLIENT_ID in your .env file.")
        print("See README.md for setup instructions.")
