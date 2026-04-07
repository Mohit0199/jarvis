"""
engine/web_search.py
Real-time web search via DuckDuckGo — no API key needed.
Detects time-sensitive queries and injects live context into LLM responses.
"""

from duckduckgo_search import DDGS

# Keywords that suggest the LLM's training data may be stale
TIME_SENSITIVE_KEYWORDS = [
    "today", "right now", "currently", "latest", "recent", "news",
    "current", "2024", "2025", "2026", "this week", "this month",
    "just happened", "who won", "score", "weather", "temperature",
    "forecast", "price", "stock", "bitcoin", "crypto", "trending",
    "live", "breaking", "update", "happened"
]


def needs_web_search(query: str) -> bool:
    """Returns True if the query likely needs real-time information."""
    q = query.lower()
    return any(keyword in q for keyword in TIME_SENSITIVE_KEYWORDS)


def web_search(query: str, max_results: int = 3) -> str:
    """
    Search DuckDuckGo and return a concise context string for the LLM.
    Returns empty string on failure so chatBot() can gracefully degrade.
    """
    try:
        print(f"🌐 Web search: '{query}'")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            print("🌐 No web results found.")
            return ""

        context_parts = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            if title or body:
                context_parts.append(f"[{i}] {title}: {body}")

        context = "\n".join(context_parts)
        print(f"🌐 Got {len(results)} results ({len(context)} chars)")
        return context

    except Exception as e:
        print(f"🌐 Web search failed: {e}")
        return ""
