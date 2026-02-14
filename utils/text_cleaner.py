# utils/text_cleaner.py
import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = text.strip()

   
    text = re.sub(r"\s+", " ", text)

    
    text = re.sub(r"[^\w\s.,!?]", "", text)

    return text
def clean_whatsapp_response(model_response: str, max_lines: int = 10) -> str:
    
    text = model_response

    
    text = re.sub(r'\|.*\|', '', text)
    text = re.sub(r'[-]{3,}', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()
    lines = text.split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append("...")  # indicate truncation
    cleaned_text = "\n".join(lines)
    return cleaned_text