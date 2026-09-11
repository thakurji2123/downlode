import os
import sys
import time
import json
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

API_KEYS = [k.strip() for k in os.getenv("GEMINI_API_KEY", "").split(",") if k.strip()]
if not API_KEYS:
    print("❌ Gemini API Key missing!")
    sys.exit(1)

TOPICS_FILE = "topics.txt"
PROMPTS_FILE = "prompts.txt"
META_FILE = "metadata.json"

def generate_with_retry(prompt, max_retries=6):
    for attempt in range(max_retries):
        key_index = attempt % len(API_KEYS)
        genai.configure(api_key=API_KEYS[key_index])
        model = genai.GenerativeModel('gemini-1.5-flash')
        try:
            print(f"📡 Trying API Key #{key_index + 1}...")
            response = model.generate_content(prompt)
            return response.text.strip()
        except ResourceExhausted:
            wait_time = 65 * (attempt + 1)
            print(f"⚠️ Quota hit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            time.sleep(15)
    sys.exit(1)

def main():
    if not os.path.exists(TOPICS_FILE):
        sys.exit(1)

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f.readlines() if line.strip()]

    if not topics:
        sys.exit(1)

    current_topic = topics[0]
    print(f"🚀 Generating script for topic: {current_topic}")

    # ==========================================
    # 📝 HINDI SCRIPT PROMPT FOR GEMINI
    # ==========================================
    system_prompt = f"""
    You are a professional YouTube scriptwriter for a Hindi channel.
    Topic: "{current_topic}".

    You have 2 tasks. Follow them exactly.

    TASK 1:
    Create EXACTLY 160 scenes for a video.
    
    CRITICAL RULES:
    1. The Image Description (Left side of '|') MUST be in English.
    2. The Voiceover text (Right side of '|') MUST be in HINDI language (Devanagari script, e.g., 'नमस्ते').
    3. Each Hindi voiceover MUST be exactly 10 to 14 words long to fit the 5-second screen time.
    
    Strict Format: Image Description | Voiceover text
    Do not add numbers. Just the format.

    TASK 2:
    After the 160 lines, write exactly this separator: ===METADATA===
    Then output a JSON for a Hindi YouTube audience:
    {{"title": "Viral Hindi Title (Hinglish/Hindi)", "description": "Hindi description", "tags": "hindi tag1, hindi tag2"}}

    Full output example:
    Jesus walking in Jerusalem, cinematic lighting | यीशु मसीह का रास्ता कठिन था, लेकिन उनका विश्वास सबसे मजबूत था।
    Jesus speaking to a crowd | उनके कहे हुए अनमोल वचन आज भी लाखों लोगों को शांति देते हैं।
    ===METADATA===
    {{"title": "यीशु मसीह का चमत्कार 🙏", "description": "इस वीडियो को अंत तक जरूर देखें!", "tags": "Jesus Hindi, Bible Story Hindi"}}
    """

    full_response = generate_with_retry(system_prompt)

    if "===METADATA===" in full_response:
        prompts_text, meta_text = full_response.split("===METADATA===", 1)
        prompts_text = prompts_text.strip()
        meta_json_str = meta_text.replace("```json", "").replace("```", "").strip()
        with open(META_FILE, "w", encoding="utf-8") as f:
            f.write(meta_json_str)
    else:
        prompts_text = full_response

    with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
        f.write(prompts_text)

    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        for topic in topics[1:]:
            f.write(topic + "\n")

if __name__ == "__main__":
    main()
