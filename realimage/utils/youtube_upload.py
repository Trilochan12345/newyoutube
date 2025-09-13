import datetime
import os
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLIENT_SECRETS_FILE = "C:/Users/trilo/OneDrive/Desktop/videoautomation/video/secrets/client_secrets.json" # ensure this is the correct path
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def upload_to_youtube_scheduled(video_path, title, description, tags, thumbnail_path):
    youtube = get_authenticated_service()

    print("Uploading video from:", video_path)
    print("Video file exists?", os.path.exists(video_path))

    # Comment out scheduling for initial test
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
            # "publishAt": publish_time,  # disabled for now
        },
        "notifySubscribers": False,
    }

    media = MediaFileUpload(video_path, resumable=True)

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )

        response = None
        max_retries = 10
        retries = 0
        while response is None and retries < max_retries:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
            retries += 1

        if response is None:
            print("Upload failed: no response after retries")
            return None

        video_id = response.get("id")
        print("Upload successful. Video ID:", video_id)

        if thumbnail_path and os.path.exists(thumbnail_path):
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded.")

        return video_id

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        raise

