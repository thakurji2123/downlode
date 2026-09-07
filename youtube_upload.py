import os
import random
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "Final_Long_Educational_Video.mp4"
CATEGORY_ID = "24" 

TITLES = [
    "Zindagi Ki Sabse Badi Seekh 😔 | Hindi Stories",
    "Ek Kahani Jo Aapko Sochne Par Majboor Kar Degi 💡",
    "Aisa Kisi Ke Sath Na Ho 😭 | Emotional Lesson",
    "Sacche Pyaar Ki Kahani ❤️ | Heart Touching Story"
]

DESCRIPTIONS = [
    "Dosto, aaj ki yeh kahani bohot seekh dene wali hai. Agar video pasand aaye to channel ko subscribe zaroor karein.\n\n#Story #Emotional #HeartTouching",
    "Kuch kahaniyan seedha dil par lagti hain. Yeh video unhi mein se ek hai.\n\nLike aur Subscribe zaroor karein!\n\n#HindiStories #LifeLesson",
]

TAG_SETS = [
    ["Story", "Emotional Story", "Heart Touching", "Hindi", "Life Lesson"],
    ["Hindi Stories", "Moral Story", "Rula dene wali kahani", "Motivation"],
]

def upload_video():
    if not os.path.exists(VIDEO_FILE):
        return

    selected_title = random.choice(TITLES)
    selected_desc = random.choice(DESCRIPTIONS)
    selected_tags = random.choice(TAG_SETS)
    
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.upload'])
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "categoryId": CATEGORY_ID,
            "title": selected_title,
            "description": selected_desc,
            "tags": selected_tags
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
