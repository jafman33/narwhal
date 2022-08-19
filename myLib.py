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
    
def updateProjectBanner(id, url):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    "projects": {
                        id: {
                            "banner": url,
                            },
                        },
                    }
                },
            )
        )
    
def deleteItem(item,id):
    client.query(
        q.update(
            q.ref(q.collection("users"), session["user"]["id"]),
            {
                "data": {
                    item: {
                        id: None,
                        },
                    }
                },
            )
        )
    
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
    
