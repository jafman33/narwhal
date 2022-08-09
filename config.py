from app import app
from faunadb.client import FaunaClient
from flask_socketio import SocketIO
from dotenv import load_dotenv
import stripe
import os

# reads key-value pairs from a .env file and can set them as environment variables
load_dotenv()

client = FaunaClient(
    secret=os.getenv("FAUNA_KEY"),
    domain="db.us.fauna.com",
    # note: Use the correct domain for your database's Region Group.
    port=443,
    scheme="https"
    )

socketio = SocketIO(app)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}

stripe.api_key = stripe_keys["secret_key"]