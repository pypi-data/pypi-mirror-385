# Streamlit Supabase Auth

Simple and elegant Supabase OAuth authentication for Streamlit apps.

## Features

- 🚀 **Simple API** - Just 3 methods to handle complete OAuth flow
- 🔐 **Secure** - Uses Supabase's implicit OAuth flow with automatic token cleanup
- 🎨 **Streamlit Native** - Feels like native Streamlit components
- 🔄 **Session Persistence** - Maintains auth state across reruns
- 🌐 **Multi-Provider** - Supports Google, GitHub, GitLab, and more

## Installation

```bash
# Using pip
pip install streamlit-supabase-auth

# Using uv (recommended)
uv add streamlit-supabase-auth
```

## Quick Start

### 1. Configure Supabase

1. Go to your [Supabase Dashboard](https://app.supabase.com/)
2. Navigate to **Authentication → Providers**
3. Enable your OAuth provider (e.g., Google)
4. Configure redirect URLs:
   - Add `http://localhost:8501` for local development
   - Add your production URL for deployment

### 2. Configure Google OAuth (Example)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URI: `https://YOUR_PROJECT.supabase.co/auth/v1/callback`
4. Copy Client ID and Secret to Supabase

### 3. Use in Your Streamlit App

```python
import streamlit as st
from streamlit_supabase_auth import SupabaseAuth

# Initialize auth
auth = SupabaseAuth(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key",
    redirect_uri="http://localhost:8501"
)

# Check authentication status
if auth.is_authenticated():
    user = auth.get_user()
    st.write(f"Welcome {user.email}!")
    
    if st.button("Logout"):
        auth.logout()
else:
    st.write("Please login to continue")
    auth.login_button(provider="google")
```

## API Reference

### `SupabaseAuth`

Main authentication class.

#### `__init__(supabase_url, supabase_key, redirect_uri='http://localhost:8501')`

Initialize the authentication handler.

**Parameters:**
- `supabase_url` (str): Your Supabase project URL
- `supabase_key` (str): Your Supabase anonymous/public key
- `redirect_uri` (str): OAuth redirect URI (default: http://localhost:8501)

#### `is_authenticated() -> bool`

Check if user is currently authenticated.

**Returns:**
- `bool`: True if authenticated, False otherwise

#### `get_user() -> Optional[User]`

Get the currently authenticated user.

**Returns:**
- `User`: Supabase user object if authenticated, None otherwise

**User attributes:**
- `user.id`: User's unique ID
- `user.email`: User's email address
- `user.user_metadata`: Custom user metadata
- `user.app_metadata`: App metadata (includes provider info)

#### `login_button(provider='google', button_text=None, **button_kwargs)`

Render a login button that initiates OAuth flow.

**Parameters:**
- `provider` (str): OAuth provider ('google', 'github', 'gitlab', etc.)
- `button_text` (str, optional): Custom button text
- `**button_kwargs`: Additional arguments passed to `st.button()`

#### `logout()`

Log out the current user and clear session. Automatically calls `st.rerun()`.

## Advanced Usage

### Custom Button Styling

```python
auth.login_button(
    provider="google",
    button_text="🚀 Sign in with Google",
    use_container_width=True,
    type="primary"
)
```

### Access Supabase Client

The underlying Supabase client is available for database operations:

```python
if auth.is_authenticated():
    # Access Supabase client
    supabase = auth.client
    
    # Query your database
    response = supabase.table('todos').select('*').execute()
    st.write(response.data)
```

### Environment Variables

Use environment variables for configuration:

```python
import os
from streamlit_supabase_auth import SupabaseAuth

auth = SupabaseAuth(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY"),
    redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:8501")
)
```

### Email Whitelisting

Restrict access to specific email addresses:

```python
ALLOWED_EMAILS = ["user1@example.com", "user2@example.com"]

if auth.is_authenticated():
    user = auth.get_user()
    
    if user.email not in ALLOWED_EMAILS:
        st.error("Access denied. Contact admin for access.")
        auth.logout()
    else:
        st.success(f"Welcome {user.email}!")
```

## Deployment

### Streamlit Cloud

1. Add secrets in Streamlit Cloud dashboard:
   ```toml
   # .streamlit/secrets.toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   REDIRECT_URI = "https://your-app.streamlit.app"
   ```

2. Update your app:
   ```python
   auth = SupabaseAuth(
       supabase_url=st.secrets["SUPABASE_URL"],
       supabase_key=st.secrets["SUPABASE_KEY"],
       redirect_uri=st.secrets["REDIRECT_URI"]
   )
   ```

3. Update Supabase redirect URLs with your Streamlit Cloud URL

### Docker

Update `redirect_uri` to match your Docker container's exposed URL.

## How It Works

This library uses Supabase's **implicit OAuth flow**:

1. User clicks login button
2. Redirects to OAuth provider (e.g., Google)
3. User authenticates
4. Provider redirects back with tokens in URL fragment (`#access_token=...`)
5. Library extracts tokens, authenticates with Supabase
6. Tokens stored in Streamlit session state
7. URL fragment cleared for security

## Supported Providers

Any OAuth provider supported by Supabase:

- Google
- GitHub
- GitLab
- Bitbucket
- Azure
- Facebook
- Discord
- Twitch
- And more...

Configure providers in your Supabase dashboard under **Authentication → Providers**.

## Troubleshooting

### "Failed to initiate login"

- Check your Supabase URL and key
- Verify the OAuth provider is enabled in Supabase dashboard
- Check redirect URI configuration

### "Authentication failed"

- Verify redirect URI matches exactly (including protocol and port)
- Check browser console for errors
- Ensure Supabase project is not paused

### Tokens not persisting

- Check if cookies are enabled
- Verify session state is not being cleared elsewhere

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/)
- [Supabase](https://supabase.com/)
- [streamlit-url-fragments](https://github.com/iamvikthur/streamlit-url-fragments)

