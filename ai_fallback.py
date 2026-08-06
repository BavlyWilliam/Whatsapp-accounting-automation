import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def ai_extract(raw_text):
    prompt = f"""Extract purchase details from this message, which was typed by hand and may contain typos, misspelled field labels, or unconventional phrasing (e.g. "Qiantity", "Quantaty", "QUNTATY" all mean "Quantity"; "Amout", "Amnt" mean "Amount"; "Itm" means "Item").

Respond with ONLY a JSON object with exactly these keys: "item", "quantity", "amount" — nothing else, no explanation, no markdown formatting.
- "item" should be the name of the thing purchased, as text.
- "quantity" should be a whole number (digits only, no units or words).
- "amount" should be a number representing the price (digits only, no currency symbols).
- If a value cannot be confidently determined even after accounting for typos, use an empty string for it.

Message: "{raw_text}"
"""

    try:
        response = model.generate_content(prompt)
        raw_output = response.text.strip()
        raw_output = raw_output.replace(
            "```json", "").replace("```", "").strip()
        data = json.loads(raw_output)
        return data
    except Exception:
        return None
