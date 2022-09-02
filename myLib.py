from config import client
from faunadb import query as q

# uploadPhoto
from config import s3, os
from werkzeug.utils import secure_filename
import uuid
from flask import session
from app import app

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
def uploadPhotoS3(photo):
    uuid_ = uuid.uuid4()
    filename = secure_filename('profile_photo-' + session["user"]["id"] + '-' + str(uuid_))
    url = 'https://bidztr.s3.amazonaws.com/{}'.format(filename)
    photo.save("static/tmp/"+filename)
    s3.upload_file(
        Bucket=app.config['S3_BUCKET'],
        Filename="static/tmp/"+filename,
        Key=filename)
    os.remove("static/tmp/"+filename)
    return url

 
def newCollectionDoc(collection,id):
    result = client.query(
        q.create(
            q.collection(collection),
            {
                "data": {
                    "user_id": id,
                    collection: [],
                }
            },
        )
    )
    return result
    
    
def deleteItem(collection,id):
    client.query(
    q.delete(q.ref(q.collection(collection), id))
)
    

def getTalents_byKey(keyword):
    matched_docs = getDocs("skill","skill_match_index",keyword)
    matches = [
        client.query(q.get(q.ref(q.collection("users"), user["data"]["user_id"] ))
        ) for user in matched_docs
    ]
    return matches

def getProjects_byKey(keyword):
    matched_docs = getDocs("project_keyword","project_keyword_index",keyword)
    matches = [
        client.query(q.get(q.ref(q.collection("projects"), project["ref"].id() ))
        ) for project in matched_docs
    ]
    return matches
    

def getMatches_byList(index, list):
    result = client.query(
        q.map_(
            q.lambda_("ref", q.get(q.var("ref"))),
            q.paginate(
                q.union(
                    q.map_(
                        q.lambda_("element",q.match(q.index(index), q.var("element"))),
                        list
                    )
                )
            )
        )
    )["data"]
    return result

def getApplicants_byProject(project_id):
    matched_docs = getDocs("applicant","project_applicant_index",project_id)
    matches = [
        client.query(q.get(q.ref(q.collection("users"), application["data"]["user_id"] ))
        ) for application in matched_docs
    ]
    return matches
    

def getDocs(var, index, id):
    result = client.query(
        q.map_(
            q.lambda_(var, q.get(q.var(var))),
            q.paginate(q.match(q.index(index), str(id)),size=100)
        )      
    )["data"]
    return result

def getCollection(var, collection):
    result = client.query(
        q.map_(
            q.lambda_(var, q.get(q.var(var))),
            q.paginate(q.documents(q.collection(collection)),size=100)
        )      
    )["data"]
    return result

def getDocsCount(var, index, id):
    result = client.query(
        q.count(
            q.map_(
                q.lambda_(var, q.get(q.var(var))),
                q.paginate(q.match(q.index(index), str(id)),size=100)
            )
        )  
    )["data"]
    return result
    
    
def getSkills(user_id):
    user_skills = client.query(q.get(q.match(q.index("skill_index"), user_id)))
    try:
        skills_list = [list(i.values())[0] for i in user_skills["data"]["skills"]]
    except:
        skills_list = []
    return skills_list



# New Docs
def newCollectionDoc(collection,id):
    client.query(
        q.create(
            q.collection(collection),
            {
                "data": {
                    "user_id": id,
                    collection: [],
                }
            },
        )
    )
    
def newMessagesDoc(room_id):
    client.query(
            q.create(
                q.collection("messages"),
                {
                    "data": {
                        "room_id": room_id, 
                        "conversation": []
                    }
                },
            )
        )
    
def newUserDoc(type,firstname,lastname,email,password,date):
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
                        "password": password,
                        },
                    "profile": {
                        "photo": "https://bidztr.s3.amazonaws.com/65463811-61ff-49d0-a714-c93369649d94-docs-avatar.png",
                        "phone": "null",
                        "calendly": "null",
                        "headline": "null",
                        "summary": "null",
                        "division": "null",
                        "availability": "null",
                        "industry": "null",
                        "zipcode": "null",
                        "city": "null",
                        },
                    "sub": {
                        "keys": {
                            "auth": "none",
                            },
                        },
                    "date": date,
                }
            },
        )
    )
    return user

def newExperiencesDoc():
    result = client.query(
                q.create(
                    q.collection("experiences"),
                    {
                        "data": {
                            "user_id": session["user"]["id"],
                            "experience": {
                                "start": "null",
                                "end": "null",
                                "title": "null",
                                "type": "null",
                                "company": "null",
                                "location": "null",    
                                "status": "null",    
                                "industry": "null",    
                                },
                        }
                    },
                )
            )
    return result

def newProjectsDoc():
    result = client.query(
                q.create(
                    q.collection("projects"),
                    {
                        "data": {
                            "user_id": session["user"]["id"],
                            "project": {
                                "banner": "https://bidztr.s3.amazonaws.com/profile_photo-340335658474143823-cbdf807e-aae5-4bd3-a976-2fd1f1f8f7ba",
                                "start": "null",
                                "end": "null",
                                "sponsor": "null",
                                "title": "null",
                                "headline": "null",
                                "link": "null",
                                "location": "null",
                                "summary": "null",
                                "talent": "null",
                                "postdate": "null",
                            },
                        }
                    },
                )
            )
    return result
    
def newEducationsDoc():
    result = client.query(
                q.create(
                    q.collection("educations"),
                    {
                        "data": {
                            "user_id": session["user"]["id"],
                            "education": {
                                "start": "null",
                                "end": "null",
                                "school": "null",
                                "degree": "null",
                                "field": "null",
                                "status": "null",
                                },
                        }
                    },
                )
            )
    return result

def newNotificationDoc(profile_id,type,name,target):
    client.query(
        q.create(
            q.collection("notifications"),
            {
                "data": {
                    "user_id": profile_id,
                    "notification": {
                        "type": type,
                        "name": name,
                        "target": target,
                        },
                    }
                },
            )
        )


# updates

def updateUserBookmarks(id,bookmarks):
    client.query(
        q.update(
            q.ref(q.collection("bookmarks"), id),
            {
                "data": {
                    "bookmarks": bookmarks
                }
            },
        )
    )
    
def updateUserApplications(id,applications):
    client.query(
        q.update(
            q.ref(q.collection("applications"), id),
            {
                "data": {
                    "applications": applications
                }
            },
        )
    )
  
def updateUserContacts(id,contacts):
    client.query(
        q.update(
            q.ref(q.collection("contacts"), id),
            {
                "data": {
                    "contacts": contacts
                }
            },
        )
    )  


def updateProfile(account_payload,profile_payload):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "account": account_payload,
                    "profile": profile_payload,
                    }
                },
            )
        )
    
def updateProjectDocument(id, payload):
    client.query(
        q.update(
            q.ref(q.collection("projects"), id),
            {
                "data": {
                    "project": payload
                    }
                },
            )
        )
    
def updateExperienceDocument(id, payload):
    client.query(
        q.update(
            q.ref(q.collection("experiences"), id),
            {
                "data": {
                    "experience": payload
                    }
                },
            )
        )

def updateEducationDocument(id,payload):
    client.query(
        q.update(
            q.ref(q.collection("educations"), id),
            {
                "data": {
                    "education": payload
                    }
                },
            )
        )

def updateProjectKeys(id,keywordList):
    client.query(
            q.update(
                q.ref(q.collection("projects"), id),
                {
                    "data": {
                        "project": {
                                "keywords": keywordList,
                            },
                        }
                    },
                )
            )   
    
def updateSkills(id,skills):
    client.query(
            q.update(
                q.ref(q.collection("skills"), id),
                {
                    "data": {
                        "skills": skills
                    }
                },
            )
        )   
    
# session
    
    
def createSession(user):
    session["user"] = {
        "id": user["ref"].id(),
        "firstname": user["data"]["account"]["firstname"],
        "lastname": user["data"]["account"]["lastname"],
        "email": user["data"]["account"]["email"],
        "usertype": user["data"]["account"]["usertype"],
        "loggedin": True,
    }
    