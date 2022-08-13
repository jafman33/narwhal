from app import app
from faunadb.client import FaunaClient
from flask_socketio import SocketIO
import boto3
from dotenv import load_dotenv
import os

# reads key-value pairs from a .env file and can set them as environment variables
load_dotenv()

client = FaunaClient(
    secret=os.getenv("FAUNA_KEY"),
    domain="db.us.fauna.com",
    port=443,
    scheme="https"
    )

socketio = SocketIO(app)

# Configure the required config variables for boto3.
app.config['S3_BUCKET'] = os.getenv('S3_BUCKET')
app.config['S3_KEY'] = os.getenv('S3_KEY')
app.config['S3_SECRET'] = os.getenv('S3_SECRET')

s3 = boto3.client(
    's3',
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
)
