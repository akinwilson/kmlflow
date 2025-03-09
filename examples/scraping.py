import kfp
from kfp import dsl
import boto3
import uuid
import pandas as pd
from pytube import YouTube
from pytube import Search
import time
import os

# MinIO configuration
MINIO_ENDPOINT_URL = "http://192.168.58.2"
MINIO_DATA_BUCKET_NAME = "data"
AWS_ACCESS_KEY_ID = "minioaccesskey"
AWS_SECRET_ACCESS_KEY = "miniosecretkey123"

# Initialize MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="eu-west-2",
    config=boto3.session.Config(signature_version="s3v4"),
)


@dsl.component(
    base_image="python:3.9",
    packages_to_install=["pytube", "boto3", "pandas"],
)
def scrape_youtube_videos(output_dir: str, num_videos: int = 30):
    """Scrape YouTube videos, download audio and subtitles, and store in MinIO."""
    search_terms = ["product reviews", "talk shows", "vlogs"]
    downloaded_videos = set()

    for _ in range(num_videos):
        # Randomize search term
        search_term = search_terms[_ % len(search_terms)]
        search = Search(search_term)
        video_url = None

        # Find a video with English subtitles
        for video in search.results:
            if video.video_id not in downloaded_videos:
                video_url = video.watch_url
                break

        if not video_url:
            continue

        # Download audio and subtitles
        yt = YouTube(video_url)
        video_id = yt.video_id
        title = yt.title
        description = yt.description
        length = yt.length

        # Check for English subtitles
        captions = yt.captions.get_by_language_code("en")
        if not captions:
            continue

        # Download audio
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)
        audio_stream.download(output_path=output_dir, filename=audio_filename)

        # Download subtitles
        subtitles = captions.generate_srt_captions()
        subtitles_filename = f"{uuid.uuid4()}.csv"
        subtitles_path = os.path.join(output_dir, subtitles_filename)

        # Convert subtitles to CSV with timestamps
        subtitles_list = []
        for line in subtitles.split("\n\n"):
            if not line.strip():
                continue
            idx, timestamp, text = line.split("\n")
            start_time, end_time = timestamp.split(" --> ")
            subtitles_list.append(
                {
                    "start_time": start_time.strip(),
                    "end_time": end_time.strip(),
                    "text": text.strip(),
                }
            )

        df = pd.DataFrame(subtitles_list)
        df.to_csv(subtitles_path, index=False)

        # Upload audio and subtitles to MinIO
        audio_object_key = f"text2audio/audio/{audio_filename}"
        subtitles_object_key = f"text2audio/meta/{subtitles_filename}"

        s3_client.upload_file(
            audio_path,
            MINIO_DATA_BUCKET_NAME,
            audio_object_key,
        )
        s3_client.upload_file(
            subtitles_path,
            MINIO_DATA_BUCKET_NAME,
            subtitles_object_key,
        )

        # Add metadata to CSV
        metadata_csv_path = os.path.join(output_dir, "metadata.csv")
        metadata = {
            "video_id": video_id,
            "title": title,
            "description": description,
            "length": length,
            "audio_filename": audio_filename,
            "subtitles_filename": subtitles_filename,
        }

        if not os.path.exists(metadata_csv_path):
            pd.DataFrame([metadata]).to_csv(metadata_csv_path, index=False)
        else:
            df = pd.read_csv(metadata_csv_path)
            df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
            df.to_csv(metadata_csv_path, index=False)

        # Mark video as downloaded
        downloaded_videos.add(video_id)

        # Wait before processing the next video
        time.sleep(60)  # 1-minute delay between videos


@dsl.pipeline(
    name="YouTube Audio and Subtitles Pipeline",
    description="Scrape YouTube videos, download audio and subtitles, and store in MinIO.",
)
def youtube_pipeline():
    """Kubeflow Pipeline to scrape YouTube videos and store data in MinIO."""
    output_dir = "/tmp/output"

    # Scrape and process videos
    scrape_task = scrape_youtube_videos(output_dir=output_dir)


# Compile the pipeline
pipeline_func = youtube_pipeline
pipeline_filename = pipeline_func.__dict__["component_spec"].name + ".pipeline.yaml"
kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename)

# Upload the pipeline
client = kfp.Client(host="http://k5w.ai/apis")
pipeline = client.upload_pipeline(
    pipeline_filename, pipeline_name="YouTube Audio and Subtitles Pipeline"
)
