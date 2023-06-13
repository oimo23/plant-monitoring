import boto3
import os
import tempfile
import cv2
from datetime import datetime

def create_video(bucket_name, folder_name, video_name, frame_rate=6):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    # Retrieve the list of object summaries for the bucket
    objects = bucket.objects.filter(Prefix=folder_name)

    image_files = []
    for obj in objects:
        # Only process objects that are .jpg images
        if obj.key.endswith(".jpg"):
            # Download the image file to a temporary file
            tmp = tempfile.NamedTemporaryFile(delete=False)
            bucket.download_file(obj.key, tmp.name)
            image_files.append(tmp.name)

    if not image_files:
        print("No image files found.")
        return

    # Determine the width and height from the first image
    frame = cv2.imread(image_files[0])
    height, width, channels = frame.shape

    # Define the codec and create a VideoWriter object
    video_name_path = os.path.join('/tmp', video_name)
    video = cv2.VideoWriter(video_name_path, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, (width, height))

    for image_file in image_files:
        frame = cv2.imread(image_file)
        video.write(frame)  # Write out frame to video

    # Release everything if job is finished
    video.release()

    print(f"Video saved as {video_name}")

    # Upload the video to S3
    bucket.upload_file(video_name_path, f'{folder_name}/{video_name}')
    print(f"Video uploaded to S3 as {folder_name}/{video_name}")

def lambda_handler(event, context):
    today = datetime.now().strftime('%Y%m%d')
    folder_name = f'images/{today}'
    bucket_name = os.environ['BUCKET_NAME']
    
    create_video(bucket_name, folder_name, 'output.mp4')
