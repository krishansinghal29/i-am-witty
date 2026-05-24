"""
One-time asset download script.

Downloads from Firebase/GCS:
  1. Push/Pull images (images/1.jpg … images/169.jpg) → app/static/images/
  2. Avatar images (from aiPersonasMetadata Firestore collection) → app/static/avatars/
  3. Exercise metadata (exerciseMeta Firestore collection) → app/constants/exercise_meta.json

Usage:
  python scripts/download_assets.py --credentials /path/to/service-account.json
"""

import argparse
import base64
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(SCRIPT_DIR, "..", "app")
IMAGES_DIR = os.path.join(APP_DIR, "static", "images")
AVATARS_DIR = os.path.join(APP_DIR, "static", "avatars")
EXERCISE_META_PATH = os.path.join(APP_DIR, "constants", "exercise_meta.json")
GCS_BUCKET = "getgame-584af.firebasestorage.app"


def download_push_pull_images(bucket):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Downloading 169 push/pull images to {IMAGES_DIR} ...")
    for i in range(1, 170):
        dest = os.path.join(IMAGES_DIR, f"{i}.jpg")
        if os.path.exists(dest):
            print(f"  {i}.jpg already exists, skipping")
            continue
        try:
            blob = bucket.blob(f"images/{i}.jpg")
            blob.download_to_filename(dest)
            print(f"  Downloaded {i}.jpg")
        except Exception as e:
            print(f"  ERROR downloading {i}.jpg: {e}", file=sys.stderr)
    print("Push/Pull images done.")


def download_avatars(db):
    os.makedirs(AVATARS_DIR, exist_ok=True)
    print(f"Downloading avatar images to {AVATARS_DIR} ...")

    avatar_urls = []
    try:
        docs = db.collection("aiPersonasMetadata").stream()
        for doc in docs:
            data = doc.to_dict()
            url = data.get("avatar_image_url")
            if url:
                avatar_urls.append(url)
    except Exception as e:
        print(f"ERROR fetching aiPersonasMetadata: {e}", file=sys.stderr)
        return

    # Write the list of URLs as avatars.json (served as-is; images remain on GCS CDN)
    avatars_json_path = os.path.join(AVATARS_DIR, "avatars.json")
    with open(avatars_json_path, "w") as f:
        json.dump(avatar_urls, f, indent=2)
    print(f"Saved {len(avatar_urls)} avatar URLs to {avatars_json_path}")
    print("Note: avatars remain on GCS CDN. If you want local copies, extend this script.")


def download_exercise_meta(db):
    print(f"Downloading exerciseMeta to {EXERCISE_META_PATH} ...")
    meta = {}
    try:
        docs = db.collection("exerciseMeta").stream()
        for doc in docs:
            meta[doc.id] = doc.to_dict()
    except Exception as e:
        print(f"ERROR fetching exerciseMeta: {e}", file=sys.stderr)
        return
    with open(EXERCISE_META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved {len(meta)} exercise meta entries.")


def main():
    parser = argparse.ArgumentParser(description="Download assets from Firebase/GCS")
    parser.add_argument("--credentials", required=True, help="Path to Firebase service account JSON")
    args = parser.parse_args()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.credentials

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        from google.cloud import storage as gcs
    except ImportError:
        print("Missing dependencies. Run: pip install firebase-admin google-cloud-storage", file=sys.stderr)
        sys.exit(1)

    cred = credentials.Certificate(args.credentials)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    storage_client = gcs.Client()
    bucket = storage_client.bucket(GCS_BUCKET)

    download_push_pull_images(bucket)
    download_avatars(db)
    download_exercise_meta(db)
    print("\nAll assets downloaded successfully.")


if __name__ == "__main__":
    main()
