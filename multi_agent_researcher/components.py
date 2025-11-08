"""
components.py
-------------
Small UI helper components used by the Streamlit frontend.

Why:
- Encapsulates Lottie loading and rendering logic (safely).
- Keeps main UI code clean by centralizing external requests and fallbacks.
"""

import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url: str, timeout: float = 6.0):
    """
    Load a Lottie JSON given a URL. Returns JSON or None.
    This function is defensive: any network error returns None so the UI does not crash.
    """
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        # Use Streamlit debug logging so the UI doesn't show a traceback to the user.
        st.debug(f"components.load_lottie_url: failed to load {url}: {e}")
    return None

def lottie_spinner(url: str = None, lottie_json: dict = None, height: int = 150, key: str = None):
    """
    Render a Lottie animation as a spinner area.
    - url: optional URL to load the lottie JSON from.
    - lottie_json: optional preloaded JSON (preferred for tests/offline).
    Returns True if a Lottie was rendered, False otherwise (so the caller can show fallback UI).
    """
    try:
        if lottie_json is None and url:
            lottie_json = load_lottie_url(url)
        if lottie_json:
            st_lottie(lottie_json, height=height, key=key)
            return True
    except Exception as e:
        st.debug(f"components.lottie_spinner: render failed: {e}")
    # fallback: simple message
    st.write("Loading...")
    return False
