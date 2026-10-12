import os
from dotenv import load_dotenv

load_dotenv()


def get(name, default=None):
    val = os.getenv(name)
    if val:
        return val
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                reg_val, _ = winreg.QueryValueEx(key, name)
                if reg_val:
                    return reg_val
        except OSError:
            pass
    return default


def require(name):
    val = get(name)
    if not val:
        raise RuntimeError(f"Missing required setting: {name} (see .env.example)")
    return val


def flag(name, default=False):
    return str(get(name, str(default))).strip().lower() in ("1", "true", "yes", "on")


GRAPH_HOST = get("GRAPH_HOST", "graph.instagram.com")
GRAPH_VERSION = get("GRAPH_VERSION", "v21.0")
CLAUDE_MODEL = get("CLAUDE_MODEL", "claude-sonnet-5-5")
LLM_PROVIDER = get("LLM_PROVIDER", "gemini").lower()
GEMINI_MODEL = get("GEMINI_MODEL", "gemini-3.8-flash")
HANDLE = get("IG_HANDLE", "@abhijeetkumar.founder")
BRAND_VOICE = get("BRAND_VOICE", "Sharp, practical, no hype.")
AUTO_POST = flag("AUTO_POST", False)
POST_TIMES = [t.strip() for t in get("POST_TIMES", "09:00,19:00").split(",") if t.strip()]
MAX_POSTS_PER_DAY = int(get("MAX_POSTS_PER_DAY", "3"))
OUTPUT_DIR = get("OUTPUT_DIR", "output")
