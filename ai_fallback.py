import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def ai_extract(raw_text):
    prompt = f"""Extract purchase details from this message. The message may be in English or Egyptian Arabic (or a mix of both), and may contain typos or misspelled field labels — for example "Qiantity", "Quantaty", "QUNTATY" all mean "Quantity"; "Amout", "Amnt" mean "Amount"; "الكمية" means "Quantity"; "السعر" or "المبلغ" mean "Amount"; "الصنف" or "الغرض" mean "Item".

Respond with ONLY a JSON object with exactly these keys: "item", "quantity", "amount", "vendor", "project" — nothing else, no explanation, no markdown formatting.
- "item" should be the name of the thing purchased, translated to English if written in Arabic.
-"Quantity" can be writtien incorrectly as some people make spelling mistakes Mistakes such as "Qiantity", "Quantaty", "QUNTATY", but it should be a whole number (digits only, no units or words).
- "quantity" should be a whole number (digits only, no units or words).
- "amount" should be a number representing the price (digits only, no currency symbols).
- "vendor" should be the shop/supplier name if mentioned, otherwise an empty string.
- "project" should be the project or job name if mentioned, otherwise an empty string.
- If a value cannot be confidently determined even after accounting for typos, use an empty string for it.

Message: "{raw_text}"
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        raw_output = response.text.strip()
        raw_output = raw_output.replace(
            "```json", "").replace("```", "").strip()
        data = json.loads(raw_output)
        return data
    except Exception:

        return None
