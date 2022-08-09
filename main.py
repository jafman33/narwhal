from app import app
from config import socketio, client

import hashlib
from functools import wraps
from datetime import datetime
import pytz

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    make_response, 
    send_from_directory
)

from flask_socketio import join_room
from faunadb import query as q
from faunadb.objects import Ref
import re


# Login decorator to ensure user is logged in before accessing certain routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# Index route, this route redirects to login/register page
@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("login"))


# Register a new user and hash password
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        # To setup validator for email
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        type = request.form["type"] 
        
        # Make sure no ther user with similar credentials is already registered
        try:
            user = client.query(q.get(q.match(q.index("userEmail_index"), email)))
            if user:
                flash("Email already exists.")
                return redirect(url_for('register'))
        
        except:
            
            if not firstname or not lastname or not password or not email or not password:
                flash("Please fill out the form completely.")
                return redirect(url_for('register'))
            
            else:
        
            # Todo - add check for terms and conditions
                user = client.query(
                    q.create(
                        q.collection("users"),
                        {
                            "data": {
                                "usertype": type,
                                "firstname": firstname,
                                "lastname": lastname,
                                "email": email,
                                "password": hashlib.sha512(password.encode()).hexdigest(),
                                "date": datetime.now(pytz.UTC),
                            }
                        },
                    )
                )
                
                # Create a new chat list for newly registered userß
                chat = client.query(
                    q.create(
                        q.collection("chats"),
                        {
                            "data": {
                                "user_id": user["ref"].id(),
                                "chat_list": [],
                            }
                        },
                    )
                )
                
                # Create new session for newly logged in user
                session["user"] = {
                    "id": user["ref"].id(),
                    "firstname": user["data"]["firstname"],
                    "lastname": user["data"]["lastname"],
                    "email": user["data"]["email"],
                    "usertype": user["data"]["usertype"],
                    "loggedin": True,
                }
                            
                return redirect(url_for("about"))
            
    return render_template("common/register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        # To add email validator here
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        try:
            # Query the data base for the inputed email address
            user = client.query(q.get(q.match(q.index("userEmail_index"), email)))

            if (hashlib.sha512(password.encode()).hexdigest() == user["data"]["password"]):
                
                # Create new session for newly logged in user
                session["user"] = {
                    "id": user["ref"].id(),
                    "firstname": user["data"]["firstname"],
                    "lastname": user["data"]["lastname"],
                    "email": user["data"]["email"],
                    "usertype": user["data"]["usertype"],
                    "loggedin": True,
                }
                            
                return redirect(url_for("home"))
        
            else:
                raise Exception()
        except Exception as e:
            flash("Invalid credentials, please try again!")
            return redirect(url_for("login"))
    return render_template("common/login.html")



# Register a new user and hash password
@app.route("/intro", methods=["GET", "POST"])
@login_required
def intro():
    if session["user"]['usertype'] == 'Project Manager':
        return render_template("pm/intro.html", user_data=session["user"])
    elif session["user"]['usertype'] == 'Engineering Talent':
        return render_template("talent/intro.html", user_data=session["user"])
    else:
        return None

@app.route("/home", methods=["GET","POST"])
@login_required
def home():
    if session["user"]['usertype'] == 'Project Manager':
        return render_template("pm/home.html", user_data=session["user"])
    elif session["user"]['usertype'] == 'Engineering Talent':
        return render_template("talent/home.html", user_data=session["user"])
    else:
      return None

@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    if session["user"]['usertype'] == 'Project Manager':
        return render_template("pm/profile.html", user_data=session["user"])
    elif session["user"]['usertype'] == 'Engineering Talent':
        return render_template("talent/profile.html", user_data=session["user"])
    else:
        return None


@app.route("/contacts", methods=["GET","POST"])
@login_required
def contacts():

    # Initialize context that contains information about the chat room
    data = []
    try:
        # Get the chat list of all their contacts
        chat_list = client.query(q.get(q.match(q.index("chat_index"), session["user"]["id"])))["data"]["chat_list"]
    except:
        chat_list = []

    for contacts in chat_list:
        # Query the database to get the user name of users in a user's chat list
        contact = client.query(q.get(q.ref(q.collection("users"), contacts["user_id"])))["data"]["username"]

        data.append(
            {
                "username": contact,
                "room_id": contacts["room_id"],
            }
        )
        
    return render_template(
        "contacts.html", 
        user_data=session["user"],
        data=data,
    )


@app.route("/new-contact", methods=["POST"])
@login_required
def new_contact():
    
    user_id = session["user"]["id"]
    new_contact = request.form["email"].strip().lower()

    # If user is trying to add their self, do nothing
    if new_contact == session["user"]["email"]:
        return redirect(url_for("contacts"))

    # If user tries to add an email which has not been registerd...
    try:
        new_contact_id = client.query(q.get(q.match(q.index("user_index"), new_contact)))
    except:
        # need to alert here that nothing was found
        # currenlty just refreshes
        return redirect(url_for("contacts"))
    
    # Get the chats | related to both users
    chats = client.query(q.get(q.match(q.index("chat_index"), user_id)))
    recepient_chats = client.query(q.get(q.match(q.index("chat_index"), new_contact_id["ref"].id())))
    
    # Check if the chat the user is trying to add has not been added before
    try:
        chat_list = [list(i.values())[0] for i in chats["data"]["chat_list"]]
    except:
        chat_list = []

    if new_contact_id["ref"].id() not in chat_list:
        
        # Append the new chat to the chat list of the user
        room_id = str(int(new_contact_id["ref"].id()) + int(user_id))[-4:]
        chats["data"]["chat_list"].append({
                "user_id": new_contact_id["ref"].id(), 
                "room_id": room_id
            }
        )
        recepient_chats["data"]["chat_list"].append({
            "user_id": user_id, "room_id": room_id
            }
        )

        # Update chat list for both users
        client.query(
            q.update(
                q.ref(q.collection("chats"), chats["ref"].id()),
                {
                    "data": {
                        "chat_list": chats["data"]["chat_list"]
                    }
                },
            )
        )
        client.query(
            q.update(
                q.ref(q.collection("chats"), recepient_chats["ref"].id()),
                {
                    "data": {
                        "chat_list": recepient_chats["data"]["chat_list"]
                    }
                },
            )
        )
        client.query(
            q.create(
                q.collection("messages"),
                {
                    "data": {
                        "room_id": room_id, "conversation": []
                    }
                },
            )
        )

    return redirect(url_for("contacts"))


@app.route("/text", methods=["GET","POST"])
@login_required
def text():
        # Get the room id in the url or set to None
    room_id = request.args.get("rid", None)
    # Initialize context that contains information about the chat room
    data = []
    messages = []

    try:
        # Get the chat list for the user in the room i.e all of the people they have a chat histor with on the application
        chat_list = client.query(q.get(q.match(q.index("chat_index"), session["user"]["id"])))["data"]["chat_list"]
    except:
        chat_list = []

    for chats in chat_list:
        if room_id == chats["room_id"]:
            # Get all the message history 
            messages = client.query(q.get(q.match(q.index("message_index"), room_id)))["data"]["conversation"]
            # Get our contact's name
            contact = client.query(q.get(q.ref(q.collection("users"), chats["user_id"])))["data"]["username"]
            # Try to get the last message for the room
            try:
                last_message = client.query(q.get(q.match(q.index("message_index"), chats["room_id"])))["data"]["conversation"][-1]["message"]
            except:
                last_message = "This place is empty. No messages ..."
            
            data.append(
                {
                    "username": contact,
                    "room_id": room_id,
                    "is_active": True,
                    "last_message": last_message,
                }
            )
             

    return render_template(
        "chat.html",
        user_data=session["user"],
        room_id=room_id,
        data=data,
        messages=messages,
    )

# Custom time filter to be used in the jinja template
@app.template_filter("ftime")
def ftime(date):
    return datetime.fromtimestamp(int(date)).strftime("%I:%M %p")
    # return datetime.fromtimestamp(int(date)).strftime("%b %-d at %I:%M %p")

# Join-chat event. Emit online message to ther users and join the room
@socketio.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    join_room(room=room)
    socketio.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
        # include_self=False,
    )

# Outgoing event handler
@socketio.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    room_id = json["rid"]
    timestamp = json["timestamp"]
    message = json["message"]
    sender_id = json["sender_id"]
    sender_username = json["sender_username"]

    messages = client.query(q.get(q.match(q.index("message_index"), room_id)))
    conversation = messages["data"]["conversation"]
    conversation.append(
        {
            "timestamp": timestamp,
            "sender_username": sender_username,
            "sender_id": sender_id,
            "message": message,
        }
    )
    # Updated the database with the new message
    client.query(
        q.update(
            q.ref(q.collection("messages"), messages["ref"].id()),
            {"data": {"conversation": conversation}},
        )
    )
    # Emit the message(s) sent to other users in the room
    socketio.emit(
        "message",
        json,
        room=room_id,
        include_self=False,
    )
    
    
# Register a new user and hash password
@app.route("/terms", methods=["GET"])
def terms():
    return render_template("common/terms.html")

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/service-worker.js')
def sw():
    response = make_response(
        send_from_directory(
            'templates',
            path='service-worker.js'
        )
    )
    response.headers['Content-Type'] = 'application/javascript'
    # response.headers['Cache-Control'] = 'no-cache'
    return response



if __name__ == "__main__":
    socketio.run(app,debug=True)
