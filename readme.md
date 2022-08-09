# A simple chat application using flask and fauna

## Setup a virtual environment
In VS Code, open a terminal and navigate to the current directory if not already there.

* `cd <my-project>/`
* `virtualenv venv`

If you want your virtualenv to also inherit globally installed packages run:

* `virtualenv venv --system-site-packages`

These commands create a venv/ directory in your project where all dependencies are installed. You need to activate it first though (in every terminal instance where you are working on your project):

* `source venv/bin/activate`

You should see a (venv) appear at the beginning of your terminal prompt indicating that you are working inside the virtualenv. Now when you install something like this:

* `pip install <package>`

If there is a requirements.txt file, run it as follows:

* `pip install -r requirements.txt`