from curses import erasechar
from urllib.parse import uses_relative
from app import app
from config import (
    socketio, 
    client, 
    VAPID_PRIVATE_KEY,
    VAPID_PUBLIC_KEY,
    VAPID_CLAIM_EMAIL
)

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
    jsonify
)

from pywebpush import webpush, WebPushException
from flask_socketio import join_room
from faunadb import query as q
from faunadb.objects import Ref
import uuid

import myLib
import json


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
                if type == 'Engineering Talent':
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
                                    "sub": {
                                        "keys": {
                                            "auth": "null"
                                            },
                                        },
                                    "date": datetime.now(pytz.UTC),
                                }
                            },
                        )
                    )
                    
                    client.query(
                            q.create(
                                q.collection("applications"),
                                {
                                    "data": {
                                        "user_id": user["ref"].id(),
                                        "applications": [],
                                    }
                                },
                            )
                        )
                
                    client.query(
                        q.create(
                            q.collection("skills"),
                            {
                                "data": {
                                    "user_id": user["ref"].id(),
                                    "skills": [],
                                }
                            },
                        )
                    )
                else:
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
                                        "division": "",
                                        "zipcode": "",
                                        "city": "",
                                        },
                                    "projects": {
                                        },
                                    "experience": {
                                        },
                                    "education": {
                                        },
                                    "sub": {
                                        "keys": {
                                            "auth": "null"
                                            },
                                        },
                                    "date": datetime.now(pytz.UTC),
                                }
                            },
                        )
                    )
                
                # Create a new chat list for newly registered user
                client.query(
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
                
                # Create a new chat list for newly registered user
                client.query(
                    q.create(
                        q.collection("bookmarks"),
                        {
                            "data": {
                                "user_id": user["ref"].id(),
                                "bookmarks": [],
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
            
            if (hashlib.sha512(password.encode()).hexdigest() == user["data"]["account"]["password"]):
                
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
    
    

@app.route("/home", methods=["GET","POST"])
@login_required
def home():

    keyword = ""
    if request.method == "POST":
        keyword = request.form["keyword"]
        
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if session["user"]['usertype'] == 'Project Manager':
        
        # get all talents
        talents = []
        if (keyword != ""):
            try:
                talent_ids = client.query(
                    q.map_(
                        q.lambda_("skill", q.get(q.var("skill"))),
                        q.paginate(q.match(q.index("skill3_match_index"), keyword),size=100)
                    )      
                )["data"]
            except:
                talent_ids = []

            # filter talents
            for talent in talent_ids:
                talent_data = client.query(q.get(q.ref(q.collection("users"), talent["data"]["user_id"])))
                talents.append(talent_data)
        
        return render_template("pm/home.html", user=user_data, talents = talents, keyword=keyword)
    
    elif session["user"]['usertype'] == 'Engineering Talent':
         
               
        skills = client.query(q.get(q.match(q.index("skill_index"), user_data["ref"].id())))["data"]["skills"]
        skills_list = [list(i.values())[0] for i in skills]
        
        managers = []
        if (keyword != ""):
            managers = client.query(
                q.map_(
                    q.lambda_("project", q.get(q.var("project"))),
                    q.paginate(q.match(q.index("userType_index"), "Project Manager"),size=100)
                )      
            )["data"]
        
        return render_template("talent/home.html", user=user_data, managers = managers, skills = json.dumps(skills_list), keyword = keyword)
    else:
      return None
  


@app.route("/profile-edit", methods=["GET","POST"])
@login_required
def profile_edit():
    if session["user"]['usertype'] == 'Project Manager':
        # get values from fauna using id... pass them to render the form pre-populated
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        
        if request.method == 'POST':   
             
            photo = request.files['file']
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
                
            division = request.form['division']
            if division:
                myLib.updateProfileDivision(division)
                
            zipcode = request.form['zipcode']
            city = request.form['city']
            if zipcode and city:
                myLib.updateProfileLocation(zipcode, city)
            
            if request.form['btn'] == 'Save':
                return redirect(url_for('profile_details'))
        return render_template("pm/profile-pm-edit.html", user=user_data)
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        
        # get values from fauna using id... pass them to render the form pre-populated
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        
        if request.method == 'POST':            
            
            photo = request.files['file']
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
                
            availability = request.form['availability']
            if availability:
                myLib.updateProfileAvailability(availability)
                
            industry = request.form['industry']
            if industry:
                myLib.updateProfileIndustry(industry)
                
            zipcode = request.form['zipcode']
            city = request.form['city']
            if zipcode and city:
                myLib.updateProfileLocation(zipcode, city)
     
            
            if request.form['btn'] == 'Save':
                return redirect(url_for('profile_details'))

        return render_template("talent/profile-talent-edit.html", user = user_data)
    else:
        return None

@app.route("/add-bookmark", methods=["POST"])
@login_required
def add_bookmark():
    
    project_id  = request.args.get('project_id', None)
    # project_email  = request.args.get('project_email', None)
    # talent_id  = request.args.get('talent_id', None)
    user_id = session["user"]["id"]
    
    if session["user"]['usertype'] == 'Project Manager':
        # Todo: bookmark talent!
        return '', 204
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        
        user_bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))
        # Create current bookmark list...
        try:
            bookmark_list = [list(i.values())[0] for i in user_bookmarks["data"]["bookmarks"]]
        except:
            bookmark_list = []
        # ...and make sure new bookmark is not already on the list
        if project_id not in bookmark_list:     
            # append the project bookmark
            user_bookmarks["data"]["bookmarks"].append({"project_id": project_id})
            # Update the user's bookmark document
            client.query(
                q.update(
                    q.ref(q.collection("bookmarks"), user_bookmarks["ref"].id()),
                    {
                        "data": {
                            "bookmarks": user_bookmarks["data"]["bookmarks"]
                        }
                    },
                )
            )
            return jsonify({
            "status": "success",
            "name": "bookmark"
            })
        else:
            user_bookmarks["data"]["bookmarks"].remove({"project_id": project_id})
            client.query(
                q.update(
                    q.ref(q.collection("bookmarks"), user_bookmarks["ref"].id()),
                    {
                        "data": {
                            "bookmarks": user_bookmarks["data"]["bookmarks"]
                        }
                    },
                )
            )
            return jsonify({
            "status": "success",
            "name": "bookmark-outline"
            })
            
@app.route("/add-application", methods=["GET","POST"])
@login_required
def add_application():

    project_id  = request.args.get('project_id', None)
    project_email  = request.args.get('project_email', None)
    # talent_id  = request.args.get('talent_id', None)
    user_id = session["user"]["id"]
    
    if session["user"]['usertype'] == 'Project Manager':
        # Todo: bookmark talent!
        return '', 204
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        
        # Get user applications document
        user_applications = client.query(q.get(q.match(q.index("application_index"), user_id)))
        # Create current application list...
        try:
            application_list = [list(i.values())[0] for i in user_applications["data"]["applications"]]
        except:
            application_list = []
        # ...and make sure new bookmark is not already on the list
        if project_id not in application_list:     
            # append the project bookmark
            user_applications["data"]["applications"].append({"project_id": project_id})
            # Update the user's application document
            client.query(
                q.update(
                    q.ref(q.collection("applications"), user_applications["ref"].id()),
                    {
                        "data": {
                            "applications": user_applications["data"]["applications"]
                        }
                    },
                )
            )

            try:
                pm_data = client.query(q.get(q.match(q.index("userEmail_index"), project_email)))["data"]
                auth = pm_data["sub"]["keys"]["auth"]
                project_title = pm_data["projects"][project_id]["title"]
            except:
                auth = ''
                project_title = ''
                return '', 204

            return jsonify({
            "status": "success",
            "name": "git-branch-outline",
            "text": "Un-Apply",
            "auth": auth,
            "title": "New Applicant!",
            "body": project_title,
            })
        else:
            user_applications["data"]["applications"].remove({"project_id": project_id})
            client.query(
                q.update(
                    q.ref(q.collection("applications"), user_applications["ref"].id()),
                    {
                        "data": {
                            "applications": user_applications["data"]["applications"]
                        }
                    },
                )
            )
            return jsonify({
            "status": "success",
            "name": "git-pull-request-outline",
            "text": "Apply"            
            })
            
@app.route('/new-applicant-notification', methods=["GET","POST"])
def new_applicant_notification():
    
    json_data = request.get_json('notification_info')
    data = json_data["notification_info"]
    auth = data['auth']
    title = data['title']
    body = data['body']
   
    try:
        subscription = client.query(q.get(q.match(q.index("sub_auth_index"), auth)))["data"]["sub"]
    except:
        return '', 204
    results = trigger_push_notification(
        subscription,
        title,
        body
        )
    return jsonify({
        "status": "success",
        "result": results
    })
    


@app.route("/check-bookmark", methods=["POST"])
@login_required
def check_bookmark():

    user_id = session["user"]["id"]
    project_id  = request.args.get('project_id', None)
    # project_email  = request.args.get('project_email', None)
    # talent_id  = request.args.get('talent_id', None)
    
    if session["user"]['usertype'] == 'Project Manager':
        # Todo: bookmark talent!
        return '', 204
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        user_bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))
        try:
            bookmark_list = [list(i.values())[0] for i in user_bookmarks["data"]["bookmarks"]]
        except:
            bookmark_list = []
        if project_id not in bookmark_list:     
            return jsonify({
            "status": "success",
            "name": "bookmark-outline"
            })
        else:
            return jsonify({
            "status": "success",
            "name": "bookmark"
            })
            
@app.route("/check-application", methods=["POST"])
@login_required
def check_application():

    user_id = session["user"]["id"]
    project_id  = request.args.get('project_id', None)
    # project_email  = request.args.get('project_email', None)
    # talent_id  = request.args.get('talent_id', None)
    
    if session["user"]['usertype'] == 'Project Manager':
        # Todo: bookmark talent!
        return '', 204
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        user_applications = client.query(q.get(q.match(q.index("application_index"), user_id)))
        try:
            application_list = [list(i.values())[0] for i in user_applications["data"]["applications"]]
        except:
            application_list = []
        if project_id not in application_list:     
            return jsonify({
            "status": "success",
            "name": "git-pull-request-outline",
            "text": "Apply"
            })
        else:
            return jsonify({
            "status": "success",
            "name": "git-branch-outline",
            "text": "Un-Apply"
            })
  
@app.route("/experience-edit", methods=["GET","POST"])
@login_required
def experience_edit():
    
    id  = request.args.get('experience_id', None)
    erase  = request.args.get('erase', None)
    
    if request.method == 'POST' and erase:
        myLib.deleteItem("experience",id)
        return redirect(url_for('profile_details'))

    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if request.method == 'POST' and not erase:
            
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
            return redirect(url_for('profile_details'))
        if request.form['btn'] == 'Save and Add':
            return redirect(url_for('experience_edit'))

    return render_template("common/experience-edit.html", user = user_data, id = id)

@app.route("/education-edit", methods=["GET","POST"])
@login_required
def education_edit():
    
    id  = request.args.get('education_id', None)
    erase  = request.args.get('erase', None)
    
    if request.method == 'POST' and erase:
        myLib.deleteItem("education",id)
        return redirect(url_for('profile_details'))
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if request.method == 'POST' and not erase:
            
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
            return redirect(url_for('profile_details'))
        if request.form['btn'] == 'Save and Add':
            return redirect(url_for('education_edit'))

    return render_template("common/education-edit.html", user = user_data, id = id)

@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    user_id = session["user"]['id']
    
    # ultimately, we dont want to pull up 200k managers here... Need to be more specific
    managers = client.query(
        q.map_(
            q.lambda_("project", q.get(q.var("project"))),
            q.paginate(q.match(q.index("userType_index"), "Project Manager"),size=100)
        )      
    )["data"]
    
    
    bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))["data"]["bookmarks"]
    bookmark_list = [list(i.values())[0] for i in bookmarks]
    
    applications = client.query(q.get(q.match(q.index("application_index"), user_id)))["data"]["applications"]
    application_list = [list(i.values())[0] for i in applications]

    return render_template(
        "common/project-list.html", 
        user=user_data, 
        managers=managers, 
        bookmarks=bookmark_list, 
        applications=application_list
        )

@app.route("/project-edit", methods=["GET","POST"])
@login_required
def project_edit():
    
    id  = request.args.get('project_id', None)
    erase  = request.args.get('erase', None)
    keywords_list = []

    if request.method == 'POST' and erase:
        myLib.deleteItem("projects",id)
        return redirect(url_for('profile_details'))
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    
    projectID = str(uuid.uuid4())
    if id:
        keywords_list=myLib.getProjectKeys(user_data, id)
        projectID = id

    if request.method == 'POST':

        banner = request.files['file']
        if banner.filename != '':
            if myLib.allowed_file(banner.filename):
                bannerUrl = myLib.uploadPhotoS3(banner)
                myLib.updateProjectBanner(projectID,bannerUrl)
            else:
                flash("Invalid File Name")
         
        start = request.form['start']  
        if start:
            date_time_obj = datetime.strptime(start, '%Y-%m-%d')
            start = date_time_obj.strftime("%m/%d/%Y")
        
        end = request.form['end']  
        if end and end != 'Present':
            date_time_obj = datetime.strptime(end, '%Y-%m-%d')
            end = date_time_obj.strftime("%m/%d/%Y")
            
        sponsor = request.form['sponsor']
        title = request.form['title']  
        headline = request.form['headline']  
        link = request.form['link']
        location = request.form['location']  
        summary = request.form['summary']
        talent = request.form['talent']
        
            
        if sponsor and title and headline and link and location and summary and start and end and talent:
            client.query(
                q.update(
                    q.ref(q.collection("users"), session["user"]["id"]),
                    {
                        "data": {
                            "projects": {
                                projectID: {
                                    "sponsor": sponsor,
                                    "title": title,
                                    "headline": headline,
                                    "link": link,
                                    "location": location,
                                    "summary": summary,
                                    "start": start,
                                    "end": end,
                                    "talent": talent,
                                    "postdate": datetime.today().strftime("%m/%d/%y"),
                                    },
                                },
                            }
                        },
                    )
                )
        
        if request.form['btn'] == 'Save and Back':
            return redirect(url_for('profile_details'))
        elif request.form['btn'] == 'Save and Add':
            return redirect(url_for('project_edit'))
        else:
            return '', 204
        
    return render_template("pm/project-edit.html", user = user_data, id = id, keys=json.dumps(keywords_list))


@app.route('/add-keyword', methods=["POST"])
def add_project_keyword():
    id  = request.args.get('project_id', None)
    
    if id:
        json_data = request.get_json('keywords_info')
        keys = json_data["keywords_info"]

        # Get user skills document - user_skills document will always exist! no need to try:
        # project_keys = client.query(q.get(q.match(q.index("skill_index"), user_id)))["data"]["projects"][id]["keys"]
        updated_keys = []
        for key in keys:
            updated_keys.append({"keyword": key})
            
        myLib.updateProjectKeys(id,updated_keys)

        return jsonify({
            "status": "successfully updated database",
        })
    return jsonify({
            "status": "new project: ID has not been assigned",
        })

    
@app.route("/talent", methods=["GET", "POST"])
@login_required
def talent():
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    talents = client.query(
        q.map_(
            q.lambda_("talent", q.get(q.var("talent"))),
            q.paginate(q.match(q.index("userType_index"), "Engineering Talent"),size=100)
        )      
    )["data"]
    
    return render_template("common/talent-list.html", user=user_data, talents=talents)

@app.route("/project-details", methods=["GET", "POST"])
@login_required
def project_details():

    project_id  = request.args.get('project_id', None)
    project_email  = request.args.get('project_email', None)
    messages  = request.args.get('messages', None)
        
    project_data = client.query(q.get(q.match(q.index("userEmail_index"), project_email)))
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    
    return render_template(
        "common/project-details.html", 
        user = user_data, 
        project=project_data, 
        id = project_id, 
        email = project_email, 
        messages=messages)

@app.route('/update-skills', methods=["POST"])
def update_skills():
    email  = request.args.get('email', None)
    user_id = session["user"]["id"]

    if email:
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), email)))
        user_id = user_data["ref"].id()
    
    json_data = request.get_json('skills_info')
    skills = json_data["skills_info"]

    # Get user skills document - user_skills document will always exist! no need to try:
    user_skills = client.query(q.get(q.match(q.index("skill_index"), user_id)))
    updated_skills = []
    for skill in skills:
        updated_skills.append({"skill": skill})
        
    myLib.updateSkills(user_skills["ref"].id(),updated_skills)
    
    return jsonify({
        "status": "successfully updated database",
    })
    
@app.route("/contacts", methods=["GET","POST"])
@login_required
def contacts():
    email  = request.args.get('email', None)
    if email:
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), email)))
        user_id = user_data["ref"].id()
    else: 
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        user_id = session["user"]["id"]

    
    contacts_data = []
    try:
        # Get the chat list of all their contacts
        chat_list = client.query(q.get(q.match(q.index("chat_index"), user_id)))["data"]["chat_list"]
    except:
        chat_list = []
    for contacts in chat_list:
        # Query the database to get the user name of users in a user's chat list
        contact_data = client.query(q.get(q.ref(q.collection("users"), contacts["user_id"])))["data"]
        contacts_data.append(
            {
                "firstname": contact_data["account"]["firstname"],
                "lastname": contact_data["account"]["lastname"],
                "photo": contact_data["profile"]["photo"],
                "room_id": contacts["room_id"],
            }
        )  
        
    return render_template(
        "common/contacts.html", 
        user=user_data,
        contacts=contacts_data,
    )
    
@app.route("/profile-details", methods=["GET", "POST"])
@login_required
def profile_details():
    
    email  = request.args.get('email', None)
    if email:
        self = False
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        profile_data = client.query(q.get(q.match(q.index("userEmail_index"), email)))
        print("viewing external profile")
    else:
        self = True
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
        profile_data = user_data

    user_type = session["user"]['usertype']
    user_id = profile_data["ref"].id()
    print(user_id)
    
    contacts_data = []
    skills_list = []

    # get contacts
    try:
        chat_list = client.query(q.get(q.match(q.index("chat_index"), user_id)))["data"]["chat_list"]
    except:
        chat_list = []
    for contacts in chat_list:
        # Query the database to get the user name of users in a user's chat list
        contact_data = client.query(q.get(q.ref(q.collection("users"), contacts["user_id"])))["data"]
        contacts_data.append(
            {
                "firstname": contact_data["account"]["firstname"],
                "lastname": contact_data["account"]["lastname"],
                "email": contact_data["account"]["email"],
                "photo": contact_data["profile"]["photo"],
                "room_id": contacts["room_id"],
            }
        )  
        
    if user_type == 'Project Manager':
        if self:
            return render_template("pm/profile-pm-self.html", type=user_type, user=user_data, profile=profile_data, contacts = contacts_data)
        elif (not self and profile_data["data"]["account"]["usertype"] == 'Project Manager'):
            return render_template("pm/profile-pm.html", type=user_type, user=user_data, profile=profile_data, contacts = contacts_data)
        else:
            skills_list=myLib.getSkills(user_id)
            return render_template("talent/profile-talent.html", type=user_type, user=user_data, profile=profile_data, contacts = contacts_data, skills = json.dumps(skills_list))
    
    elif user_type == 'Engineering Talent':
        if self:
            skills_list=myLib.getSkills(user_id)
            return render_template("talent/profile-talent-self.html", type=user_type, user=user_data, profile=profile_data, contacts = contacts_data, skills = json.dumps(skills_list))
        elif (not self and profile_data["data"]["account"]["usertype"] == 'Engineering Talent'):
            skills_list=myLib.getSkills(user_id)
            return render_template("talent/profile-talent.html", type=user_type, user=user_data, profile=profile_data, contacts = contacts_data, skills = json.dumps(skills_list))
        else:
            return render_template("pm/profile-pm.html", type=user_type, user=user_data, profile=profile_data, contacts = contacts_data)
        
    else:
      return None
    


    
    



@app.route("/calendly/<user_email>", methods=["GET","POST"])
@login_required
def schedule(user_email):
    
    try:
        user_data = client.query(q.get(q.match(q.index("userEmail_index"), user_email)))
    except:
        return 'user does not have calendly setup'

    return render_template("common/calendly.html", user=user_data, self = session)



@app.route("/new-contact", methods=["POST"])
@login_required
def new_contact():
    
    user_id = session["user"]["id"]
    new_contact = request.form["email"].strip().lower()
    
    # If user is trying to add their self, do nothing
    if new_contact == session["user"]["email"]:
        # print('cant contact yourself!')
        return redirect(url_for("contacts"))

    # If user tries to add an email which has not been registerd...
    try:
        new_contact_id = client.query(q.get(q.match(q.index("userEmail_index"), new_contact)))
        # print('contact added')
    except:
        # need to alert here that contact was not found!
        # currenlty just refreshes
        # print('contact not found')
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

@app.route("/save-project", methods=["POST"])
@login_required
def save_project():
# 
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
            contact_data = client.query(q.get(q.ref(q.collection("users"), chats["user_id"])))
            # Try to get the last message for the room
            try:
                last_message = client.query(q.get(q.match(q.index("message_index"), chats["room_id"])))["data"]["conversation"][-1]["message"]
            except:
                last_message = "This place is empty. No messages ..."
            
            data.append(
                {
                    "name": contact_data["data"]["account"]["firstname"],
                    "room_id": room_id,
                    "is_active": True,
                    "last_message": last_message,
                }
            )
             

    return render_template(
        "common/chat.html",
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
    sender_name = json["sender_name"]

    messages = client.query(q.get(q.match(q.index("message_index"), room_id)))
    conversation = messages["data"]["conversation"]
    conversation.append(
        {
            "timestamp": timestamp,
            "sender_name": sender_name,
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
    return app.send_static_file('service-worker.js')


#  SUBSCRIPTIONS
@app.route('/api/subscribe', methods=["POST"])
def subscribe():

    json_data = request.get_json('subscription_info')
    subscription_json = json.loads(json_data['subscription_json'])
    auth = subscription_json["keys"]["auth"]

    try:
        client.query(q.get(q.match(q.index("sub_auth_index"), auth)))
        print("Found Authorization on database...")
    except:
        print("Creating NEW Authorization on database")
        client.query(
                q.update(
                    q.ref(q.collection("users"), session["user"]["id"]),
                    {
                        "data": {
                            "sub": subscription_json,
                            }
                        },
                    )
                )

    return '', 204

# remove the sub key if unsubscribed
@app.route('/api/unsubscribe', methods=["POST"])
def unsubscribe():

    try:
        client.query(
            q.update(
                q.ref(q.collection("users"), session["user"]["id"]),
                {
                    "data": {
                        "sub": {
                            "keys": {
                                "auth": "null"
                                },
                            },
                        }
                    },
                )
            )
        
        print("Subscription Removed!")
    except:
        print("Fauna could not find push subscription for this user")
    return '', 204

@app.route('/api/test', methods=["POST"])
def api_test():
    
    json_data = request.get_json('subscription_info')
    subscription_json = json.loads(json_data['subscription_json'])
    auth = subscription_json["keys"]["auth"]
    
    try:
        subQ = client.query(q.get(q.match(q.index("sub_auth_index"), auth)))
        subscription = subQ["data"]["sub"]
        print("Found Authorization on database. Sending push!")
    except:
        print("----------------------------------")
        print("NOTE: did NOT find authorization for this user. PLEASE AUTHORIZE NOTIFICATIONS")
        print("----------------------------------")
        return '', 204
        
    myTitle = "Congratulations!"
    myBody = "You are now subscribed to notifications from Narwhal"
        
    results = trigger_push_notification(
        subscription,
        myTitle,
        myBody
        )
    return jsonify({
        "status": "success",
        "result": results
    })
    

    
@app.route('/api/notify', methods=["POST"])
def notify():
    # mass notification to all subscriptoins
    
    
    try:
        subscriptions = client.query(
            q.map_(
                q.lambda_("x", q.get(q.var("x"))),
                q.paginate(q.match(q.index("sub_auth_index"), "null"),size=999)
            )      
        )["data"]
    except:
        print("Fauna returned some errors")
    
    myTitle = "My Title"
    myBody = "My Body"
 
    results = trigger_push_notifications_for_subscriptions(
        subscriptions,
        myTitle,
        myBody,
    )

    return jsonify({
        "status": "success",
        "result": results
    })

def trigger_push_notification(sub, title, body):
    
    try:
        response = webpush(
            subscription_info=sub,
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": "mailto:{}".format(VAPID_CLAIM_EMAIL)
            }
        )
        return response.ok
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                extra.code,
                extra.errno,
                extra.message
            )
        print(ex)
        return False

# loop through all subscirptions and send all the clients a push notification
def trigger_push_notifications_for_subscriptions(subscriptions, title, body):
    return [trigger_push_notification(subscription["data"]["sub"], title, body)
            for subscription in subscriptions]
    
@app.route("/publicVapidKey")
def get_public_key():
    publicVapidKey = {"publicVapidKey": VAPID_PUBLIC_KEY}
    return jsonify(publicVapidKey)

# @app.route('/manifest.json')
# def manifest():
#     return app.send_from_directory('static', 'manifest.json')

if __name__ == "__main__":
    socketio.run(app, debug=True)


