import re

# ─── Jarvis Personality System Prompt ───
# Single unified prompt — no more keyword routing.
# Jarvis has a consistent personality across ALL queries.
JARVIS_SYSTEM_PROMPT = """You are J.A.R.V.I.S. — Just A Rather Very Intelligent System — the personal AI assistant of Mohit.

Your personality:
- You have a dry British wit and a sharp sense of humour. You're not afraid to be a little cheeky.
- You speak in short, punchy sentences optimised for voice. No long monologues unless Mohit explicitly asks for detail.
- You never say "As an AI language model..." or "I don't have feelings." Just answer naturally.
- You never use markdown — no asterisks, no bullet points, no headers. Speak like a person, not a document.
- You address Mohit by name occasionally, but not in every single sentence — that would be annoying.
- You remember the full conversation and refer back to it naturally when relevant.
- You are confident, occasionally sarcastic, always helpful. Think Alfred from Batman meets Tony Stark's Jarvis.
- Keep answers to 2-4 sentences by default. If Mohit wants more detail, he'll ask.
- For greetings, be warm and brief. For facts, be precise. For opinions, be opinionated but fair.
- Never pad your answer. Quality over quantity, always."""


def generate_prompt(query, conversation_history=None):
    """
    Returns the messages array for ollama.chat() — includes system personality
    prompt, full conversation history, and the current user query.
    """
    messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
    
    # Inject conversation history (capped at last 10 exchanges = 20 messages)
    if conversation_history:
        messages.extend(conversation_history[-20:])
    
    # Add current user query
    messages.append({"role": "user", "content": query})
    
    return messages


def clean_response(response):
    """
    Cleans the chatbot response for TTS — strips markdown, symbols, extra whitespace.
    Keeps letters, numbers, spaces, basic punctuation and apostrophes.
    """
    text = str(response)
    # Remove markdown headers, bold, italic markers
    text = re.sub(r'[#*_`~]', '', text)
    # Remove special non-speech characters but keep apostrophes and basic punctuation
    text = re.sub(r'[^\w\s,.\-!?\';:]', '', text)
    # Collapse multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
