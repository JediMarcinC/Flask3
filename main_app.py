import gc
from functools import wraps

from flask import Flask, render_template, redirect, flash, request, session, url_for
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart

from content.content_management import Content
from dbconnect import connection
from forms import RegistrationForm

app = Flask(__name__)

app.secret_key = 'llave'

TOPIC_DICT = Content()

    
def login_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('You need to log in first')
            return redirect(url_for('login'))
    return wrap


def topic_completion_percent():
    completed_percentages = {}
    try:
        client_name, settings, tracking, rank = userinformation()
        try:
            tracking = tracking.split(",")
        except:
            pass
        if tracking == None:
            tracking = []
            flash("tracking is none")
        
        for each_topic in TOPIC_DICT:
            total = 0
            total_complete = 0
            
            for each in TOPIC_DICT[each_topic]:
                total += 1
                for done in tracking:
                    if done == each[1]:
                        total_complete += 1
            percent_complete = int(((total_complete*100)/total))
            completed_percentages[each_topic] = percent_complete
    except:
        print(" -!- COMPLETION PERCENT PROBLEM!!!")
        for each_topic in TOPIC_DICT:
            total = 0
            total_complete = 0
            completed_percentages[each_topic] = 0.0
    print('completed_percentages:', completed_percentages)
    return completed_percentages


@app.route('/')
def main():
    return render_template('dashboard.html', TOPIC_DICT = Content())


@app.route('/guided-tutorials/', methods=['GET', 'POST'])
@app.route('/topics/', methods=['GET', 'POST'])
@app.route('/begin/', methods=['GET', 'POST'])
@app.route('/python-programming-tutorials/', methods=['GET', 'POST'])
@app.route('/dashboard/', methods=['GET', 'POST'])
#@login_required
def dashboard():
    client_name, settings, tracking, rank = userinformation()
    if len(tracking) < 10:
        tracking = "/introduction-to-python-programming/"
    gc.collect()

    if client_name == "Guest":
        flash("Welcome Guest, feel free to browse content. Progress tracking is only available for Logged-in users.")
        tracking = ['None']

    update_user_tracking()

    completed_percentages = topic_completion_percent()

    return render_template("dashboard.html",TOPIC_DICT = TOPIC_DICT, tracking = tracking, completed_percentages=completed_percentages)
        


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur, conn = connection()
        cur.execute("SELECT * FROM users WHERE username=(%s);", thwart(request.form['username']))
        user = cur.fetchone()
        if user:
            password = user[2]
            if sha256_crypt.verify(request.form['password'], password):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash('You are now logged in.', 'success')
                return redirect(url_for('main'))
            else:
                error = 'Invalid password!'
        else:
            error = "This user doesn't exists."
    gc.collect()
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur, conn = connection()
        cur.execute("SELECT * FROM users WHERE username=(%s);", thwart(username))
        if cur.fetchone():
            flash('This username is already taken.', 'danger')
            return render_template('register.html', form=form)
        cur.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                    (thwart(username), thwart(password), thwart(email), thwart('/main/')))
        conn.commit()
        flash('You have successfully signed up.', 'success')
        cur.close()
        conn.close()
        gc.collect()
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('main'))
    return render_template('register.html', form=form)

def userinformation():
    try:
        client_name = (session['username'])
        guest = False
    except:
        guest = True
        client_name = "Guest"
        
    if not guest:
        try:
            c,conn = connection()
            c.execute("SELECT * FROM users WHERE username = (%s)",
                    (thwart(client_name)))
            data = c.fetchone()
            settings = data[4]
            tracking = data[5]
            rank = data[6]
        except Exception as e:
            print(" -!- SQL PROBLEM!!!")
            pass

    else:
        settings = [0,0]
        tracking = [0,0]
        rank = [0,0]
        
    return client_name, settings, tracking, rank

def update_user_tracking():
    try:
        completed = str(request.args['completed'])
        if completed in str(TOPIC_DICT.values()):
            client_name, settings, tracking, rank = userinformation()
            if tracking == None:
                tracking = completed
            else:
                if completed not in tracking:
                    tracking = tracking+","+completed
            
            c,conn = connection()
            c.execute("UPDATE users SET tracking = %s WHERE username = %s",
                    (thwart(tracking),thwart(client_name)))
            conn.commit()
            c.close()
            conn.close()
            client_name, settings, tracking, rank = userinformation()

        else:
            pass

    except Exception as e:
        pass
        print(" -!- CANNOT UPDATE USER TRACKING!!!")
        flash(str(e))
    

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.')
    gc.collect()
    return redirect(url_for('main'))



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)