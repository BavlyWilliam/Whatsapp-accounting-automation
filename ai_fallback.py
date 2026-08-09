import json
import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MIN_SECONDS_BETWEEN_CALLS = 4.5
_last_call_time = 0


def ai_extract(raw_text, max_retries=2):
    global _last_call_time

    prompt = f"""Extract purchase details from this message. The message may be in English or Egyptian Arabic (or a mix of both), and may contain typos or misspelled field labels — for example "Qiantity", "Quantaty", "QUNTATY" all mean "Quantity"; "Amout", "Amnt" mean "Amount"; "الكمية" means "Quantity"; "السعر" or "المبلغ" mean "Amount"; "الصنف" or "الغرض" mean "Item".

Respond with ONLY a JSON object with exactly these keys: "item", "quantity", "amount", "vendor", "project" — nothing else, no explanation, no markdown formatting.
- "item" should be the name of the thing purchased, translated to English if written in Arabic.
- "quantity" should be a whole number (digits only, no units or words).
- "amount" should be a number representing the price (digits only, no currency symbols).
- "vendor" should be the shop/supplier name if mentioned, otherwise an empty string.
- "project" should be the project or job name if mentioned, otherwise an empty string.
- If a value cannot be confidently determined even after accounting for typos, use an empty string for it.

Message: "{raw_text}"
"""

    for attempt in range(max_retries + 1):
        elapsed = time.time() - _last_call_time
        if elapsed < MIN_SECONDS_BETWEEN_CALLS:
            time.sleep(MIN_SECONDS_BETWEEN_CALLS - elapsed)

        try:
            _last_call_time = time.time()
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text.strip())
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                time.sleep(10)
                continue
            return None

    return None
