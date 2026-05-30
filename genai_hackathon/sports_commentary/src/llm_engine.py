"""
llm_engine.py — Groq API with JSON mode
"""

import json
import re
import time
import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def call_llm(system_prompt: str, user_prompt: str, retries: int = 2) -> dict:
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.5,
                response_format={"type": "json_object"},
            )
            raw_text = response.choices[0].message.content

            print("\n--- GROQ RAW ---")
            print(repr(raw_text[:600]))
            print("--- END ---\n")

            parsed = json.loads(raw_text)
            # Groq sometimes wraps response in {"result": [...]} or similar
            if isinstance(parsed, dict):
                # unwrap single-key dict containing a list
                keys = list(parsed.keys())
                if len(keys) == 1 and isinstance(parsed[keys[0]], dict):
                    return parsed[keys[0]]
            return parsed

        except json.JSONDecodeError as e:
            print(f"[JSON ERROR] {e}")
            print(f"[RAW] {repr(raw_text[:400])}")
            if attempt < retries:
                time.sleep(2)
                continue
            return {"error": f"JSON parse failed: {str(e)}"}

        except Exception as e:
            err = str(e)
            print(f"[GROQ ERROR] {err}")
            if attempt < retries:
                time.sleep(3)
                continue
            return {"error": f"Groq error: {err}"}

    return {"error": "Max retries exceeded."}


def generate_cricket_commentary(ctx, innings_index: int = 0) -> dict:
    from src.prompt_builder import build_cricket_over_by_over_prompt
    system, user = build_cricket_over_by_over_prompt(ctx, innings_index)
    return call_llm(system, user)


def generate_cricket_post_match(ctx) -> dict:
    from src.prompt_builder import build_cricket_post_match_prompt
    system, user = build_cricket_post_match_prompt(ctx)
    return call_llm(system, user)


def generate_football_commentary(ctx) -> dict:
    from src.prompt_builder import build_football_commentary_prompt
    system, user = build_football_commentary_prompt(ctx)
    return call_llm(system, user)