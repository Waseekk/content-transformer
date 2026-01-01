# Password Protection Setup Guide

## Overview
The app now includes password protection to prevent unauthorized access and protect your OpenAI API credits.

## Default Password (Local Development)
- **Password**: `demo2024`
- This is hardcoded as a fallback for local testing

## Setting Custom Password on Streamlit Cloud

### Step 1: Deploy Your App
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select branch: `streamlit-cloud`
4. Click "Deploy"

### Step 2: Configure Secrets
1. In your deployed app dashboard, click **Settings** (⚙️)
2. Click **Secrets** in the left menu
3. Add the following content:

```toml
# App Password Protection
APP_PASSWORD = "YourSecurePassword123"

# OpenAI API Key
OPENAI_API_KEY = "sk-your-actual-openai-key"
```

4. Click **Save**
5. App will automatically restart with new password

### Step 3: Share Password with Client
- Send the password to your client via secure channel (email, WhatsApp, etc.)
- Don't share it publicly
- Change password anytime by updating Secrets

## How It Works

### Login Screen
- Users see a clean login screen when they first visit
- They must enter the correct password to access the app
- Failed login attempts are logged

### Session Management
- Once logged in, users stay authenticated for the entire session
- Session ends when:
  - User clicks "Logout" button
  - User closes browser tab
  - Session expires (Streamlit default timeout)

### Security Features
- ✅ Password is stored in environment variable (not in code)
- ✅ Password input field is masked (`type="password"`)
- ✅ Failed login attempts are logged
- ✅ Successful logins are logged
- ✅ Logout button in sidebar

## Changing Password

### On Streamlit Cloud:
1. Go to app Settings → Secrets
2. Change `APP_PASSWORD = "new-password"`
3. Save (app auto-restarts)

### For Local Development:
1. Set environment variable:
   ```bash
   # Windows
   set APP_PASSWORD=mynewpassword

   # Mac/Linux
   export APP_PASSWORD=mynewpassword
   ```

2. Or edit the default in `app.py` line 54:
   ```python
   APP_PASSWORD = os.getenv('APP_PASSWORD', 'your-new-default')
   ```

## Best Practices

1. **Use Strong Password**:
   - At least 12 characters
   - Mix of letters, numbers, symbols
   - Example: `TravelNews@2024!`

2. **Don't Commit Secrets**:
   - Never commit `.streamlit/secrets.toml` to git
   - File is already in `.gitignore`
   - Only use example file for reference

3. **Monitor Usage**:
   - Check OpenAI usage dashboard regularly
   - Set usage limits in OpenAI account
   - Review app logs for suspicious activity

4. **Share Securely**:
   - Send password via encrypted channel
   - Don't post password publicly
   - Change password if compromised

## Troubleshooting

### "Incorrect password" error
- Double-check password (case-sensitive)
- Verify Secrets are saved in Streamlit Cloud
- Check for extra spaces in password

### App won't start after adding secrets
- Verify TOML syntax is correct
- Check for missing quotes
- Ensure `OPENAI_API_KEY` is valid

### Password not working after change
- App takes 1-2 minutes to restart after secret change
- Clear browser cache
- Try in incognito/private window

## Future Enhancements

For production use, consider upgrading to:
- User accounts with email/password
- JWT token authentication
- Per-user API key management
- Usage limits per user
- Admin dashboard

See `CLAUDE.md` for full multi-user SaaS implementation plan.
