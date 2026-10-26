import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_authenticated_service():
    """
    Reads OAuth credentials from token.json, written to disk by the
    GitHub Actions workflow step "Restore YouTube OAuth Token".
    """
    with open("token.json", "r") as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"]
    )
    return build("youtube", "v3", credentials=creds)


def upload_short(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "27"  # 27 = Education
):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True  # MANDATORY for kids content
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ Uploaded: https://youtube.com/shorts/{video_id}")
    return video_id
