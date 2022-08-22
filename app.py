from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "afmanKey#".encode('utf8')
app.config["SESSION_PERMANENT"] = True

