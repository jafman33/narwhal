from xml.dom.pulldom import END_ELEMENT
from app import app
from config import socketio, client, s3, os

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

from werkzeug.utils import secure_filename
from flask_socketio import join_room
from faunadb import query as q
from faunadb.objects import Ref
import re
import uuid

import myLib


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
            
            if not firstname or not lastname or not password or not email:
                flash("Please fill out the form completely.")
                return redirect(url_for('register'))
            
            else:
        
            # Todo - add check for terms and conditions
            
            # make this USER TYPE specific!
                user = client.query(
                    q.create(
                        q.collection("users"),
                        {
                            "data": {
                                "account": {
                                    "usertype": type,
                                    "firstname": firstname,
                                    "lastname": lastname,
                                    "email": email,
                                    "password": hashlib.sha512(password.encode()).hexdigest(),
                                    },
                                "profile": {
                                    "photo": "https://bidztr.s3.amazonaws.com/65463811-61ff-49d0-a714-c93369649d94-docs-avatar.png",
                                    "phone": "",
                                    "calendly": "",
                                    "headline": "",
                                    "summary": "",
                                    "industry": "",
                                    "zipcode": "",
                                    "city": "",
                                    },
                                "experience": {
                                    },
                                "education": {
                                    },
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
                    "firstname": user["data"]["account"]["firstname"],
                    "lastname": user["data"]["account"]["lastname"],
                    "email": user["data"]["account"]["email"],
                    "usertype": user["data"]["account"]["usertype"],
                    "loggedin": True,
                }
                            
                return redirect(url_for("intro"))
            
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
            
            print('trying password!...')
            print(user["data"]["account"]["password"])
            if (hashlib.sha512(password.encode()).hexdigest() == user["data"]["account"]["password"]):
                print('made it!')
                
                # Create new session for newly logged in user
                session["user"] = {
                    "id": user["ref"].id(),
                    "firstname": user["data"]["account"]["firstname"],
                    "lastname": user["data"]["account"]["lastname"],
                    "email": user["data"]["account"]["email"],
                    "usertype": user["data"]["account"]["usertype"],
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
        return render_template("pm/intro.html", user=session["user"])
    elif session["user"]['usertype'] == 'Engineering Talent':
        return render_template("talent/intro.html", user=session["user"])
    else:
        return None
    
    
@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    return render_template("common/projects.html", user=user_data)
 


@app.route("/home", methods=["GET","POST"])
@login_required
def home():
    if session["user"]['usertype'] == 'Project Manager':
        return render_template("pm/home.html", user=session["user"])
    elif session["user"]['usertype'] == 'Engineering Talent':
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        return render_template("talent/home.html", user=user_data)
    else:
      return None
  


@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    if session["user"]['usertype'] == 'Project Manager':
        return render_template("pm/profile.html", user_data=session["user"])
    elif session["user"]['usertype'] == 'Engineering Talent':
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        return render_template("talent/profile.html", user=user_data)
    else:
        return None



@app.route("/profile-edit", methods=["GET","POST"])
@login_required
def profile_edit():
    if session["user"]['usertype'] == 'Project Manager':
        # to-do...
        #
        #
        return render_template("pm/profile_edit.html", user_data=session["user"])
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        
        # get values from fauna using id... pass them to render the form pre-populated
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        
        if request.method == 'POST':            
            
            photo = request.files['file']
            # here logic to make sure you actually received a photo submission
            #
            #
            if photo.filename != '' and myLib.allowed_file(photo.filename):
                photoUrl = myLib.uploadPhotoS3(photo)
                myLib.updateProfilePhoto(photoUrl)
            
            firstname = request.form['firstname']
            lastname = request.form['lastname']  
            if firstname and lastname:                
                myLib.updateAccountName(firstname, lastname)
            
            phone = request.form['phone']
            calendly = request.form['calendly']
            if phone:              
                myLib.updateProfileContact(phone, calendly)
            
            headline = request.form['headline']
            if headline:
                myLib.updateProfileHeadline(headline)
                
            summary = request.form['summary']
            if summary:
                myLib.updateProfileSummary(summary)
                
            industry = request.form['industry']
            if industry:
                myLib.updateProfileIndustry(industry)
                
            zipcode = request.form['zipcode']
            city = request.form['city']
            if zipcode and city:
                myLib.updateProfileLocation(zipcode, city)
     
            
            if request.form['btn'] == 'Save':
                return redirect(url_for('profile_edit'))

        return render_template("talent/profile-edit.html", user = user_data)
    else:
        return None

@app.route("/experience-edit", methods=["GET","POST"])
@app.route("/experience-edit/<id>", methods=["GET","POST"])
@login_required
def experience_edit(id=None):
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if request.method == 'POST':
        
        if request.form['btn'] == 'Delete Entry':
            client.query(
                q.update(
                    q.ref(q.collection("users"), session["user"]["id"]),
                    {
                        "data": {
                            "experience": {
                                id: None,
                                },
                            }
                        },
                    )
                )
            return redirect(url_for('profile_edit'))
            
        title = request.form['title']
        type = request.form['type']  
        company = request.form['company']  
        location = request.form['location']  
        status = request.form['status']  
        start = request.form['start']  
        end = request.form['end']  
        industry = request.form['industry']  
        
        if start:
            date_time_obj = datetime.strptime(start, '%Y-%m-%d')
            start = date_time_obj.strftime("%m/%d/%Y")
        if end and end != 'Present':
            date_time_obj = datetime.strptime(end, '%Y-%m-%d')
            end = date_time_obj.strftime("%m/%d/%Y")
            
        experienceID = str(uuid.uuid4())
        if id:
            experienceID = id

        if title and type and company and location and status and start and end and industry:
            client.query(
                q.update(
                    q.ref(q.collection("users"), session["user"]["id"]),
                    {
                        "data": {
                            "experience": {
                                experienceID: {
                                    "title": title,
                                    "type": type,
                                    "company": company,
                                    "location": location,
                                    "status": status,
                                    "start": start,
                                    "end": end,
                                    "industry": industry,
                                    },
                                },
                            }
                        },
                    )
                )
        else:
            flash("You need to fill out every field")
            return redirect(url_for('experience_edit'))
        
        if request.form['btn'] == 'Save and Back':
            return redirect(url_for('profile_edit'))
        if request.form['btn'] == 'Save and Add':
            return redirect(url_for('experience_edit'))

    return render_template("talent/experience-edit.html", user = user_data, id = id)

@app.route("/education-edit", methods=["GET","POST"])
@app.route("/education-edit/<id>", methods=["GET","POST"])
@login_required
def education_edit(id=None):
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if request.method == 'POST':
        
        if request.form['btn'] == 'Delete Entry':
            client.query(
                q.update(
                    q.ref(q.collection("users"), session["user"]["id"]),
                    {
                        "data": {
                            "education": {
                                id: None,
                                },
                            }
                        },
                    )
                )
            return redirect(url_for('profile_edit'))
            
        school = request.form['school']
        degree = request.form['degree']  
        field = request.form['field']  
        status = request.form['status']  
        start = request.form['start']  
        end = request.form['end']  
        
        if start:
            date_time_obj = datetime.strptime(start, '%Y-%m-%d')
            start = date_time_obj.strftime("%m/%d/%Y")
        if end and end != 'Present':
            date_time_obj = datetime.strptime(end, '%Y-%m-%d')
            end = date_time_obj.strftime("%m/%d/%Y")
            
        educationID = str(uuid.uuid4())
        if id:
            educationID = id

        if school and degree and field and status and start and end:
            client.query(
                q.update(
                    q.ref(q.collection("users"), session["user"]["id"]),
                    {
                        "data": {
                            "education": {
                                educationID: {
                                    "school": school,
                                    "degree": degree,
                                    "field": field,
                                    "status": status,
                                    "start": start,
                                    "end": end,
                                    },
                                },
                            }
                        },
                    )
                )
        else:
            flash("You need to fill out every field")
            return redirect(url_for('education_edit'))
        
        if request.form['btn'] == 'Save and Back':
            return redirect(url_for('profile_edit'))
        if request.form['btn'] == 'Save and Add':
            return redirect(url_for('education_edit'))

    return render_template("talent/education-edit.html", user = user_data, id = id)



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

@app.route('/under-construction')
@login_required
def under_construction():
    return render_template("common/construction.html")

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
