import os
import json
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "Final_Long_Educational_Video.mp4"
META_FILE = "metadata.json"
CATEGORY_ID = "24" # 24 = Entertainment (Aap apne hisab se badal sakte ho)

def upload_video():
    if not os.path.exists(VIDEO_FILE):
        print("❌ Video file not found!")
        return
        
    if not os.path.exists(META_FILE):
        print("❌ Metadata file not found!")
        return

    with open(META_FILE, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    title = meta_data.get("title", "रहस्यमयी कहानी 😱")
    
    # ⚠️ AI ALTERED CONTENT DISCLAIMER (Required by YouTube Policy)
    ai_disclaimer = "⚠️ [Altered Content]: इस वीडियो में इस्तेमाल किए गए विजुअल्स और आवाज़ AI (Artificial Intelligence) द्वारा बनाए गए हैं।\n\n"
    
    description = ai_disclaimer + meta_data.get("description", "")
    tags = [tag.strip() for tag in meta_data.get("tags", "").split(",")]

    print(f"📌 UPLOADING: {title}")
    
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.upload'])
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "categoryId": CATEGORY_ID,
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:15]
        },
        "status": {
            "privacyStatus": "public", 
            "selfDeclaredMadeForKids": False
            # API me 'AlteredContent' ka direct tick box abhi nahi hai, isliye humne description me dala hai.
        }
    }

    media_file = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media_file)
    
    try:
        response = request.execute()
        print(f"✅ VIDEO SUCCESSFULLY UPLOADED! Link: https://youtu.be/{response['id']}")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

if __name__ == "__main__":
    upload_video()
