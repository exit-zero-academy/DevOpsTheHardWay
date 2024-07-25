from flask import Flask
import boto3

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    return 'Hello world!'


@app.route("/list", methods=['GET'])
def list_buckets():
    s3 = boto3.client('s3')
    return s3.list_buckets()

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
