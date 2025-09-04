import random
import re
import spacy

# --- 1. Generate Title ---
def generate_title(script_text):
    templates = [
        "Why {} Will Rule 2030",
        "The Rise of {}",
        "{} Is Just Getting Started",
        "What No One Tells You About {}",
        "{} Is Eating the World",
    ]

    keywords = extract_keywords(script_text)
    if not keywords:
        keywords = ["AI"]

    subject = random.choice(keywords)
    template = random.choice(templates)

    return template.format(subject.title())

# --- 2. Generate Description ---
def generate_description(script_text, credits=None, hashtags=None):
    lines = script_text.strip().split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    summary = "\n".join(lines[:3])  # First 2–3 lines from script

    # Auto-insert credits
    credit_block = "\n\n🎥 Visuals by:\n"
    if credits:
        for c in credits:
            credit_block += f"- {c}\n"
    else:
        credit_block += "- Pexels, Unsplash, AI-generated\n"

    # Add hashtags
    if hashtags is None:
        hashtags = ["#AI", "#Python", "#Tech", "#Shorts"]
    hashtag_str = " ".join(hashtags)

    return f"{summary}\n\n{credit_block}\n{hashtag_str}"

# --- 3. Generate Tags from script ---
def extract_keywords(script_text, top_n=10):
    nlp = spacy.load("en_core_web_sm")  # Lazy load here
    doc = nlp(script_text)
    nouns = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2]
    keywords = list(dict.fromkeys(nouns))  # Deduplicate
    return keywords[:top_n]
