import boto3
import requests
import json
from datetime import datetime

def lambda_handler(event, context):
    url = "https://api.line.me/v2/bot/message/push"
    access_token = os.environ['LINE_ACCESS_TOKEN']
    line_to = os.environ['LINE_TO']
    
    # Generate a presigned URL for the S3 object
    s3 = boto3.client('s3')
    today = datetime.now().strftime('%Y%m%d')
    object_name = f'images/{today}/output.mp4'
    bucket_name = os.environ['BUCKET_NAME']
    response = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': object_name},
                                        ExpiresIn=604800)  # 7 days in seconds
    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {}'.format(access_token),
    }

    # Create a Flex Message with video preview
    flex_message = {
        "type": "flex",
        "altText": "動画プレビュー",
        "contents": {
            "type": "bubble",
            "hero": {
                "type": "video",
                "url": response,
                "previewUrl": "https://example.com/video_preview.jpg", # サムネイル画像が欲しい時は正しいURLに
                "altContent": {
                    "type": "image",
                    "size": "full",
                    "aspectRatio": "16:9",
                    "aspectMode": "cover",
                    "url": "https://example.com/video_preview.jpg", # サムネイル画像が欲しい時は正しいURLに
                },
                "aspectRatio": "16:9",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "新しい動画が利用可能です",
                        "weight": "bold",
                        "size": "md",
                        "wrap": True
                    }
                ]
            }
        }
    }

    data = {
        'to': line_to,
        'messages': [flex_message],
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # check the response
    if response.status_code == 200:
        return {
            'statusCode': 200,
            'body': json.dumps('Request was successful')
        }
    else:
        return {
            'statusCode': response.status_code,
            'body': response.text  # レスポンス本文（エラーメッセージなど）を返す
        }
