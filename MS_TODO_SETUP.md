# Microsoft To-Do Setup Guide

This guide will help you set up Microsoft To-Do integration for the Egile Notifier.

## Prerequisites

- A Microsoft account (personal or organizational)
- Access to Azure Portal (free tier is sufficient)

## Step-by-Step Setup

### 1. Create an Azure App Registration

**For Personal Microsoft Accounts (recommended for most users):**

1. Go directly to [Azure App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Sign in with your Microsoft account
3. If prompted to select a directory, choose **Personal Microsoft Account** or your email address
4. Click **New registration**

**For Organizational Accounts:**

1. Go to [Azure Portal](https://portal.azure.com/)
2. Sign in with your organizational Microsoft account
3. Navigate to **Azure Active Directory** (or **Microsoft Entra ID**)
4. Click on **App registrations** in the left menu
5. Click **New registration**

**Important**: If you get an error about the account not existing in a tenant, you're using a personal account but being directed to an organizational tenant. Use the direct link above or sign out and try again.

### 2. Configure Your App

Fill in the registration form:

- **Name**: `Egile Notifier` (or any name you prefer)
- **Supported account types**: Select one of the following:
  - `Accounts in any organizational directory and personal Microsoft accounts` (Recommended for personal use)
  - `Accounts in this organizational directory only` (For organization-only use)
- **Redirect URI**: Leave blank (we'll use device code flow)
- Click **Register**

### 3. Copy Application (Client) ID

After registration:

1. You'll be taken to the app's overview page
2. Copy the **Application (client) ID** (it looks like: `12345678-1234-1234-1234-123456789abc`)
3. This is your `MS_TODO_CLIENT_ID` - save it for later

### 4. (Optional) Copy Directory (Tenant) ID

If you're using organizational accounts:

1. On the same overview page, copy the **Directory (tenant) ID**
2. This is your `MS_TODO_TENANT_ID`
3. For personal Microsoft accounts, you can use `common` (default)

### 5. Configure API Permissions

1. Click on **API permissions** in the left menu
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Search for and add the following permissions:
   - `Tasks.ReadWrite` - Read and write user tasks
   - `offline_access` - Maintain access to data you have given it access to
6. Click **Add permissions**

**Note**: Admin consent is NOT required for these delegated permissions when using personal accounts.

### 6. Configure Your Environment

Add the following to your `.env` file:

```env
# Microsoft To-Do Configuration
MS_TODO_CLIENT_ID=your-application-client-id-here
MS_TODO_TENANT_ID=common
MS_TODO_TOKEN_FILE=ms_token_cache.json
```

Replace `your-application-client-id-here` with the Application (client) ID you copied in step 3.

For organizational accounts, replace `common` with your Directory (tenant) ID from step 4.

### 7. First Run Authentication

When you run the application for the first time:

1. The application will display a message like:
   ```
   To sign in, use a web browser to open the page https://microsoft.com/devicelogin
   and enter the code ABC123DEF to authenticate.
   ```

2. Open a web browser and go to https://microsoft.com/devicelogin
3. Enter the code displayed in your terminal
4. Sign in with your Microsoft account
5. Grant the requested permissions to the app
6. Return to your terminal - the authentication should complete automatically

The authentication token will be cached in `ms_token_cache.json` and will be automatically refreshed, so you won't need to authenticate again unless you revoke the permissions.

## Troubleshooting

### "Account does not exist in tenant" error

This happens when using a personal Microsoft account with the wrong Azure Portal URL.

**Solution**: Use the direct app registration link: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

Or:
1. Clear your browser cache/cookies
2. Sign out of all Microsoft accounts
3. Use an incognito/private browser window
4. Go directly to the app registration URL above
5. Sign in with your personal Microsoft account

### "No To-Do lists found"

Make sure you have at least one To-Do list in your Microsoft To-Do account. You can create one at https://to-do.microsoft.com/

### "Failed to acquire token"

- Make sure you entered the device code correctly
- Check that you granted all required permissions
- Verify your `MS_TODO_CLIENT_ID` is correct
- Try deleting `ms_token_cache.json` and authenticating again

### "Unauthorized" errors

- Verify that you added both required permissions (`Tasks.ReadWrite` and `offline_access`)
- Check that you're using the correct Microsoft account
- Delete `ms_token_cache.json` and authenticate again

### Using with organizational accounts

If you're using an organizational Microsoft 365 account:

1. Your organization may require admin consent for the app
2. Contact your IT administrator if you get permission errors
3. Use your Directory (tenant) ID instead of `common` in the `MS_TODO_TENANT_ID` setting

## Testing Your Setup

Run the example script to test your configuration:

```bash
python example_todo.py
```

This will:
- List your To-Do lists
- Create a sample task
- List tasks
- Update task status
- Mark task as completed

## Security Notes

- The `ms_token_cache.json` file contains your authentication tokens - keep it secure
- Add `ms_token_cache.json` to your `.gitignore` file
- Never commit your `.env` file or client ID to version control
- The application uses device code flow, which is secure for public clients
- Tokens are automatically refreshed and don't require re-authentication

## Resources

- [Microsoft Graph To-Do API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/todo-overview)
- [Azure App Registration Documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Device Code Flow Documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code)
