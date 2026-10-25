from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_short(video_path, hook_line, topic_title, creds_path="token.json"):
    creds = Credentials.from_authorized_user_file(creds_path)
    youtube = build("youtube", "v3", credentials=creds)

    clean_hook = hook_line.replace("\n", " ").strip()[:75]
    title = f"{clean_hook} #Shorts"
    description = f"{clean_hook}\n\nTopic: {topic_title}\n#Shorts #TrueCrime #History #Documentary"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["Shorts", "true crime", "history", topic_title],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    return response["id"]
