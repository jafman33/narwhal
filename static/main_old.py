from app import app
from flask import render_template, redirect, url_for, request, session, make_response, send_from_directory
import MySQLdb.cursors
from flask_gtts import gtts
from config import mysql
import re
import yaml

# new idea to rout these on the fly
import os


from flask_gtts import gtts

# GTTS
gtts(app, temporary=False, tempdir='flask_gtts', route=True, route_path='/gtts')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        # sumbmit all data entries
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query_string = 'SELECT * FROM accounts WHERE email = %s AND password = %s'
        cur.execute(query_string, (email, password,))
        account = cur.fetchone()

        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['firstname'] = account['firstname']
            session.permanent = True

            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('my_home'))
        else:
            # Account doesnt exist or email/password incorrect
            msg = 'Incorrect email or password!'
            return render_template('page-login.html', msg=msg)

    return render_template('page-login.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('firstname', None)
    # Redirect to login page
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST'\
            and 'firstname' in request.form \
            and 'lastname' in request.form \
            and 'email' in request.form \
            and 'password' in request.form:

        # Create variables for easy access
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not firstname or not lastname or not email or not password:
            msg = 'Please fill out the form completely!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s)',
                (firstname, lastname, email, password, " ", "0",))

            # Create lessons default flags for that user
            cursor.execute('INSERT INTO lessons (id) VALUES (NULL)')

            mysql.connection.commit()
            cursor.close()
            msg = 'You have successfully registered!'
            # Send Email here!!!!
            #
            #   EMAIL SCRIPT
            #

            # ---- New! -----
            # Log people in automatically after registering!
            # since you're routed from registration page, maybe start with instructions wizzard!

            # sumbmit all data entries
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query_string = 'SELECT * FROM accounts WHERE email = %s AND password = %s'
            cur.execute(query_string, (email, password,))
            account = cur.fetchone()

            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['email'] = account['email']
                session['firstname'] = account['firstname']
                # Redirect to instructions page!
                return redirect(url_for('about'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('page-register.html', msg=msg)


@ app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('loggedin'):

        return redirect(url_for('my_home'))

    # we can also just render it directly if problems occur!
    return redirect(url_for('login'))


@ app.route('/my-home', methods=['GET', 'POST'])
def my_home():
    if 'loggedin' in session:

        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = %s', (session['id'],))
        lessons_status = cursor.fetchone()
        cursor.close()
        print(lessons_status)

        return render_template('index.html', account=account, home_active='active', lessons_status=lessons_status)

    return redirect(url_for('login'))


@ app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@ app.route('/how-to-play', methods=['GET', 'POST'])
def how_to_play():
    return render_template('how-to-play.html')


@ app.route('/my-lessons', methods=['GET', 'POST'])
def my_lessons():
    if session.get('loggedin'):

        # We need all the account info for the user so we can display it sidebar
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        cursor.close()

        # We need all the account info for the user so we can display /my-lessons
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = %s', (session['id'],))
        lessons_status = cursor.fetchone()
        cursor.close()

        # Create a Yaml File with all the lesson names!
        titles = 'yaml/phonemes.yaml'
        data = yaml.full_load(open(titles))

        return render_template('lessons-list.html', lessons_status=lessons_status, titles=data, account=account, lessons_active='active')

    return redirect(url_for('login'))


@ app.route('/lesson/<phonemeNo>', methods=['GET', 'POST'])
def lesson(phonemeNo):

    if session.get('loggedin'):
        lessonNo = 'lesson_' + phonemeNo
        phoneme_request = 'yaml/phoneme' + str(phonemeNo) + '.yaml'
        data = yaml.full_load(open(phoneme_request))

        # Get the status of all the lessons for this user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM lessons WHERE id = %s', (session['id'],))
        status = cursor.fetchone()
        cursor.close()

        # update the status of the requested lesson to 'in-progress' IFF status != 'completed'
        if status[lessonNo] != 'completed':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query_str = 'UPDATE lessons SET ' + lessonNo + ' = %s WHERE id = %s'
            cursor.execute(query_str, ('in-progress', session['id'],))
            mysql.connection.commit()
            cursor.close()

        # Question: how to set status = 'completed'? -  POST from last page here!
        # formData = request.form
        if request.method == 'POST' and request.form['btn'] == 'Finish!':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            query_str = 'UPDATE lessons SET ' + lessonNo + ' = %s WHERE id = %s'
            cursor.execute(query_str, ('completed', session['id'],))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('my_lessons'))
        elif request.method == 'POST' and request.form['btn'] == 'Keep Learning':
            return render_template('lesson-template-1v4.html', data=data)

        return render_template('lesson-template-1v4.html', data=data)

    return redirect(url_for('login'))


@ app.route('/profile', methods=['GET', 'POST'])
def my_profile():

    if session.get('loggedin'):
        # We need all the account info for the user so we can display it sidebar
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        cursor.close()

        return render_template('my-profile.html', account=account)
    return redirect(url_for('login'))


@ app.route('/under-construction', methods=['GET', 'POST'])
def under_construction():
    return render_template('page-under-construction.html')


@ app.route('/terms', methods=['GET', 'POST'])
def terms():
    return render_template('component-go-to-top.html')


# Rout to the service-worker javascript file otherwise not found.
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


@app.route('/test', methods=['GET', 'POST'])
def test():

    return render_template('test.html')


@app.route("/t2s/<contrastNo>/<name>", methods=['POST', 'GET'])
def t2s(contrastNo, name):
    from gtts import gTTS
    import os
    filename = "static/assets/audio/contrast" + \
        contrastNo + "/words/" + name + ".mp3"
    obj = gTTS(text=name, lang='en')
    obj.save(filename)
    return '', 204

# @app.route('/manifest.json')
# def manifest():
#     return send_from_directory('static', 'manifest.json')


if __name__ == '__main__':
    app.run(debug=True)
