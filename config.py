from app import app
from faunadb.client import FaunaClient
from flask_socketio import SocketIO
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
