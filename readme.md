# Project Narwhal

### Table of contents
0. **Demo**
1. **About**
	1.1 Creating the Navy’s Gig Economy App
	1.2 Project Requirements
2. **Submission**
	2.1 Compliance Matrix
	2.2 Technology
	2.3 User Experience
	2.4 Features
	2.5 Future Integration
3. **Get Started**
	3.1 Docker Compose
	3.3 Docker File
	3.3 Build from Scratch
4. **Contact**
5. **License**

## 0. Demo
An fully functional online demo of this project is provided through access to [narwhal.app](https://narwhal.app) 
The objective of this demo is to provide you with the complete experience of the Narwhal progressive web application.

You may log in using an engineering talent account, or a program manager account:
#### Browse Narwhal as: `engineering talent`
`Email:` talent@narwhal.app
`Password:` NarwhalApp

When browsing under the `engineering talent` account, your profile will be setup and you'll be able to browse through several projects from 3 different program managers, each with 2 active projects.

#### Browse Narwhal as: `program manager`
`Email:` pm@narwhal.app
`Password:` NarwhalApp

When browsing under the `program manager` account, your profile and projects will be setup and you'll be able to browse through 5 talented


## 1. About

### 1.1 Creating the Navy's Gig Economy App

The Naval Warfare Centers work on ever changing Research, Development, Test, and Evaluation (RDT&E) projects for various customers/sponsors across the DoD. However, being able to match project needs with available personnel is a challenge. With the help of a workshop with Begin Morning Nautical Twilight (BMNT), the Naval Information Warfare Center Pacific (NIWC Pacific) have derived that the Naval workforce could benefit from an online, interactive Gig economy. Therefore, we are looking to leverage novel concepts and new technologies currently being used to create the emergent “Gig Economy” and develop an internal capability to more efficiently and effectively solicit short-term project needs and find skilled workers to help with tasks. For additional information, please check out the full [challenge details.](https://www.challenge.gov/?challenge=project-narwhal)

### 1.2 Project Requirements
Submissions will be judged based on ability to adhere to the 7 feature requests provided below:
1.  **Talent profiles**
    - Intuitive and fun user interface (UI) that allows engineers to create profiles.  
	    - Requires the ability to easily input both pre-populated and manually entered skills
	    - Requires the ability of the engineers to provide information about their availability and interests 
	    - The Challenge winner would have a way to engage the engineer to make this fun.
2.  **Program manager profiles**
    - Intuitive and fun UI for Program Managers that allows them to break down a task.  
	    - Requires both the ability to input free text and suggest text. 
	    - Requires the ability to search through past and active projects easily by different filters 
3.  **Matching algorithm**
    -   Requires the ability to easily search through matches.
    -   Every successful match is then used to reinforce the algorithm and update a “rating” for the engineer.
4.  **Intuitive and user-friendly homepage**
	- Includes robust search algorithm that lets:
		- project managers to easily search through engineer profiles and,
		- allows talent to see posted projects.
5.  **Push notifications**
	- Ability to set alerts that will ping users when certain key words, skills, or project tasks are posted.
6.  **Container**
	- The entire application needs to be able to be built with a DockerFile.
7.  **Repository**
	- The complete code repository needs to be provided for review.

## 2. Submission

### 2.1 Compliance Matrix
| |      Requirement          |     Status    |     Notes     |
|-|---------------------------|:-------------:|---------------|
|1| Talent Profiles 					|    Success    | . |
|2| Program Manager Profiles 	|    Success    | . |
|3| Matching Algorithm 				|    Success    | . |
|4| Intuitive Home-Page 			|    Success    | . |
|5| Push Notifications 				|    Success    | . |
|6| Containerized 						|    Success    | `docker pull jafman3/narwhal_web` |
|7| Repository 								|    Success    | `git@github.com:jafman33/narwhal.git` |


### 2.2 Technology
The Narwhal project is a progressive web application **PWA**, built using python **Flask**, taking advantage of **Fauna**'s server-less database.

**[Flask](https://www.fullstackpython.com/flask.html)** is a web development micro-framework developed in Python. Flask is known as a _micro-framework_ because it is _lightweight_ and _only_ provides components that are _essential_. It only provides the necessary components for web development, such as routing, request handling, sessions, and so on.

**[PWAs](https://web.dev/what-are-pwas/)** are web apps developed using a number of specific technologies and standard patterns to allow them to take advantage of both web apps and native app features. PWA's are built and enhanced with modern APIs to deliver enhanced capabilities, reliability, and installability while reaching _anyone, anywhere, on any device_ with a single code-base.

**[Fauna](https://fauna.com/)** is a distributed document-relational database delivered as a cloud API. You can build existing applications to Fauna and scale without worrying about operations.

Additional integrations
talk about S3
talk about Calendly

### 2.3 User Experience


### 2.4 Features

calendly + zoom
messenger

### 2.4 Future Integrations

LinkedIn API


## 3. Get Started

### 3.1 Docker Compose

In compliance with ```Project Requirement 6```,  both a ```Dockerfile``` and a ```docker-compose.yml``` has been provided with this submission. Assuming you have docker installed, you may build and run the narwhal project with the following command:

```docker compose up```

The link to the Narwhal image is stored in [Dockerhub](#).

### 3.2 Dockerfile
Alternatively, you may build and run the narwhal project without using docker compose. 

```docker build --tag narwhal-docker:latest .```

```docker run -d -p 5000:5000 narwhal-docker```

For additional questions, visit [Docker](https://docker-curriculum.com/).

### 3.3 Build from scratch 
In VS Code, open a terminal and navigate to the current directory if not already there.

`cd <my-project>/`

`virtualenv venv`

If you want your virtualenv to also inherit globally installed packages run:

`virtualenv venv --system-site-packages`

These commands create a venv/ directory in your project where all dependencies are installed. You need to activate it first though (in every terminal instance where you are working on your project):

`source venv/bin/activate`

You should see a (venv) appear at the beginning of your terminal prompt indicating that you are working inside the virtualenv. Now when you install something like this:

`pip install <package>`

If there is a requirements.txt file, run it as follows:

`pip install -r requirements.txt`

## 4. Author

For any questions, please contact the creator of this work, please contact the sole developer and creator of this submission.

`Name:` Juan-Pablo Afman
`LinkedIn:`  [linkedin.com/in/jp-afman](https://www.linkedin.com/in/jp-afman/)
`Email:` [jafman3@gmail.com](mailto:jafman3@gmail.com)

## 5. License
[MIT](https://choosealicense.com/licenses/mit/)