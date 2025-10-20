"""
Streamlit Supabase Authentication module.

Provides a simple interface for Supabase OAuth authentication in Streamlit
apps.
"""

from pathlib import Path

import streamlit as st
from streamlit.components.v1 import components
from streamlit_url_fragments import get_fragments  # type: ignore
from supabase import Client
from supabase.lib.client_options import SyncClientOptions
from supabase_auth import User

# Declare the clear_fragment component
_FRONTEND_DIR = Path(__file__).parent.parent /'public'
_clear_fragment_component = components.declare_component(
    "clear_fragment", path=str(_FRONTEND_DIR)
)


def _clear_url_fragment() -> None:
    """Clear the URL fragment using a custom component."""
    _clear_fragment_component()


class SupabaseAuth:
    """
    Streamlit Supabase Authentication handler.

    This class manages OAuth authentication with Supabase using the implicit flow,
    which works seamlessly with Streamlit's rerun mechanism.

    Example:
        ```python
        import streamlit as st
        from streamlit_supabase_auth import SupabaseAuth

        auth = SupabaseAuth(
            supabase_url="https://your-project.supabase.co",
            supabase_key="your-anon-key",
            redirect_uri="http://localhost:8501"
        )

        if auth.is_authenticated():
            user = auth.get_user()
            st.write(f"Welcome {user.email}!")
            auth.client.table("users").select("*").execute()

            if st.button("Logout"):
                auth.logout()
        else:
            auth.login_button(provider="google")
        ```
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        redirect_uri: str = "http://localhost:8501",
    ):
        """
        Initialize the Supabase authentication handler.

        Args:
            supabase_url: Your Supabase project URL
            supabase_key: Your Supabase anonymous/public key
            redirect_uri: The URI to redirect to after OAuth (default: localhost:8501)
        """
        self.redirect_uri = redirect_uri

        # Initialize Supabase client with implicit flow (stored in session state)
        if "supabase_auth_client" not in st.session_state:
            options = SyncClientOptions(flow_type="implicit")
            st.session_state.supabase_auth_client = Client(
                supabase_url, supabase_key, options=options
            )

        self.client: Client = st.session_state.supabase_auth_client

        # Handle OAuth callback on page load
        self._handle_oauth_callback()

    def _handle_oauth_callback(self) -> None:
        """Process OAuth callback tokens from URL fragment."""
        fragments: dict[str, str] = get_fragments()

        # Only process if we have tokens and haven't processed them yet
        if (
            fragments
            and "access_token" in fragments
            and not st.session_state.get("supabase_auth_tokens_processed")
        ):
            access_token = fragments.get("access_token")
            refresh_token = fragments.get("refresh_token")

            if access_token and refresh_token:
                try:
                    # Set Supabase session
                    self.client.auth.set_session(access_token, refresh_token)

                    # Store in session state
                    st.session_state.supabase_auth_authenticated = True
                    st.session_state.supabase_auth_access_token = access_token
                    st.session_state.supabase_auth_refresh_token = refresh_token
                    st.session_state.supabase_auth_tokens_processed = True

                    # Clear URL fragment for security
                    _clear_url_fragment()

                    # Rerun to show authenticated state
                    st.rerun()

                except Exception as e:
                    st.error(f"Authentication failed: {e}")

    def _restore_session(self) -> None:
        """Restore Supabase session from session state if available."""
        if st.session_state.get("supabase_auth_authenticated"):
            access_token = st.session_state.get("supabase_auth_access_token")
            refresh_token = st.session_state.get("supabase_auth_refresh_token")

            if access_token and refresh_token:
                try:
                    self.client.auth.set_session(access_token, refresh_token)
                except Exception:
                    # Session expired, clear state
                    st.session_state.supabase_auth_authenticated = False

    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        self._restore_session()

        try:
            user = self.client.auth.get_user()
            return user is not None
        except Exception:
            return False

    def get_user(self) -> User | None:
        """
        Get the currently authenticated user.

        Returns:
            User object if authenticated, None otherwise
        """
        if not self.is_authenticated():
            return None

        try:
            response = self.client.auth.get_user()
            return response.user if response else None
        except Exception:
            return None

    def login_button(
        self,
        provider: str = "google",
        button_text: str | None = None,
        **button_kwargs,
    ) -> None:
        """
        Render a login button that initiates OAuth flow.

        Args:
            provider: OAuth provider (e.g., 'google', 'github', 'gitlab')
            button_text: Custom button text (default: "Login with {Provider}")
            **button_kwargs: Additional kwargs passed to st.button()
        """
        if button_text is None:
            button_text = f"Login with {provider.capitalize()}"

        # Set default button type to primary if not specified
        if "type" not in button_kwargs:
            button_kwargs["type"] = "primary"

        if st.button(button_text, **button_kwargs):
            try:
                response = self.client.auth.sign_in_with_oauth(
                    {
                        "provider": provider,  # type: ignore
                        "options": {  # type: ignore
                            "redirect_to": self.redirect_uri,
                            "skip_browser_redirect": True,
                        },
                    }
                )

                oauth_url = response.url

                # Redirect to OAuth provider
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; ' f'url={oauth_url}">',
                    unsafe_allow_html=True,
                )
                redirect_text = (
                    f"Redirecting to {provider.capitalize()}... "
                    f"[Click here if not redirected]({oauth_url})"
                )
                st.info(redirect_text)

            except Exception as e:
                st.error(f"Failed to initiate login: {e}")

    def logout(self) -> None:
        """
        Log out the current user and clear session state.
        Call st.rerun() after this to update the UI.
        """
        try:
            self.client.auth.sign_out()
        except Exception:
            pass  # Ignore errors on logout

        # Clear all auth-related session state
        keys_to_clear = [
            "supabase_auth_authenticated",
            "supabase_auth_access_token",
            "supabase_auth_refresh_token",
            "supabase_auth_tokens_processed",
        ]
        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.rerun()
