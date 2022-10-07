from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_file
)

from app.auth import login_required
from app.db import get_db

bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@bp.route("/getDB")
@login_required
def getDB():
    return send_file(current_app.config['DATABASE'], as_attachment=True)


@bp.route('/show')
@login_required
def show():
    db = get_db()
    userId= g.user['id']
    messages = db.execute(
        'SELECT u.username As username, m.subject AS subjet, m.body AS body from (select * from message where to_id= ?', (userId)
        ).fetchall()
        #ORDER BY created DESC # cambio 
    

    return render_template('inbox/show.html', messages=messages) # cambio


@bp.route('/send', methods=('GET', 'POST'))
@login_required
def send():
    if request.method == 'POST':        
        from_id = g.user['id']
        to_username = request.form['to']
        subject = request.form['subject']
        body = request.form['body']

        db = get_db()
       
        if not to_username:
            flash('To field is required')
            return render_template('inbox/send.html')  # cambio
        
        if not subject:  # cambio
            flash('Subject field is required')
            return render_template('inbox/send.html')
        
        if not body:  # cambio
            flash('Body field is required')
            return render_template('inbox/send.html')    # cambio
        
        error = None    
        userto = None 
        
        userto = db.execute(
            'SELECT * FROM user WHERE username = ?', (to_username,)  # cambio
        ).fetchone()
        
        if userto is None:
            error = 'Recipient does not exist'
     
        if error is not None:
            flash(error)
        else:
            db = get_db() # cambio
            db.execute(
                'INSERT INTO menssage (from_id, to, subject, body)'
                ' VALUES (?, ?, ?, ?)',
                (g.user['id'], userto['id'], subject, body)
            )
            db.commit()

            return redirect(url_for('inbox.show'))

    return render_template('inbox/send.html')