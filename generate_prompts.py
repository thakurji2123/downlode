import os
import sys
import google.generativeai as genai
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Gemini API Key missing!")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.6-flash')

TOPICS_FILE = "topics.txt"
PROMPTS_FILE = "prompts.txt"
META_FILE = "metadata.json"

def main():
    if not os.path.exists(TOPICS_FILE):
        print("❌ topics.txt not found!")
        sys.exit(1)

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f.readlines() if line.strip()]

    if not topics:
        print("❌ No topics left in topics.txt!")
        sys.exit(1)

    current_topic = topics[0]
    print(f"🚀 Generating script for topic: {current_topic}")

    # ==========================================
    # 📝 SCRIPT GENERATION (Har image 5 second ke liye)
    # ==========================================
        system_prompt = f"""
    You are a professional YouTube scriptwriter for a Hindi Motivation/Story channel. 
    Topic: "{current_topic}".
    Create EXACTLY 160 scenes for a video.
    
    CRITICAL RULE: 
    1. The Image Description MUST be in English (for the AI image generator).
    2. The Voiceover text MUST be in HINDI language (Devanagari script - like 'नमस्ते').
    3. Each voiceover text MUST be EXACTLY 10 to 14 words long.
    
    Strict Format: Image Description | Voiceover text
    Example:
    A successful man standing on a mountain, sunrise, cinematic | सफलता एक दिन में नहीं मिलती, लेकिन मेहनत करने वालों को एक दिन जरूर मिलती है।
    """
    
    response = model.generate_content(system_prompt)
    prompts_text = response.text.strip()

    with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
        f.write(prompts_text)
    print("✅ prompts.txt successfully created with ~160 scenes!")

    # Generate Viral MetaData
    meta_prompt = f"""
    Topic: "{current_topic}".
    Generate a viral YouTube Title (max 60 chars), Description, and Tags (comma separated) for a US Christian audience.
    Return strictly in JSON format like this:
    {{"title": "Title Here", "description": "Desc Here", "tags": "tag1, tag2, tag3"}}
    """
    meta_response = model.generate_content(meta_prompt)
    meta_json_str = meta_response.text.replace("```json", "").replace("```", "").strip()
    
    with open(META_FILE, "w", encoding="utf-8") as f:
        f.write(meta_json_str)
    print("✅ metadata.json successfully created!")

    # Delete the used topic
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        for topic in topics[1:]:
            f.write(topic + "\n")
    print(f"🗑️ Topic '{current_topic}' removed from topics.txt")

if __name__ == "__main__":
    main()
