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

def updateProfilePhoto(url):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "photo": url,
                        },
                    }
                },
            )
        )
    
    

    
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

    
def deleteItem(collection,id):
    client.query(
    q.delete(q.ref(q.collection(collection), id))
)
    
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

def getDocs(var, index, id):
    result = client.query(
        q.map_(
            q.lambda_(var, q.get(q.var(var))),
            q.paginate(q.match(q.index(index), str(id)),size=100)
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
    
def updateAccountName(firstname, lastname):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "account": {
                        "firstname": firstname,
                        "lastname": lastname,
                        },
                    }
                },
            )
        )
    
def updateProfileContact(phone, calendly = ""):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "phone": phone,
                        "calendly": calendly,
                        },
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
    
def getSkills(user_id):
    user_skills = client.query(q.get(q.match(q.index("skill_index"), user_id)))
    try:
        skills_list = [list(i.values())[0] for i in user_skills["data"]["skills"]]
    except:
        skills_list = []
    return skills_list



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
    

def updateProfileHeadline(headline):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "headline": headline,
                        },
                    }
                },
            )
        )
    
def updateProfileAvailability(availability):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "availability": availability,
                        },
                    }
                },
            )
        )
    
def updateProfileSummary(summary):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "summary": summary,
                        },
                    }
                },
            )
        )

def updateProfileIndustry(industry):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "industry": industry,
                        },
                    }
                },
            )
        )
    
def updateProfileDivision(division):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "division": division,
                        },
                    }
                },
            )
        )
    
def updateProfileLocation(zipcode,city):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "profile": {
                        "zipcode": zipcode,
                        "city": city,
                        },
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
    

    
# def newAuthorizationDoc(collection,id):
#     client.query(
#         q.create(
#             q.collection(collection),
#             {
#                 "data": {
#                     "user_id": id,
#                     "keys": {
#                         "auth": "null"
#                     },
#                 }
#             },
#         )
#     )
    
def createSession(user):
    session["user"] = {
        "id": user["ref"].id(),
        "firstname": user["data"]["account"]["firstname"],
        "lastname": user["data"]["account"]["lastname"],
        "email": user["data"]["account"]["email"],
        "usertype": user["data"]["account"]["usertype"],
        "loggedin": True,
    }
    