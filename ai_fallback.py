import os
import json
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def ai_extract(raw_text):
    prompt = f"""Extract purchase details from this message. Respond with ONLY a JSON object with keys "item", "quantity", "amount" — nothing else, no explanation, no markdown formatting.
If a value cannot be confidently determined, use an empty string for it.

Message: "{raw_text}"
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_output = response.content[0].text.strip()
        raw_output = raw_output.replace(
            "```json", "").replace("```", "").strip()
        data = json.loads(raw_output)
        return data
    except Exception:
        return None
