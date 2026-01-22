# Installing Microsoft To-Do Support

Quick installation guide for the Microsoft To-Do functionality added to egile-agent-notifier.

## Step 1: Install/Update the Packages

### For MCP Server (egile-mcp-notifier)

```bash
cd egile-mcp-notifier
pip install -e .
```

This will install the new `msal` dependency needed for Microsoft authentication.

### For Agent (egile-agent-notifier)

```bash
cd egile-agent-notifier
pip install -e .
```

This will pick up the updated egile-mcp-notifier package.

## Step 2: Set Up Azure App Registration

You need to create an Azure app to get a client ID. Follow the detailed guide in [MS_TODO_SETUP.md](MS_TODO_SETUP.md).

Quick steps:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory > App registrations
3. Create a new registration
4. Copy the Application (client) ID
5. Add API permissions: `Tasks.ReadWrite` and `offline_access`

## Step 3: Configure Environment

Add to your `.env` file:

```env
# Microsoft To-Do Configuration
MS_TODO_CLIENT_ID=paste-your-client-id-here
MS_TODO_TENANT_ID=common
MS_TODO_TOKEN_FILE=ms_token_cache.json
```

Replace `paste-your-client-id-here` with the Application (client) ID from Azure.

## Step 4: Test the Setup

Run the example script:

```bash
cd egile-mcp-notifier
python example_todo.py
```

On first run:
1. You'll see a message with a device code
2. Open https://microsoft.com/devicelogin in your browser
3. Enter the code shown
4. Sign in with your Microsoft account
5. Grant permissions

After authentication, the example will:
- List your To-Do lists
- Create sample tasks
- Update tasks
- Mark tasks as completed

## Step 5: Use with Agent

Once configured, you can use natural language commands:

```bash
# Standalone
notifier

# Then chat:
> Add a task to review the project documentation
> Show me my to-do list
> Mark the review task as completed

# Via Agent Hub
agent-hub notifier "Create a high-priority task to prepare the presentation by Friday"
```

## Verification

To verify everything is working:

1. **Check dependencies**:
   ```bash
   pip list | grep msal
   ```
   Should show: `msal` version 1.26.0 or higher

2. **Check authentication**:
   After first run, you should have a file: `ms_token_cache.json`

3. **Test MCP tools**:
   Run `example_todo.py` - it should complete without errors

## Troubleshooting

### "No module named 'msal'"

Reinstall the package:
```bash
cd egile-mcp-notifier
pip install -e . --force-reinstall
```

### "MS_TODO_CLIENT_ID not configured"

Make sure:
- Your `.env` file contains `MS_TODO_CLIENT_ID=...`
- The `.env` file is in the correct directory (where you run the command)
- You're using the correct client ID from Azure

### Authentication fails

1. Delete `ms_token_cache.json`
2. Run the application again
3. Follow the device code flow carefully
4. Make sure you granted all required permissions in Azure

### "No To-Do lists found"

1. Go to https://to-do.microsoft.com/
2. Create at least one to-do list
3. Try again

## Security Notes

- Never commit `.env` file to git
- Never commit `ms_token_cache.json` to git
- The `.gitignore` files have been updated to exclude these files
- Keep your Azure client ID private

## What's New

The following features are now available:

### MCP Tools (for developers)
- `create_todo` - Create tasks
- `list_todos` - List tasks with filters
- `update_todo` - Update task properties
- `delete_todo` - Delete tasks
- `list_todo_lists` - List all To-Do lists

### Natural Language (for users via agent)
- "Add a task..."
- "Show me my tasks"
- "Mark task as completed"
- "Create a high-priority reminder..."

### Task Features
- Due dates
- Reminders
- Priority levels (low, normal, high)
- Status tracking (notStarted, inProgress, completed)
- Task notes/descriptions
- Multiple list support

## Next Steps

1. Read [MS_TODO_QUICKREF.md](MS_TODO_QUICKREF.md) for usage examples
2. Review [MS_TODO_IMPLEMENTATION.md](MS_TODO_IMPLEMENTATION.md) for technical details
3. Experiment with natural language commands
4. Integrate with your workflow

## Support

For issues or questions:
1. Check [MS_TODO_SETUP.md](MS_TODO_SETUP.md) for detailed setup instructions
2. Review the troubleshooting section above
3. Check Microsoft Graph API documentation: https://learn.microsoft.com/en-us/graph/api/resources/todo-overview
