"""
Fun Fact Generator — a PyWebIO app that fetches random useless facts.
"""

import json
import requests
from pywebio.output import *
from pywebio.session import hold

# --- Configuration Constants ---
API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"

# --- UI Constants ---
APP_TITLE = "Fun Fact Generator"
ICON_URL = "https://media.geeksforgeeks.org/wp-content/uploads/20210720224119/MessagingHappyicon.png"
FOOTER_TEXT = "\U0001f4a1 uselessfacts.jsph.pl \u2022 click for random fact"
INITIAL_MESSAGE = "\u2728 Press the button to get a fun fact! \u2728"
LOADING_MESSAGE = "Fetching a fun fact..."
BUTTON_LABEL = "\u2728 Get Another Fact \u2728"

# --- Error Messages ---
ERROR_MESSAGES = {
    "timeout":     "\u23f0 Request timed out. Please check your internet connection.",
    "connection":  "\U0001f4e1 Cannot connect to the internet. Please try again later.",
    "api_parse":   "\U0001f527 Oops! The fact factory is temporarily broken. Try again.",
    "unexpected":  "\u274c Unexpected error: {error_detail}",
}

# --- CSS Styles ---
CSS_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

    * {
        font-family: 'Poppins', sans-serif;
        box-sizing: border-box;
    }

    body {
        align-items: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        justify-content: center;
        margin: 0;
        min-height: 100vh;
        padding: 20px;
    }

    .fact-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(2px);
        border-radius: 32px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        max-width: 700px;
        padding: 2rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        width: 100%;
    }

    .fact-card:hover {
        box-shadow: 0 24px 48px rgba(0, 0, 0, 0.25);
        transform: scale(1.02);
    }

    h2 {
        align-items: center;
        color: #4a5568;
        display: flex;
        font-weight: 700;
        gap: 12px;
        justify-content: center;
        margin-bottom: 1.5rem;
    }

    h2 img {
        height: auto;
        vertical-align: middle;
        width: 48px;
    }

    .fact-text {
        background: #f7fafc;
        border-radius: 24px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05),
                    0 2px 5px rgba(0, 0, 0, 0.05);
        color: #2d3748;
        font-size: 1.6rem;
        font-weight: 500;
        line-height: 1.4;
        margin: 1.5rem 0;
        overflow-wrap: break-word;
        padding: 1.5rem;
        transition: all 0.2s;
        word-break: break-word;
    }

    .btn-fun {
        background: linear-gradient(95deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 50px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        color: #fff !important;
        cursor: pointer;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1rem;
        padding: 12px 32px;
        transition: all 0.3s ease;
    }

    .btn-fun:hover,
    .btn-fun:focus-visible {
        background: linear-gradient(95deg, #5a67d8 0%, #6b46a0 100%);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        outline: none;
        transform: translateY(-3px);
    }

    .error-text {
        background: #fff5f5;
        border-left: 5px solid #e53e3e;
        border-radius: 12px;
        color: #e53e3e;
        font-weight: 500;
        padding: 1rem;
    }

    .loader {
        animation: spin 1s linear infinite;
        border: 4px solid #e2e8f0;
        border-radius: 50%;
        border-top-color: #667eea;
        display: inline-block;
        height: 30px;
        margin: 1rem auto;
        width: 30px;
    }

    @keyframes spin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loader-text {
        color: #4a5568;
        font-weight: 500;
        margin-top: 0.5rem;
        text-align: center;
    }

    footer {
        color: #a0aec0;
        font-size: 0.8rem;
        margin-top: 2rem;
    }

    @media (max-width: 480px) {
        .fact-card {
            padding: 1.25rem;
        }

        .fact-text {
            font-size: 1.2rem;
            padding: 1rem;
        }

        .btn-fun {
            font-size: 1rem;
            padding: 10px 24px;
        }
    }
</style>
"""


def show_header() -> None:
    """Render the app header and card container."""
    put_html(CSS_STYLES)
    put_html(f"""
        <div class="fact-card">
            <h2>
                <img src="{ICON_URL}" alt="App icon" width="48" height="48" />
                {APP_TITLE}
            </h2>

            <div id="fact-content">
                <!-- dynamic fact will appear here -->
            </div>

            <div id="button-area"></div>

            <footer>{FOOTER_TEXT}</footer>
        </div>
    """)

    put_scope("fact_content", content=put_text(INITIAL_MESSAGE))
    put_scope("button_area")


def display_fact(fact_text: str, is_error: bool = False) -> None:
    """Update the fact area with text, styled differently on error."""
    clear("fact_content")
    icon = "\u26a0\ufe0f" if is_error else "\U0001f4d6"
    css_class = "error-text" if is_error else ""
    put_html(
        f'<div class="fact-text {css_class}">{icon} {fact_text}</div>',
        scope="fact_content",
    )


def show_loader() -> None:
    """Show a loading spinner in the fact area."""
    clear("fact_content")
    put_html(
        f"""
        <div class="loader"></div>
        <p class="loader-text">{LOADING_MESSAGE}</p>
        """,
        scope="fact_content",
    )


def get_fun_fact(_=None) -> None:
    """Fetch a random fact and update the UI."""
    show_loader()

    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        display_fact(data["text"])
    except requests.exceptions.Timeout:
        display_fact(ERROR_MESSAGES["timeout"], is_error=True)
    except requests.exceptions.ConnectionError:
        display_fact(ERROR_MESSAGES["connection"], is_error=True)
    except (KeyError, json.JSONDecodeError):
        display_fact(ERROR_MESSAGES["api_parse"], is_error=True)
    except Exception as e:
        display_fact(
            ERROR_MESSAGES["unexpected"].format(error_detail=str(e)),
            is_error=True,
        )


def create_button() -> None:
    """Create the fetch button inside its scope (replaces any previous)."""
    clear("button_area")
    put_buttons(
        [dict(label=BUTTON_LABEL, value="refresh", color="outline-success")],
        onclick=get_fun_fact,
        scope="button_area",
    )


if __name__ == "__main__":
    show_header()
    create_button()
    hold()