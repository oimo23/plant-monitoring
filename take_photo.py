import os
import time
from picamera import PiCamera
import boto3

def take_photo():
    if not os.path.exists('images'):
        os.makedirs('images')

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    date = time.strftime("%Y%m%d")
    img_path = f'images/{timestamp}.jpg'

    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.start_preview()
        time.sleep(2)  # Camera warm-up time
        camera.capture(img_path)
        print(f'Photo taken and saved as {img_path}')
        upload_to_s3(img_path, date)

def upload_to_s3(file_path, date):
    # name of the bucket
    BUCKET_NAME = 'plant-monitoring'

    # name of the file on S3, set as 'images/YYYYMMDD/{timestamp}.jpg'
    S3_NAME = f'images/{date}/' + os.path.basename(file_path)

    s3 = boto3.client('s3')
    s3.upload_file(file_path, BUCKET_NAME, S3_NAME)

    print(f'Uploaded {file_path} to {BUCKET_NAME}/{S3_NAME}')
    
if __name__ == '__main__':
    take_photo()
