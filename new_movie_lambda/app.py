import boto3
import json
import os

sns = boto3.client('sns')

topic_arn = os.environ['TOPIC_ARN']


def lambda_handler(event, context):
    for record in event['Records']:
        print('Stream record: ', record)

        if record['eventName'] == 'INSERT':

            movie_image_url = 'https://image.tmdb.org/t/p/original' + record['dynamodb']['NewImage']['poster_path']['S']
            movie_title = record['dynamodb']['NewImage']['title']['S']

            html_body = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <title>New Movie Release from Netflix!</title>
                  <style>
                    body, html {
                      margin: 0;
                      padding: 0;
                      font-family: Arial, sans-serif;
                      line-height: 1.6;
                    }
                    img {
                      max-width: 100%;
                      height: auto;
                    }
                    .container {
                      max-width: 600px;
                      margin: 20px auto;
                      padding: 20px;
                      background-color: #f9f9f9;
                      border: 1px solid #ddd;
                      border-radius: 8px;
                    }
                    .title {
                      font-size: 24px;
                      font-weight: bold;
                      color: #333;
                      margin-bottom: 10px;
                    }
                    .description {
                      font-size: 16px;
                      color: #666;
                      margin-bottom: 20px;
                    }
                    .button {
                      display: inline-block;
                      background-color: #e50914;
                      color: #fff;
                      text-decoration: none;
                      padding: 10px 20px;
                      border-radius: 5px;
                      font-weight: bold;
                    }
                    .footer {
                      margin-top: 20px;
                      text-align: center;
                      color: #999;
                      font-size: 12px;
                    }
                  </style>
                </head>
                <body>
                  <div style="text-align: center;">
            """ + f"""
                    <img src="{movie_image_url}" alt="New Movie Released" style="max-width: 100%; height: auto;">
                    <h2 style="color: #333;">Introducing <strong>{movie_title}</strong></h2>
                    <p style="color: #666;">Discover the latest sensation from Netflix!</p>
                    <a href="https://www.netflix.com" style="display: inline-block; background-color: #e50914; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold;">Watch Now</a>
                  </div>
                </body>
                </html>
                """

            message = {
                'Subject': {
                    'Data': 'New Movie Released: ' + movie_title
                },
                'Body': {
                    'Html': {
                        'Data': html_body
                    }
                }
            }

            params = {
                'Message': json.dumps({'default': json.dumps(message)}),
                'TopicArn': topic_arn,
                'MessageStructure': 'json'
            }
            try:
                response = sns.publish(**params)
                print("Results from sending message: ", response)
            except Exception as e:
                print(f"Unable to send message. Error: {str(e)}")

    return f"Successfully processed {len(event['Records'])} records."
