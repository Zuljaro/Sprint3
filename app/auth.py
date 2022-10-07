from ast import And
from asyncio import current_task
import functools
import random
import flask
from . import utils

from email.message import EmailMessage
import smtplib

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/activate', methods=('GET', 'POST'))
def activate():
    try:
        if g.user:
            return redirect(url_for('inbox.show'))
        
        if request.method == 'GET':    # cambio
            number = request.args['auth'] 
            
            db = get_db() # cambio
            attempt = db.execute(
                'SELECT * FROM activationlink where challenge = ? state = ? AND  CURRENT_TIMESTAMP BETWEEN created and validuntil', (number, utils.U_UNCONFIRMED)  # cambio
            ).fetchone()

            if attempt is not None:
                db.execute(
                    'UPDATE activationlink SET state = ? WHERE id = ?', (utils.U_CONFIRMED, attempt['id']) # update falta

                )
                db.execute(
                    'INSERT INTO user (username, password,  salt, email) VALUES (?,?,?,?)', (attempt['username'], attempt['password'], attempt['salt'], attempt['email'])  # insert 
                
                )
                db.commit()

        return redirect(url_for('auth.login'))
    except Exception as e:
        print(e)
        return redirect(url_for('auth.login'))


@bp.route('/register', methods=('GET', 'POST')) # cambio
def register():
    try:
        if g.user:
            return redirect(url_for('inbox.show'))
      
        if request.method == 'POST':  # cambio    
            username = request.form['username'] #cambio
            password = request.form['password'] #cambio
            email = request.form['email'] #cambio
            
            db = get_db()  # cambioo
            error = None

            if not username:   #cambio
                error = 'Username is required.'
                flash(error)
                return render_template('auth/register.html') # cambio
            
            if not utils.isUsernameValid(username):
                error = "Username should be alphanumeric plus '.','_','-'"
                flash(error)
                return render_template('auth/register.html')  # cambio

            if not utils.isPasswordValid(password): #cambio 
                error = 'Password is required.'
                flash(error)
                return render_template('auth/register.html')

            if db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
                flash(error)
                return render_template('auth/register.html') # cambio
            
            if ( not email   or (not utils.isEmailValid(email))):  #cambio
                error =  'Email address invalid.'
                flash(error)
                return render_template('auth/register.html')
            
            if db.execute('SELECT id FROM user WHERE email = ?', (email,)).fetchone() is not None:
                error =  'Email {} is already registered.'.format(email)
                flash(error)
                return render_template('auth/register.html')
            
            if (not utils.isPasswordValid(password)):
                error = 'Password should contain at least a lowercase letter, an uppercase letter and a number with 8 characters long'
                flash(error)
                return render_template('auth/register.html')

            salt = hex(random.getrandbits(128))[2:]
            hashP = generate_password_hash(password + salt)
            number = hex(random.getrandbits(512))[2:]

            db.execute(
                'INSERT INTO activationlink (challenge, state, username, password, salt, email) VALUES (?,?,?,?,?,?)',  # cambio  activate link ojo preguntar
                (number, utils.U_UNCONFIRMED, username, hashP, salt, email)  #tengo dudas  (id, username, email, generate_password_hash(password))
            )
            db.commit()

            credentials = db.execute(
                'Select user,password from credentials where name=?', (utils.EMAIL_APP,)
            ).fetchone()

            content = 'Hello there, to activate your account, please click on this link ' + flask.url_for('auth.activate', _external=True) + '?auth=' + number
            
            send_email(credentials, receiver=email, subject='Activate your account', message=content)
            
            flash('Please check in your registered email to activate your account')
            return render_template('auth/login.html') 

        return render_template('auth/register.html') 
    except:
        return render_template('auth/register.html')

    
@bp.route('/confirm', methods=('GET', 'POST'))  #cambio
def confirm():
    try:
        if g.user:
            return redirect(url_for('inbox.show'))

        if request.method == 'POST': 
            password =  request.form['password'] # cambio
            password1 =  request.form['password1'] #cambio
            authid = request.form['authid']

            if not authid:
                flash('Invalid')
                return render_template('auth/forgot.html')

            if not password:  #cambio
                flash('Password required')
                return render_template('auth/change.html', number=authid)

            if not password1:
                flash('Password confirmation required')
                return render_template('auth/change.html', number=authid)  # cambio

            if password1 != password:  #cambio
                flash('Both values should be the same')
                return render_template('auth/change.html', number=authid)  # cambio

            if not utils.isPasswordValid(password):
                error = 'Password should contain at least a lowercase letter, an uppercase letter and a number with 8 characters long.'
                flash(error)
                return render_template('auth/change.html', number=authid)

            db = get_db()
            attempt = db.execute(
                'SELECT * from forgotlink WHERE challenge = ? AND state = ? AND CURRENT_TIMESTAMP BETWEEN create and validuntil', (authid, utils.F_ACTIVE)
            ).fetchone()
            
            if attempt is not None:
                db.execute(
                    'UPDATE forgotlink SET state = ? WHERE id = ? ', (utils.F_INACTIVE, attempt['id'])
                )
                salt = hex(random.getrandbits(128))[2:]
                hashP = generate_password_hash(password + salt)   
                db.execute(
                    'UPDATE user SET password = ? , salt =? WHERE id = ?', (hashP, salt, attempt['userid'])  # cambiarr
                )
                db.commit()
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid')
                return render_template('auth/forgot.html')

        return render_template('auth.login')  # cambio preguntar
    except:
        return render_template('auth/forgot.html')


@bp.route('/change', methods=('GET', 'POST'))
def change():
    try:
        if g.user:
            return redirect(url_for('inbox.show'))
        
        if request.method == 'GET':  #cambio
            number = request.args['auth'] 
            
            db = get_db()  # cambio
            attempt = db.execute(
                'UPDATE  SET ', (number, utils.F_ACTIVE)  # falta
            ).fetchone()
            
            if attempt is not None:
                return render_template('auth/change.html', number=number)
        
        return render_template('auth/forgot.html')
    except:
        return render_template('auth/forgot.html')


@bp.route('/forgot', methods=('GET', 'POST'))
def forgot():
    try:
        if g.user:
            return redirect(url_for('inbox.show'))
        
        if request.method == 'POST':
            email = request.form['email'] #cambio  
            
            if (not email or (not utils.isEmailValid(email))):  # cambio
                error = 'Email Address Invalid'
                flash(error)
                return render_template('auth/forgot.html')

            db = get_db()
            user = db.execute(
                QUERY, (email,)
            ).fetchone()

            if user is not None:
                number = hex(random.getrandbits(512))[2:]
                
                db.execute(
                    QUERY,
                    (utils.F_INACTIVE, user['id'])
                )
                db.execute(
                    QUERY,
                    (user['id'], number, utils.F_ACTIVE)
                )
                db.commit()
                
                credentials = db.execute(
                    'Select user,password from credentials where name=?',(utils.EMAIL_APP,)
                ).fetchone()
                
                content = 'Hello there, to change your password, please click on this link ' + flask.url_for('auth.change', _external=True) + '?auth=' + number
                
                send_email(credentials, receiver=email, subject='New Password', message=content)
                
                flash('Please check in your registered email')
            else:
                error = 'Email is not registered'
                flash(error)            

        return render_template('auth/forgot.html')  # cambio
    except:
        return render_template('auth/login.html')  # cambio 


@bp.route('/login', methods=('GET', 'POST'))
def login():
    try:
        if g.user:
            return redirect(url_for('inbox.show'))

        if request.method == 'POST': # cambio
            username = request.form['username'] #cambio
            password = request.form['password'] # cambio

            if not username: #cambio
                error = 'Username Field Required'
                flash(error)
                return render_template('auth/login.html') # cambio

            if not password:
                error = 'Password Field Required'
                flash(error)
                return render_template('auth/login.html')  # cambio

            db = get_db() # cambio
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ? ', (username,)   #cambio complete query
            ).fetchone()
            
            if user is not None:  # cambio  ojo puse el not
                error = 'Incorrect username or password'
            elif not check_password_hash(user['password'], password + user['salt']):
                error = 'Incorrect username or password'   

            if error is None:
                session.clear()
                session['user_id'] = user['id']  # cambio
                return redirect(url_for('inbox.show'))

            flash(error)

        return render_template('auth/login.html')  # cambio preguntar forgot
    except:
        return render_template('auth/login.html')  # cambio
        

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')  # cambio

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

        
@bp.route('/logout')
def logout():
    session.clear()  # cambio
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def send_email(credentials, receiver, subject, message):
    # Create Email
    email = EmailMessage()
    email["From"] = credentials['user']
    email["To"] = receiver
    email["Subject"] = subject
    email.set_content(message)

    # Send Email
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(credentials['user'], credentials['password'])
    smtp.sendmail(credentials['user'], receiver, email.as_string())
    smtp.quit()