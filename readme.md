# Project Narwhal
Narwhal is an interactive Progressive Web Application designed with the intent of creating employment connections for the Naval Workforce. Narwhal leverages novel concepts and new technologies currently being employed to create the emergent “Gig Economy”. We have developed the internal capability for project managers to more effectively solicit short-term project needs while connecting them with skilled engineers to take their projects to the next level.
### Table of contents
1. **Project Submission**
	- 1.1 Creating the Navy’s Gig Economy App
	- 1.2 Project Requirements
	- 1.3 Compliance Matrix
2. **Get Started**
	- 2.1 Docker Compose
	- 2.3 Docker File
	- 2.3 Build from Scratch
3. **Contact**
4. **License**
5. **Demo**

## 1. Project Submission

### 1.1 Creating the Navy's Gig Economy App

The Naval Warfare Centers work on ever changing Research, Development, Test, and Evaluation (RDT&E) projects for various customers/sponsors across the DoD. However, being able to match project needs with available personnel is a challenge. With the help of a workshop with Begin Morning Nautical Twilight (BMNT), the Naval Information Warfare Center Pacific (NIWC Pacific) have derived that the Naval workforce could benefit from an online, interactive Gig economy. Therefore, we are looking to leverage novel concepts and new technologies currently being used to create the emergent “Gig Economy” and develop an internal capability to more efficiently and effectively solicit short-term project needs and find skilled workers to help with tasks. For additional information, please check out the full [challenge details.](https://www.challenge.gov/?challenge=project-narwhal)

### 1.2 Project Requirements
The project objectives are laid out by the following 7 feature requests:
1.	Talent profiles: Narwhal provides an intuitive and fun UI that allows talent to create profiles where they
	- can visualize an overview of their profile progress to engage users to fully complete their profiles!
	- can easily input both pre-populated and manually entered content.
	- can provide information about their availability, skills, objective, and much more!
	- automatically get matched with projects that meet one or more of their skills and talents.
2.	Program manager profiles: Intuitive and fun UI for Program Managers that allows them to break down a task.
	- create blog-post style projects that talent can then bookmark, share, and apply to
	- input both free text and suggest text while searching for talent
	- automatically get matched with active talents that meet one or more of their project requirements.
3.	Matching algorithm: Narwhal provides the ability for both talent and program managers to
	-	perform efficient searches through active projects or talent respectively via key words 
	-	be proposed automatic matches of projects or talent respectively without the need for user input
	-	enter and endorse skills respectively.
4.	Intuitive and user-friendly homepage: Includes robust search algorithm that lets:
	-	project managers to easily search through engineer profiles and,
	-	allows talent to see posted projects.
5.	Push notifications: Narwhal supports both web-push notifications and in-app notifications that ping users when 
	-	a new match between a project and a talent has been automatically detected
	-	a new contact has been requested
	-	a new application to a project has been submitted
6.	Docker Container: The Narwhal PWA builds both from source and a DockerFile has been provided.
7.	Shared Repository: The Narwhal PWA code repository has been provided for review. 

### 1.3 Compliance Matrix
| |      Requirement          |     Status    |     Notes     |
|-|---------------------------|:-------------:|---------------|
|1| Talent Profiles 				|    Success    | Intuitive and fun UI for engaging talent to create robust profiles |
|2| Program Manager Profiles 		|    Success    | Intuitive and fun UI for program managers to create project posts |
|3| Matching Algorithm 				|    Success    | Basic but fully scalable demonstration. Automatic and Keyword Based |
|4| Intuitive Home-Page 			|    Success    | Talent can find projects and program managers can find talent |
|5| Notifications 					|    Success    | Both in-app and web-push          |
|6| Containerized 					|    Success    | `docker pull jafman3/narwhal_web:submission` |
|7| Repository 						|    Success    | `git@github.com:jafman33/narwhal.git` |

DockerHub and GitHub repositories are private. Please request access per instructions by Dr. Jamie R. Lukos

## 2. Get Started

The link to the Narwhal image can be obtained by:

`docker pull jafman3/narwhal_web:submission`

Note that this is a private repository and permission will be granted upon request.
Ref: Conversation with Dr. Jamie R. Lukos

### 2.1 Docker Compose

In compliance with ```Project Requirement 6```,  both a ```Dockerfile``` and a ```docker-compose.yml``` have been provided with this submission. 

Assuming you have docker installed, you may build and run the narwhal project with the following command:

```docker compose up```

Verify the deployment by navigating to your server address in your preferred browser.

``` 127.0.0.1:5000 ```

### 2.2 Dockerfile
Alternatively, you may build and run the narwhal project without using docker compose. 

```docker build --tag narwhal-docker:latest .```

```docker run -d -p 5000:5000 narwhal-docker```

For additional questions, visit [Docker](https://docker-curriculum.com/).

### 2.3 Build from scratch 
In VS Code, open a terminal and navigate to the current directory if not already there.

`cd <my-project>/`

`virtualenv venv`

If you want your virtualenv to also inherit globally installed packages run:

`virtualenv venv --system-site-packages`

These commands create a venv/ directory in your project where all dependencies are installed. You need to activate it first though (in every terminal instance where you are working on your project):

`source venv/bin/activate`

You should see a (venv) appear at the beginning of your terminal prompt indicating that you are working inside the virtualenv. 
Now simply install the packages using:

`pip install -r requirements.txt`

Note that this project uses Python3.8.9. Python versions above this may result in compilations errors.

## 3. Contact

For any questions, please contact the creator of this work, please contact the sole developer and creator of this submission.

`Name:` Juan-Pablo Afman

`LinkedIn:`  [linkedin.com/in/jp-afman](https://www.linkedin.com/in/jp-afman/)

`Email:` [jafman3@gmail.com](mailto:jp-afman@atlrobotics.com)

## 4. License

No license has been assigned to this project yet.

## 5. Demo
An fully functional online demo of this project is provided through access to [Narwhal](http://139.144.26.69) 
The objective of this demo is to provide you with the complete experience of the Narwhal progressive web application.

You may log in using an engineering talent account, or a program manager account:
#### Browse Narwhal as: `Engineering Talent`
- `Email:` talent@narwhal.app
- `Password:` NarwhalApp

When browsing under the `Engineering Talent` account, your profile will be setup and you'll be able to browse through one or more projects from two different program managers.

#### Browse Narwhal as: `Program Manager`
- `Email:` pm@narwhal.app
- `Password:` NarwhalApp

When browsing under the `Program Manager` account, your profile and projects will be setup and you'll be able to browse through two talented individuals.