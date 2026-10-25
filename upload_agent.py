from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_video(video_path, title, description, tags, thumbnail_path, creds_path="token.json"):
    creds = Credentials.from_authorized_user_file(creds_path)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:95],
            "description": description,
            "tags": tags,
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()

    try:
        youtube.thumbnails().set(videoId=response["id"], media_body=MediaFileUpload(thumbnail_path)).execute()
    except Exception as e:
        print(f"Thumbnail upload skipped: {e}")

    return response["id"]
