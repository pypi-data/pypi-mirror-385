# Streamlit Supabase Auth Flow

Other streamlit supabase auth packages build a custom log in form in react and pass back to the streamlit app information about the user. This package uses the the IdP's implicit flow to authenticate the user, get's the token from the URL with a simple html component, and returns a user object. The client can be used to make database queries impersonating the user.

I used LLM's to create this, and although I made all the techinal decisions and used the LLM to speed things up, I might have missed something. Please raise an issue.

## Installation

```bash
pip install streamlit-supabase-auth-flow
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
from streamlit_supabase_auth_flow import SupabaseAuth

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
