"""
translator.py — English to Kannada translation
Primary: IndicTrans2 | Fallback: deep-translator (Google)
"""

import os

_INDIC_AVAILABLE = False
_translator_pipeline = None


def _try_load_indictrans2():
    global _INDIC_AVAILABLE, _translator_pipeline
    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
        print(f"[Translator] Loading IndicTrans2...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)
        model.eval()
        _translator_pipeline = (tokenizer, model)
        _INDIC_AVAILABLE = True
        print("[Translator] IndicTrans2 loaded.")
    except Exception as e:
        print(f"[Translator] IndicTrans2 unavailable ({e}). Using fallback.")
        _INDIC_AVAILABLE = False


def _translate_with_indictrans2(text: str) -> str:
    import torch
    tokenizer, model = _translator_pipeline
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model.generate(**inputs, num_beams=4, max_length=512, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def _translate_with_fallback(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="en", target="kn").translate(text)
    except Exception:
        pass
    try:
        from googletrans import Translator
        return Translator().translate(text, src="en", dest="kn").text
    except Exception as e:
        return f"[Translation unavailable] {text}"


def initialize_translator(force_indictrans: bool = False):
    if force_indictrans or os.environ.get("USE_INDICTRANS2", "").lower() == "true":
        _try_load_indictrans2()


def translate_to_kannada(text: str) -> str:
    if not text or not text.strip():
        return ""
    if _INDIC_AVAILABLE and _translator_pipeline:
        return _translate_with_indictrans2(text)
    return _translate_with_fallback(text)