import os
import random
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "Final_Long_Educational_Video.mp4"
CATEGORY_ID = "24" 

# ==========================================
# 🎲 DYNAMIC UNIQUE TITLE/DESC GENERATOR
# ==========================================

def generate_unique_metadata():
    # In tukdon ko jod kar title banega (Taaki kabhi copy/duplicate na ho)
    hooks = ["Rula dene wali kahani", "Dil chhu lene wali baat", "Zindagi ki sachai", "Ek sachi seekh", "Aisa kisi ke sath na ho", "Rongte khade kar dene wali story"]
    topics = ["Pyaar ka dard", "Rishton ki ehmiyat", "Akelepan ka safar", "Maa Baap ka pyaar", "Dhoka aur vishwas", "Kismat ka khel"]
    emojis = ["💔", "🥺", "😭", "❤️", "✨", "🙏", "😔"]

    # Generate Unique Title: "Rula dene wali kahani - Pyaar ka dard 💔"
    unique_title = f"{random.choice(hooks)} - {random.choice(topics)} {random.choice(emojis)}"

    # Generate Unique Description
    desc_intros = [
        "Agar aapne ye video nahi dekhi, toh bohot kuch miss kar doge.", 
        "Dosto is kahani ko sunkar aapke bhi aansu aa jayenge.", 
        "Zindagi me kabhi kabhi aisi seekh milti hai jo humesha yaad rehti hai.",
        "Kahaani jo aapke dil ko chhu jayegi, end tak zaroor dekhna."
    ]
    desc_ctas = [
        "\n\nVideo pasand aaye toh Like aur Subscribe zaroor karein! 🙏", 
        "\n\nApne dosto ke sath is seekh ko share karein aur Channel ko subscribe karna na bhoolein! ❤️"
    ]
    tags = "\n\n#EmotionalStory #HindiStories #LifeLessons #Trending #HeartTouching #SadStory"

    unique_description = f"{random.choice(desc_intros)} {random.choice(desc_ctas)} {tags}"
    
    return unique_title, unique_description

def upload_video():
    if not os.path.exists(VIDEO_FILE):
        print(f"❌ Error: {VIDEO_FILE} not found!")
        return

    # Random Function call kiya
    selected_title, selected_desc = generate_unique_metadata()

    print(f"📌 FINAL TITLE: {selected_title}")
    
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.upload'])
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "categoryId": CATEGORY_ID,
            "title": selected_title,
            "description": selected_desc,
            # Tags ko array me convert kiya
            "tags": ["Hindi Stories", "Emotional", "Moral Story", "Trending", "Life Lesson"]
        },
        "status": {
            "privacyStatus": "public", 
            "selfDeclaredMadeForKids": False
        }
    }

    media_file = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media_file)
    response = request.execute()
    print(f"✅ VIDEO SUCCESSFULLY UPLOADED! Link: https://youtu.be/{response['id']}")

if __name__ == "__main__":
    upload_video()
