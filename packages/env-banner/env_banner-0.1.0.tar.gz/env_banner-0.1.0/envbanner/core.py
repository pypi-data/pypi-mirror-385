# envbanner/core.py
import os
import re
from html import escape
from typing import Optional, Tuple, Dict, Any

# Map host/path to env buckets; override with ENVBANNER_MAP if needed.
DEFAULT_RULES = [
    # dev/local/test
    (r"(localhost|127\.0\.0\.1|\.local$)", "dev"),
    (r"(^|\.)dev(\.|-)|(\b)dev(\b)", "dev"),
    (r"(^|\.)test(\.|-)|(\b)qa(\b)|(\b)sandbox(\b)", "dev"),
    (r":\d{2,5}$", "dev"),  # non-standard port is a strong hint

    # staging/validation
    (r"(^|\.)stg(\.|-)|(^|\.)stage(\.|-)|(^|\.)staging(\.)", "staging"),
    (r"(^|\.)val(\.|-)|(\b)validation(\b)|(\b)preprod(\b)", "staging"),
]

ENV_NORMS = {
    "prod": "prod", "production": "prod",
    "staging": "staging", "stage": "staging", "stg": "staging",
    "val": "staging", "validation": "staging", "preprod": "staging",
    "dev": "dev", "development": "dev",
    "local": "dev",
    "test": "dev", "qa": "dev",
    "unknown": "unknown", "auto": "auto",
}

def _norm_env(value: Optional[str]) -> Optional[str]:
    if not value: return None
    v = value.strip().lower()
    return ENV_NORMS.get(v, v)

def classify_from_host_path(host: str, path: str) -> str:
    text = f"{host}{path}".lower()
    for pattern, env in DEFAULT_RULES:
        if re.search(pattern, text):
            return env
    return "unknown"

def classify_env(*, env_var: Optional[str], host: Optional[str], path: Optional[str]) -> str:
    # 1) Explicit env var wins if provided
    e = _norm_env(env_var)
    if e and e != "auto":
        return e

    # 2) Host/path detection when available
    if host:
        detected = classify_from_host_path(host, path or "")
        if detected != "unknown":
            return detected
        return "dev" # unknown from host: prefer safety unless explicitly prod

    # 3) Last resort
    return "dev"  # safe default

def is_prod(env: str) -> bool:
    return env == "prod"

def banner_palette(env: str) -> Tuple[str, str]:
    """Returns (bg, fg) hex colors by env bucket."""
    if env == "staging":
        return ("#f59e0b", "#111827")  # amber-500 bg, gray-900 text
    # dev/test/local/unknown -> red
    return ("#ef4444", "#ffffff")     # red-500 bg, white text

def banner_label(env: str) -> str:
    if env == "prod": return ""
    if env == "staging": return "STAGING"
    if env in ("dev", "test", "local"): return env.upper()
    if env == "unknown": return "NON-PROD (UNKNOWN)"
    return env.upper()

def build_banner_html(options: Dict[str, Any]) -> str:
    """
    Generates the complete HTML and CSS for the banner based on options.

    Args:
        options: Dictionary with the following keys:
            - env: str (required) - The detected environment
            - host: Optional[str] - The hostname/port to display
            - text: Optional[str] - Custom banner text
            - background: Optional[str] - Custom background color (hex)
            - color: Optional[str] - Custom text color (hex)
            - position: Optional[str] - Banner position ('top', 'bottom', 'top-left',
                                       'top-right', 'bottom-left', 'bottom-right',
                                       'diagonal', 'diagonal-tlbr', 'diagonal-bltr')
            - show_host: Optional[bool] - Whether to show hostname (default: True)
            - opacity: Optional[float] - Banner opacity 0.0-1.0 (default: 1.0 for most, 0.5 for diagonal)

    Returns:
        HTML string to be injected
    """
    env = options.get("env", "dev")
    host = options.get("host")

    if is_prod(env):
        return ""

    # Determine text and colors: use custom options first, then fall back to defaults
    default_bg, default_fg = banner_palette(env)
    background = options.get("background", default_bg)
    color = options.get("color", default_fg)
    label = options.get("text", banner_label(env))
    show_host = options.get("show_host", True)
    host_text = f" • {host}" if (host and show_host) else ""
    text = f"{escape(label)}{escape(host_text)}"

    # Determine position and generate appropriate CSS
    position = options.get("position", "bottom")

    # Top-right corner ribbon
    if position == "top-right":
        opacity = options.get("opacity", 1.0)
        css = f"""
        #env-banner-bar {{
            position: fixed; top: 0; right: 0;
            width: 200px; height: 50px;
            overflow: hidden;
            z-index: 2147483647;
        }}
        #env-banner-bar-ribbon {{
            position: absolute; top: 15px; right: -50px;
            padding: 4px 0;
            width: 200px;
            transform: rotate(45deg);
            box-shadow: 0 1px 3px rgba(0,0,0,.2);
            display: flex; align-items: center; justify-content: center;
            font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700;
            background: {background}; color: {color}; text-transform: uppercase;
            opacity: {opacity};
        }}"""
        return f'<div id="env-banner-bar"><style>{css}</style><div id="env-banner-bar-ribbon" role="status">{text}</div></div>'

    # Top-left corner ribbon
    if position == "top-left":
        opacity = options.get("opacity", 1.0)
        css = f"""
        #env-banner-bar {{
            position: fixed; top: 0; left: 0;
            width: 200px; height: 50px;
            overflow: hidden;
            z-index: 2147483647;
        }}
        #env-banner-bar-ribbon {{
            position: absolute; top: 15px; left: -50px;
            padding: 4px 0;
            width: 200px;
            transform: rotate(-45deg);
            box-shadow: 0 1px 3px rgba(0,0,0,.2);
            display: flex; align-items: center; justify-content: center;
            font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700;
            background: {background}; color: {color}; text-transform: uppercase;
            opacity: {opacity};
        }}"""
        return f'<div id="env-banner-bar"><style>{css}</style><div id="env-banner-bar-ribbon" role="status">{text}</div></div>'

    # Bottom-right corner ribbon
    if position == "bottom-right":
        opacity = options.get("opacity", 1.0)
        css = f"""
        #env-banner-bar {{
            position: fixed; bottom: 0; right: 0;
            width: 200px; height: 50px;
            overflow: hidden;
            z-index: 2147483647;
        }}
        #env-banner-bar-ribbon {{
            position: absolute; bottom: 15px; right: -50px;
            padding: 4px 0;
            width: 200px;
            transform: rotate(-45deg);
            box-shadow: 0 1px 3px rgba(0,0,0,.2);
            display: flex; align-items: center; justify-content: center;
            font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700;
            background: {background}; color: {color}; text-transform: uppercase;
            opacity: {opacity};
        }}"""
        return f'<div id="env-banner-bar"><style>{css}</style><div id="env-banner-bar-ribbon" role="status">{text}</div></div>'

    # Bottom-left corner ribbon
    if position == "bottom-left":
        opacity = options.get("opacity", 1.0)
        css = f"""
        #env-banner-bar {{
            position: fixed; bottom: 0; left: 0;
            width: 200px; height: 50px;
            overflow: hidden;
            z-index: 2147483647;
        }}
        #env-banner-bar-ribbon {{
            position: absolute; bottom: 15px; left: -50px;
            padding: 4px 0;
            width: 200px;
            transform: rotate(45deg);
            box-shadow: 0 1px 3px rgba(0,0,0,.2);
            display: flex; align-items: center; justify-content: center;
            font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700;
            background: {background}; color: {color}; text-transform: uppercase;
            opacity: {opacity};
        }}"""
        return f'<div id="env-banner-bar"><style>{css}</style><div id="env-banner-bar-ribbon" role="status">{text}</div></div>'

    # Diagonal banners: bottom-left to top-right (/) or top-left to bottom-right (\)
    if position in ("diagonal", "diagonal-tlbr", "diagonal-bltr"):
        opacity = options.get("opacity", 0.5)
        # diagonal or diagonal-bltr: bottom-left to top-right (/) uses -45deg (default)
        # diagonal-tlbr: top-left to bottom-right (\) uses 45deg
        rotation = "45deg" if position == "diagonal-tlbr" else "-45deg"
        css = f"""
        #env-banner-bar {{
            position: fixed;
            top: 50%;
            left: 50%;
            width: 200vmax;
            height: 80px;
            transform: translate(-50%, -50%) rotate({rotation});
            opacity: {opacity};
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: system-ui, sans-serif;
            font-size: 14px;
            font-weight: 700;
            z-index: 2147483647;
            background: {background};
            color: {color};
            text-transform: uppercase;
            box-shadow: 0 2px 4px rgba(0,0,0,.3);
            pointer-events: none;
        }}"""
        return f'<style>{css}</style><div id="env-banner-bar" role="status">{text}</div>'

    # Default to bottom bar (or top if explicitly specified)
    opacity = options.get("opacity", 1.0)
    if position == "top":
        css = f"""
    #env-banner-bar {{
        position: fixed; left: 0; right: 0; height: 32px;
        display: flex; align-items: center; justify-content: center;
        font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700;
        z-index: 2147483647; background: {background}; color: {color};
        text-transform: uppercase; box-shadow: 0 1px 3px rgba(0,0,0,.2);
        opacity: {opacity};
    }}
    #env-banner-bar {{ top: 0; }} body {{ padding-top: 32px !important; }}"""
    else:  # bottom (default)
        css = f"""
    #env-banner-bar {{
        position: fixed; left: 0; right: 0; height: 32px;
        display: flex; align-items: center; justify-content: center;
        font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700;
        z-index: 2147483647; background: {background}; color: {color};
        text-transform: uppercase; box-shadow: 0 1px 3px rgba(0,0,0,.2);
        opacity: {opacity};
    }}
    #env-banner-bar {{ bottom: 0; top: auto; }} body {{ padding-bottom: 32px !important; }}"""

    return f'<style>{css}</style><div id="env-banner-bar" role="status">{text}</div>'
