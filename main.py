from curses import erasechar
from platform import python_branch
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

import myLib
import json

# Decorator to ensure login before routing
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("login"))

# Register a new user and hash password
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        type = request.form["type"] 
        
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
                user = myLib.newUserDoc(
                    type, firstname, lastname,email, 
                    hashlib.sha512(password.encode()).hexdigest(),
                    datetime.now(pytz.UTC)
                )
                myLib.newCollectionDoc("bookmarks",user["ref"].id())
                myLib.newCollectionDoc("contacts",user["ref"].id())
                
                if type == 'Engineering Talent': 
                    myLib.newCollectionDoc("applications",user["ref"].id())
                    myLib.newCollectionDoc("skills",user["ref"].id())
                    
                myLib.createSession(user)
                return redirect(url_for("intro"))
            
    return render_template("common/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        try:
            user = client.query(q.get(q.match(q.index("userEmail_index"), email)))
            if (hashlib.sha512(password.encode()).hexdigest() == user["data"]["account"]["password"]):
                myLib.createSession(user)   
                return redirect(url_for("home"))
            else:
                raise Exception()
        except Exception as e:
            flash("Invalid credentials, please try again!")
            return redirect(url_for("login"))
    return render_template("common/login.html")


@app.route("/intro", methods=["GET", "POST"])
@login_required
def intro():
    if session["user"]['usertype'] == 'Program Manager':
        return render_template("pm/intro.html", user=session["user"])
    if session["user"]['usertype'] == 'Engineering Talent':
        return render_template("talent/intro.html", user=session["user"])
    
@app.route("/notifications", methods=["GET", "POST"])
@login_required
def notifications():
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    # pull user notifications
    

    return render_template("common/notifications.html", user=user_data, notifications_active = "active")

@app.route("/project-applicants", methods=["GET", "POST"])
@login_required
def project_applicants():
    applicants_data = []
    project_id  = request.args.get('project_id', None)
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    #create applicants list (same as contacts) 
    try:
        applicant_list = myLib.getApplicants_byProject(project_id)
    except:
        applicant_list = []
    for applicant in applicant_list:
        applicant_data = client.query(q.get(q.ref(q.collection("users"), applicant["ref"].id() )))["data"]
        applicants_data.append(
            {
                "firstname": applicant_data["account"]["firstname"],
                "lastname": applicant_data["account"]["lastname"],
                "email": applicant_data["account"]["email"],
                "photo": applicant_data["profile"]["photo"],
            }
        )

    return render_template("pm/applicants.html", user=user_data, applicants = applicants_data)


@app.route("/home", methods=["GET","POST"])
@login_required
def home():
    from_intro  = request.args.get('flag', None)

    keyword = ""
    if request.method == "POST":
        keyword = request.form["keyword"]
    user_id = session["user"]['id']
    count_dict = {}
        
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    user_experiencesNo = myLib.getDocsCount("experience","experience_index",user_id)
    user_educationsNo = myLib.getDocsCount("education","education_index",user_id)
    count_dict.update({"experiences":  user_experiencesNo})
    count_dict.update({"educations":  user_educationsNo})

    if session["user"]['usertype'] == 'Program Manager':
        user_projectsNo = myLib.getDocsCount("project","project_index",user_id)
        count_dict.update({"projects":  user_projectsNo})

        talents_matched = myLib.getTalents_byKey(keyword) 
        
        return render_template(
            "pm/home.html",
            user=user_data,
            counter = json.dumps(count_dict),
            talents = talents_matched, 
            keyword=keyword,
            flag = from_intro,
            home_active = "active"
            )
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        
        try:
            skills = client.query(q.get(q.match(q.index("skill_index"), user_data["ref"].id())))["data"]["skills"]
            skills_list = [list(i.values())[0] for i in skills]
        except:
            skills_list = []
        
        projects_matched = myLib.getProjects_byKey(keyword)
 
        return render_template(
            "talent/home.html", 
            user=user_data,
            counter = json.dumps(count_dict),
            projects = projects_matched,
            skills = json.dumps(skills_list), 
            keyword = keyword,
            flag = from_intro,
            home_active = "active"
            )
    else:
      return None
  


@app.route("/profile-edit", methods=["GET","POST"])
@login_required
def profile_edit():
    account_payload = {}
    profile_payload = {}
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if session["user"]['usertype'] == 'Program Manager':
        if request.method == 'POST':   
            
            photo = request.files['file']
            if photo.filename != '' and myLib.allowed_file(photo.filename):
                photoUrl = myLib.uploadPhotoS3(photo)
                profile_payload.update({"photo": photoUrl})
            
            firstname = request.form['firstname']
            lastname = request.form['lastname']  
            phone = request.form['phone']
            calendly = request.form['calendly']
            headline = request.form['headline']
            summary = request.form['summary']
            division = request.form['division']
            zipcode = request.form['zipcode']
            city = request.form['city']
            
            account_payload.update({"firstname": firstname})
            account_payload.update({"lastname": lastname})
            
            profile_payload.update({"phone": phone})
            profile_payload.update({"calendly": calendly})
            profile_payload.update({"headline": headline})
            profile_payload.update({"summary": summary})
            profile_payload.update({"division": division})
            profile_payload.update({"zipcode": zipcode})
            profile_payload.update({"city": city})
                    
            myLib.updateProfile(account_payload,profile_payload)  
                
            if request.form['btn'] == 'Save':
                return redirect(url_for('profile_details'))

        return render_template("pm/profile-pm-edit.html", user=user_data)
    
    elif session["user"]['usertype'] == 'Engineering Talent':   
        if request.method == 'POST':            
            
            photo = request.files['file']
            if photo.filename != '' and myLib.allowed_file(photo.filename):
                photoUrl = myLib.uploadPhotoS3(photo)
                profile_payload.update({"photo": photoUrl})
            
            firstname = request.form['firstname']
            lastname = request.form['lastname']  
            phone = request.form['phone']
            calendly = request.form['calendly']
            headline = request.form['headline']
            summary = request.form['summary']  
            availability = request.form['availability']
            industry = request.form['industry']
            zipcode = request.form['zipcode']
            city = request.form['city']
            
            account_payload.update({"firstname": firstname})
            account_payload.update({"lastname": lastname})
            
            profile_payload.update({"phone": phone})
            profile_payload.update({"calendly": calendly})
            profile_payload.update({"headline": headline})
            profile_payload.update({"summary": summary})
            profile_payload.update({"availability": availability})
            profile_payload.update({"industry": industry})
            profile_payload.update({"zipcode": zipcode})
            profile_payload.update({"city": city})
            
            myLib.updateProfile(account_payload,profile_payload)  

            if request.form['btn'] == 'Save':
                return redirect(url_for('profile_details'))

        return render_template("talent/profile-talent-edit.html", user = user_data)

@app.route("/check-bookmark", methods=["POST"])
@login_required
def check_bookmark():

    user_id = session["user"]["id"]
    project_id  = request.args.get('project_id', None)
    talent_id  = request.args.get('talent_id', None)
    
    if session["user"]['usertype'] == 'Program Manager':
        try:
            user_bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))
            bookmark_list = [list(i.values())[0] for i in user_bookmarks["data"]["bookmarks"]]
        except:
            bookmark_list = []
        if talent_id not in bookmark_list:
            return jsonify({"status": "success","name": "bookmark-outline"})
        else:
            return jsonify({"status": "success","name": "bookmark"})
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        try:
            user_bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))
            bookmark_list = [list(i.values())[0] for i in user_bookmarks["data"]["bookmarks"]]
        except:
            bookmark_list = []
        if project_id not in bookmark_list:     
            return jsonify({"status": "success","name": "bookmark-outline"})
        else:
            return jsonify({"status": "success","name": "bookmark"})

@app.route("/add-bookmark", methods=["POST"])
@login_required
def add_bookmark():
    
    project_id  = request.args.get('project_id', None)
    user_id  = request.args.get('user_id', None)
    
    if session["user"]['usertype'] == 'Program Manager':
        try:
            user_bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), session["user"]["id"])))
            bookmark_list = [list(i.values())[0] for i in user_bookmarks["data"]["bookmarks"]]
        except:
            bookmark_list = []
        if user_id not in bookmark_list:     
            user_bookmarks["data"]["bookmarks"].append({"user_id": user_id})
            myLib.updateUserBookmarks(user_bookmarks["ref"].id(),user_bookmarks["data"]["bookmarks"])
            return jsonify({"status": "success","name": "bookmark"})
        else:
            user_bookmarks["data"]["bookmarks"].remove({"user_id": user_id})
            myLib.updateUserBookmarks(user_bookmarks["ref"].id(),user_bookmarks["data"]["bookmarks"])
            return jsonify({"status": "success","name": "bookmark-outline"})
    
    elif session["user"]['usertype'] == 'Engineering Talent':
        try:
            user_bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), session["user"]["id"])))
            bookmark_list = [list(i.values())[0] for i in user_bookmarks["data"]["bookmarks"]]
        except:
            bookmark_list = []
        if project_id not in bookmark_list:     
            user_bookmarks["data"]["bookmarks"].append({"project_id": project_id})
            myLib.updateUserBookmarks(user_bookmarks["ref"].id(),user_bookmarks["data"]["bookmarks"])
            return jsonify({"status": "success","name": "bookmark"})
        else:
            user_bookmarks["data"]["bookmarks"].remove({"project_id": project_id})
            myLib.updateUserBookmarks(user_bookmarks["ref"].id(),user_bookmarks["data"]["bookmarks"])
            return jsonify({"status": "success","name": "bookmark-outline"})
            
@app.route("/add-application", methods=["GET","POST"])
@login_required
def add_application():

    project_id  = request.args.get('project_id', None)
    project_email  = request.args.get('project_email', None)
    user_id = session["user"]["id"]
    
    if session["user"]['usertype'] == 'Engineering Talent':
        try:
            user_applications = client.query(q.get(q.match(q.index("application_index"), user_id)))
            application_list = [list(i.values())[0] for i in user_applications["data"]["applications"]]
        except:
            application_list = []
            
        if project_id not in application_list:     
            user_applications["data"]["applications"].append({"project_id": project_id})
            myLib.updateUserApplications(user_applications["ref"].id(),user_applications["data"]["applications"])

            try:
                auth = client.query(q.get(q.match(q.index("userEmail_index"), project_email)))["data"]["sub"]["keys"]["auth"]
                project_title = client.query(q.get(q.ref(q.collection("projects"), project_id)))["data"]["project"]["title"]
                return jsonify({
                    "status": "success",
                    "name": "git-branch-outline",
                    "text": "Un-Apply",
                    "auth": auth,
                    "title": "New Applicant!",
                    "body": project_title,
                })
            except:
                print("[Warning]: Manager has not allowed push notifications")
                return '', 204

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
    
    if (auth != "null"):
        try:
            subscription = client.query(q.get(q.match(q.index("sub_auth_index"), auth)))["data"]["sub"]
            
            results = trigger_push_notification(subscription,title,body)
            return jsonify({
                "status": "success",
                "result": results
            })
        except:
            print("[Error]: new_application_notification()")
            return '', 204
        

@app.route('/new-skill-notification', methods=["GET","POST"])
def new_skill_notification():
    
    json_data = request.get_json('skill_info')
    data = json_data["skill_info"]
    skill = data['skill']
    talent_name = data['talent_name']
    
    # find match with project
    try: 
        projects_matched = myLib.getProjects_byKey(skill)
    except: 
        return '[new_skill_notification()][Message:] No matches found', 204
        
    # for loop 
    for doc in projects_matched:
        # get project titles and owner's id
        project_title = doc["data"]["project"]["title"]
        project_owner_id = doc["data"]["user_id"]
        # pull project owner info
        project_owner_subscription = client.query(q.get(q.ref(q.collection("users"), project_owner_id)))["data"]["sub"]
        
        title = "New skill match for " + project_title + "!"
        body = "The skill '" + skill + "' has been added by " + talent_name + "."
        # link to pablos profile...
        
        try:             
            results = trigger_push_notification(project_owner_subscription,title,body)
            return jsonify({
                "status": "success",
                "result": results
            })
        except:
            return '[new_skill_notification()][Message:] No Authorization found for user: ' +  project_owner_id, 204


            
@app.route("/check-application", methods=["POST"])
@login_required
def check_application():

    user_id = session["user"]["id"]
    project_id  = request.args.get('project_id', None)
    
    if session["user"]['usertype'] == 'Engineering Talent':
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
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    id  = request.args.get('experience_id', None)
    erase  = request.args.get('erase', None)
    experience_data = []
    payload = {}
    
    if not id:
        experience_data = myLib.newExperiencesDoc()
        id = experience_data["ref"].id()
    else:
        experience_data = client.query(q.get(q.ref(q.collection("experiences"), id)))
        
    if request.method == 'POST' and erase:
        myLib.deleteItem("experiences",id)
        return redirect(url_for('profile_details'))

    if request.method == 'POST' and not erase:    
        start = request.form['start']
        if start:
            date_time_obj = datetime.strptime(start, '%Y-%m-%d')
            start = date_time_obj.strftime("%m/%d/%Y")
            payload.update({"start": start})
        end = request.form['end']
        if end and end != 'Present':
            date_time_obj = datetime.strptime(end, '%Y-%m-%d')
            end = date_time_obj.strftime("%m/%d/%Y")
            payload.update({"end": end})
            
        title = request.form['title']
        type = request.form['type']  
        company = request.form['company']  
        location = request.form['location']  
        status = request.form['status']  
        industry = request.form['industry']  

        payload.update({"title": title})
        payload.update({"type": type})
        payload.update({"company": company})
        payload.update({"location": location})
        payload.update({"status": status})
        payload.update({"industry": industry})
        myLib.updateExperienceDocument(id,payload)      
        
        if request.form['btn'] == 'Save and Back':
            return redirect(url_for('profile_details'))
        if request.form['btn'] == 'Save and Add':
            return redirect(url_for('experience_edit'))

    return render_template("common/experience-edit.html", user = user_data, experience = experience_data, id = id)

@app.route("/education-edit", methods=["GET","POST"])
@login_required
def education_edit():
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    id  = request.args.get('education_id', None)
    erase  = request.args.get('erase', None)
    education_data = []
    payload = {}

    if not id:
        education_data = myLib.newEducationsDoc()
        id = education_data["ref"].id()
    else:
        education_data = client.query(q.get(q.ref(q.collection("educations"), id)))
        
    if request.method == 'POST' and erase:
        myLib.deleteItem("educations",id)
        return redirect(url_for('profile_details'))

    if request.method == 'POST' and not erase:
                
        start = request.form['start']
        if start:
            date_time_obj = datetime.strptime(start, '%Y-%m-%d')
            start = date_time_obj.strftime("%m/%d/%Y")
            payload.update({"start": start})
            
        end = request.form['end']
        if end and end != 'Present':
            date_time_obj = datetime.strptime(end, '%Y-%m-%d')
            end = date_time_obj.strftime("%m/%d/%Y")
            payload.update({"end": end})
            
        school = request.form['school']
        degree = request.form['degree']  
        field = request.form['field']  
        status = request.form['status']  

        payload.update({"school": school})
        payload.update({"degree": degree})
        payload.update({"field": field})
        payload.update({"status": status})
        myLib.updateEducationDocument(id,payload)      
        
        if request.form['btn'] == 'Save and Back':
            return redirect(url_for('profile_details'))
        if request.form['btn'] == 'Save and Add':
            return redirect(url_for('education_edit'))

    return render_template("common/education-edit.html", user = user_data, education = education_data, id = id)

@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    user_id = session["user"]['id']
    
    projects_all = myLib.getCollection("project","projects")
    
    try:
        bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))["data"]["bookmarks"]
        bookmark_list = [list(i.values())[0] for i in bookmarks]
    except:
        bookmark_list = []
    projects_bookmarked = [
        client.query(q.get(q.ref(q.collection("projects"), project_id))
            ) for project_id in bookmark_list
    ]

    try:
        applications = client.query(q.get(q.match(q.index("application_index"), user_id)))["data"]["applications"]
        application_list = [list(i.values())[0] for i in applications]
    except:
        application_list = []
    projects_applied = [
        client.query(q.get(q.ref(q.collection("projects"), project_id))
            ) for project_id in application_list
    ]
    
    try:
        skills = client.query(q.get(q.match(q.index("skill_index"), user_id)))["data"]["skills"]
        skills_list = [list(i.values())[0] for i in skills]
    except:
        skills_list = []
    matched_projects = myLib.getMatches_byList("project_keyword_index", skills_list)

    return render_template(
        "common/project-list.html", 
        user=user_data, 
        projects=projects_all, 
        bookmarks=projects_bookmarked, 
        applications=projects_applied, 
        matches=matched_projects,
        projects_active="active"
        )
    
@app.route("/project-details", methods=["GET", "POST"])
@login_required
def project_details():
    project_id  = request.args.get('project_id', None)
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    project = client.query(q.get(q.ref(q.collection("projects"), project_id)))
    project_data = project["data"]["project"]

    if session["user"]['usertype'] == 'Engineering Talent':
        owner_data = client.query(q.get(q.ref(q.collection("users"), project["data"]["user_id"])))
        return render_template(
            "common/project-details.html", 
            user = user_data, 
            project=project_data, 
            manager=owner_data,
            id = project_id
            )
    
    if session["user"]['usertype'] == 'Program Manager':
        owner_data = user_data
        return render_template(
            "pm/project-details-pm.html", 
            user = user_data, 
            project=project_data, 
            manager=owner_data,
            id = project_id
            )

    
@app.route("/talent", methods=["GET", "POST"])
@login_required
def talent():
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    user_id = session["user"]["id"]

    talents_all = myLib.getDocs("talent","user_type_index","Engineering Talent")
    user_projects = myLib.getDocs("project","project_index",user_id)
    
    # Find matches
    project_keywords= []
    for item in user_projects:
        for key in item["data"]["project"]["keywords"]:
            project_keywords.append(key["keyword"])
    try:
        matched_docs = myLib.getMatches_byList("skill_match_index", project_keywords)
    except:
        matched_docs = []
    talents_matched = [
        client.query(q.get(q.ref(q.collection("users"), doc["data"]["user_id"] ))
            ) for doc in matched_docs
    ]
                
    # Query User's Bookmarks
    try:
        bookmarks = client.query(q.get(q.match(q.index("bookmark_index"), user_id)))["data"]["bookmarks"]
        bookmark_list = [list(i.values())[0] for i in bookmarks]
    except:
        bookmark_list = []
    talents_bookmarked = [
        client.query(q.get(q.ref(q.collection("users"), user_id ))
            ) for user_id in bookmark_list
    ]

    return render_template(
        "common/talent-list.html", 
        user=user_data, 
        talents=talents_all, 
        matches=talents_matched,
        bookmarks=talents_bookmarked,
        talent_active="active"
        )

@app.route("/project-edit", methods=["GET","POST"])
@login_required
def project_edit():
    
    id  = request.args.get('project_id', None)
    erase  = request.args.get('erase', None)
    date = datetime.today().strftime("%m/%d/%y")
    keyword_list = []
    project_data = []
    payload = {}
    
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))

    if not id:
        project_data = myLib.newProjectsDoc()
        id = project_data["ref"].id()
    else:
        try:
            project_data = client.query(q.get(q.ref(q.collection("projects"), id)))
            keywords = project_data["data"]["project"]["keywords"]
            for key in keywords:
                keyword_list.append(key["keyword"])
        except:
            keyword_list = []
            
    if request.method == 'POST' and erase:
        myLib.deleteItem("projects",id)
        return redirect(url_for('profile_details'))

    if request.method == 'POST' and not erase:

        banner = request.files['file']
        if banner.filename != '':
            if myLib.allowed_file(banner.filename):
                bannerUrl = myLib.uploadPhotoS3(banner)
                payload.update({"banner": bannerUrl})
                
        start = request.form['start']  
        if start:
            date_time_obj = datetime.strptime(start, '%Y-%m-%d')
            start = date_time_obj.strftime("%m/%d/%Y")
            payload.update({"start": start})
        end = request.form['end']  
        
        if end and end != 'Present':
            date_time_obj = datetime.strptime(end, '%Y-%m-%d')
            end = date_time_obj.strftime("%m/%d/%Y")   
            payload.update({"end": end})
            
        sponsor = request.form['sponsor']
        title = request.form['title']  
        headline = request.form['headline']  
        link = request.form['link']
        location = request.form['location']  
        summary = request.form['summary']
        talent = request.form['talent']
        
        payload.update({"sponsor": sponsor})
        payload.update({"title": title})
        payload.update({"headline": headline})
        payload.update({"link": link})
        payload.update({"location": location})
        payload.update({"summary": summary})
        payload.update({"talent": talent})
        payload.update({"postdate": date})
        myLib.updateProjectDocument(id,payload)                
        
        if request.form['btn'] == 'Save and Back':
            return redirect(url_for('profile_details'))
        elif request.form['btn'] == 'Save and Add':
            return redirect(url_for('project_edit'))
        
    return render_template("pm/project-edit.html", user = user_data, project=project_data, id = id, keys=json.dumps(keyword_list))


@app.route('/add-keyword', methods=["POST"])
def add_project_keyword():
    id  = request.args.get('project_id', None)
    
    if id:
        json_data = request.get_json('keywords_info')
        keys = json_data["keywords_info"]

        updated_keys = []
        for key in keys:
            updated_keys.append({"keyword": key})            
            
        myLib.updateProjectKeys(id,updated_keys)

        return jsonify({"status": "successfully updated database",})
    return jsonify({"status": "new project: ID has not been assigned",})


@app.route('/update-skills', methods=["POST"])
def update_skills():
    talent_email  = request.args.get('email', None)
    talent_id = session["user"]["id"]
    talent_name = session["user"]["firstname"] + " " + session["user"]["lastname"]

    if talent_email:
        talent_data = client.query(q.get(q.match(q.index("userEmail_index"), talent_email)))
        talent_id = talent_data["ref"].id()
        talent_name = talent_data["data"]["account"]["firstname"] + talent_data["data"]["account"]["lastname"]
    
    json_data = request.get_json('skills_info')
    skills = json_data["skills_info"]

    # Get talent skills
    talent_skils = client.query(q.get(q.match(q.index("skill_index"), talent_id)))
    updated_skills = []
    # added_skill = ''
    for skill in skills:
        updated_skills.append({"skill": skill})
        # added_skill = skill
    try:
        myLib.updateSkills(talent_skils["ref"].id(),updated_skills)
        return jsonify({
            "status": "successfully updated database",
            "skill": updated_skills[-1]["skill"],
            "talent_name": talent_name
            })
    except:
        return jsonify({"status": "failed to update the database"})
        
    
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
        contact_list = client.query(q.get(q.match(q.index("contact_index"), user_id)))["data"]["contacts"]
    except:
        contact_list = []
    for contacts in contact_list:
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
    
    skills_list = []
    profile_contacts_data = []
    my_contact = {"status": False}
    user_data = client.query(q.get(q.match(q.index("userEmail_index"), session["user"]['email'])))
    email  = request.args.get('email', None)
    
    if email:
        self = False
        profile_data = client.query(q.get(q.match(q.index("userEmail_index"), email)))
    else:
        self = True
        profile_data = user_data
        
    user_type = session["user"]['usertype']
    user_id = user_data["ref"].id()
    profile_id = profile_data["ref"].id()
    
    profile_experience = myLib.getDocs("experience","experience_index",profile_id)
    profile_education = myLib.getDocs("education","education_index",profile_id)
    profile_projects = myLib.getDocs("project","project_index",profile_id)

    try:
        profile_contact_list = client.query(q.get(q.match(q.index("contact_index"), profile_id)))["data"]["contacts"]
    except:
        profile_contact_list = []
    for contacts in profile_contact_list:
        profile_contact_data = client.query(q.get(q.ref(q.collection("users"), contacts["user_id"])))["data"]
        profile_contacts_data.append(
            {
                "firstname": profile_contact_data["account"]["firstname"],
                "lastname": profile_contact_data["account"]["lastname"],
                "email": profile_contact_data["account"]["email"],
                "photo": profile_contact_data["profile"]["photo"],
                "room_id": contacts["room_id"],
            }
        )
    
    try:
        user_contact_list = client.query(q.get(q.match(q.index("contact_index"), user_id)))["data"]["contacts"]
    except:
        user_contact_list = []
    for contacts in user_contact_list:
        user_contact_data = client.query(q.get(q.ref(q.collection("users"), contacts["user_id"])))
        if user_contact_data["ref"].id() == profile_id:
            my_contact.update({"status": True})
            my_contact.update({"room_id": contacts["room_id"]})    
        
    if user_type == 'Program Manager':
        if self:
            return render_template(
                "pm/profile-pm-self.html", 
                type=user_type, user=user_data, 
                profile=profile_data, 
                experiences=profile_experience, 
                educations=profile_education, 
                projects=profile_projects,
                contacts = profile_contacts_data,
                profile_active="active"
                )
        elif (not self and profile_data["data"]["account"]["usertype"] == 'Program Manager'):
            return render_template(
                "pm/profile-pm.html", 
                type=user_type, user=user_data, 
                profile=profile_data, 
                experiences=profile_experience, 
                educations=profile_education, 
                projects=profile_projects,
                contacts = profile_contacts_data,
                my_contact = my_contact,
                profile_active="active"
                )
        else:
            skills_list=myLib.getSkills(profile_id)
            return render_template(
                "talent/profile-talent.html",
                type=user_type, user=user_data, 
                profile=profile_data, 
                experiences=profile_experience, 
                educations=profile_education, 
                contacts = profile_contacts_data, 
                skills = json.dumps(skills_list),
                my_contact = my_contact,
                profile_active="active"
                )
    elif user_type == 'Engineering Talent':
        if self:
            skills_list=myLib.getSkills(profile_id)
            return render_template(
                "talent/profile-talent-self.html", 
                type=user_type, user=user_data, 
                profile=profile_data, 
                experiences=profile_experience, 
                educations=profile_education, 
                contacts = profile_contacts_data, 
                skills = json.dumps(skills_list),
                profile_active="active"
                )
        elif (not self and profile_data["data"]["account"]["usertype"] == 'Engineering Talent'):
            skills_list=myLib.getSkills(profile_id)
            return render_template(
                "talent/profile-talent.html",
                type=user_type, user=user_data, 
                profile=profile_data, 
                experiences=profile_experience, 
                educations=profile_education, 
                contacts = profile_contacts_data, 
                skills = json.dumps(skills_list),
                my_contact = my_contact,
                profile_active="active"
                )                 
        else:
            return render_template(
                "pm/profile-pm.html",
                type=user_type, user=user_data, 
                profile=profile_data, 
                experiences=profile_experience, 
                educations=profile_education, 
                projects=profile_projects,
                contacts = profile_contacts_data,
                my_contact = my_contact,
                profile_active="active"
                )
            

@app.route("/calendly", methods=["GET","POST"])
@login_required
def schedule():
    try:
        user_email = request.args.get('email', None)
        profile_data = client.query(q.get(q.match(q.index("userEmail_index"), user_email)))
    except:
        return 'user does not have calendly setup'
    return render_template("common/calendly.html", profile=profile_data, session = session)


@app.route("/new-contact", methods=["POST"])
@login_required
def new_contact():
    
    user_id = session["user"]["id"]
    new_contact = request.form["email"].strip().lower()
    
    # If user is trying to add their self, do nothing
    if new_contact == session["user"]["email"]:
        return redirect(url_for("contacts"))

    try:
        new_contact_id = client.query(q.get(q.match(q.index("userEmail_index"), new_contact)))
    except:
        # need to alert here that contact was not found!
        return redirect(url_for("contacts"))
    
    # Get the contacts | related to both users
    user_contacts = client.query(q.get(q.match(q.index("contact_index"), user_id)))
    recepient_contacts = client.query(q.get(q.match(q.index("contact_index"), new_contact_id["ref"].id())))
    
    # Check if the chat the user is trying to add has not been added before
    try:
        contact_list = [list(i.values())[0] for i in user_contacts["data"]["contacts"]]
    except:
        contact_list = []

    if new_contact_id["ref"].id() not in contact_list:
        
        # Append the new chat to the chat list of the user
        room_id = str(int(new_contact_id["ref"].id()) + int(user_id))[-4:]
        user_contacts["data"]["contacts"].append({
                "user_id": new_contact_id["ref"].id(), 
                "room_id": room_id
            }
        )
        recepient_contacts["data"]["contacts"].append({
            "user_id": user_id, "room_id": room_id
            }
        )

        # Update chat list for both users
        myLib.updateUserContacts(user_contacts["ref"].id(),user_contacts["data"]["contacts"])
        myLib.updateUserContacts(recepient_contacts["ref"].id(),recepient_contacts["data"]["contacts"])

        # create new document for their conversations
        myLib.newMessagesDoc(room_id)

    return redirect(url_for("contacts"))


@app.route("/text", methods=["GET","POST"])
@login_required
def text():
    
    room_id = request.args.get("rid", None)
    data = []
    message_history = []

    try:
        # Get the chat list for the user in the room i.e all of the people they have a chat histor with on the application
        contact_list = client.query(q.get(q.match(q.index("contact_index"), session["user"]["id"])))["data"]["contacts"]
    except:
        contact_list = []

    for contacts in contact_list:
        if room_id == contacts["room_id"]:
            message_history = client.query(q.get(q.match(q.index("message_index"), room_id)))["data"]["conversation"]
            contact_data = client.query(q.get(q.ref(q.collection("users"), contacts["user_id"])))
            # Try to get the last message for the room
            try:
                last_message = client.query(q.get(q.match(q.index("message_index"), contacts["room_id"])))["data"]["conversation"][-1]["message"]
            except:
                last_message = "This place is empty. No messages ..."
            
            data.append(
                {
                    "name": contact_data["data"]["account"]["firstname"],
                    "lastname": contact_data["data"]["account"]["lastname"],
                    "photo": contact_data["data"]["profile"]["photo"],
                    "calendly": contact_data["data"]["profile"]["calendly"],
                    "email": contact_data["data"]["account"]["email"],
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
        messages=message_history,
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
            {
            "data": {
                "conversation": conversation
                }
            },
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


