# envbanner/streamlit_adapter.py
import os
from html import escape
from typing import Dict, Any
from .core import classify_env, banner_palette, banner_label, is_prod

def streamlit(env_var_name: str = "APP_ENV", **options):
    """
    Renders a Streamlit-safe banner using st.markdown (HTML+CSS only).
    Place this call near the top of your Streamlit script.

    Args:
        env_var_name: Primary environment variable to check (default: "APP_ENV")
        **options: Additional banner options:
            - text: Custom banner text
            - background: Custom background color (hex)
            - color: Custom text color (hex)
            - position: Banner position ('top' or 'bottom' - default: 'bottom')
            - show_host: Whether to show hostname (default: True, though host is not available in Streamlit)
            - opacity: Banner opacity 0.0-1.0

    Note: Due to Streamlit's architecture, only 'top' and 'bottom' positions are supported.
          Diagonal and corner positions are not available for Streamlit.
    """
    try:
        import streamlit as st
    except ImportError:
        print("Warning: Streamlit is not installed. Banner will not be shown.")
        return

    # Streamlit can't easily access the browser URL from the server,
    # so we rely primarily on the environment variable.
    env_var = os.getenv(env_var_name) or os.getenv("ENVBANNER_ENV")
    env = classify_env(env_var=env_var, host=None, path=None)

    if is_prod(env):
        return

    # Determine text and colors: use custom options first, then fall back to defaults
    default_bg, default_fg = banner_palette(env)
    bg = options.get("background", default_bg)
    fg = options.get("color", default_fg)
    label = options.get("text", banner_label(env))
    position = options.get("position", "bottom")
    opacity = options.get("opacity", 1.0)

    # Streamlit doesn't have easy host access, so we omit the hostname
    text = escape(label)

    # Determine position styling
    if position == "top":
        pos_style = "top: 0;"
        padding_style = ".main .block-container { padding-top: 5rem; }"
    else:  # bottom (default)
        pos_style = "bottom: 0;"
        padding_style = ".main .block-container { padding-bottom: 5rem; }"

    # Note: Streamlit injects its own CSS which can be complex.
    # Using `position: fixed` is more reliable than `sticky` here.
    st.markdown(
        f"""
<div style="
  position: fixed;
  {pos_style}
  left: 0;
  right: 0;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  background: {bg};
  color: {fg};
  opacity: {opacity};
  z-index: 999999;
  border-bottom: 1px solid rgba(0,0,0,.2);
">
  {text}
</div>
<style>
  /* Push down/up the main Streamlit content area */
  {padding_style}
</style>
""",
        unsafe_allow_html=True,
    )
