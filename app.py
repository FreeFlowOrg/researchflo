#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask,flash,Blueprint,render_template,request,redirect,session,url_for,abort,send_file,safe_join
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from models import *
import bcrypt
from werkzeug import secure_filename, FileStorage
from flask_uploads import UploadSet,configure_uploads,DOCUMENTS
from flask_mail import Mail,Message
import datetime
import time
import random
from sqlalchemy.pool import StaticPool
import boto3,botocore
import string

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# File upload config
files = UploadSet('files',DOCUMENTS)
app.config['UPLOADED_FILES_DEST'] = 'static/journals'
app.config['UPLOADED_FILES_ALLOW']=['doc','docx']
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'skilllauncher7@gmail.com',
    MAIL_PASSWORD = 'skill7launcher'
))
mail= Mail(app)
configure_uploads(app,files)

# /file upload config

#----------------------------------------------------------------------------#
# //App Config.
#----------------------------------------------------------------------------#


# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''#----------------------------------------------------------------------------#
s3 = boto3.client('s3')

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            kind = user.type
        #  login
            if user.type == 'Reviewer':
                if bcrypt.hashpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
                    session['email'] = form.email.data
                    session['user_type'] = kind
                    return redirect(url_for('dashboard'))
                # reviewer login
            elif user and user.type == 'Subscriber' :
                if bcrypt.hashpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
                    session['email'] = form.email.data
                    session['user_type'] = kind
                    return redirect(url_for('dashboard'))
                    # subscriber login
            elif user and user.type == 'Publisher' :
                if bcrypt.hashpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
                    session['email'] = form.email.data
                    session['user_type'] = kind
                    return redirect(url_for('dashboard'))
                    #publisher login
            elif user and user.type == 'Editor' :
                if bcrypt.hashpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
                    session['email'] = form.email.data
                    session['user_type'] = kind
                    return redirect(url_for('dashboard'))

        elif not user:
            error = 'Incorrect credentials'
            flash(error)
            return redirect(url_for('login'))

    return render_template('forms/login.html', form=form, error=error)

@app.route('/paper_upload',methods=['POST','GET'])
def paper_upload(): # Journal Upload
    if  request.method == 'POST' and 'file' in request.files:
        # for Amazon S3
        os.chdir('/tmp')
        filename = files.save(request.files['file'])
        file = request.files['file']
        doc = Journal(title=request.form['Title'],user_email=session['email'],
                    domain=request.form['domain'],status="submission received",filename=filename,date=datetime.datetime.utcnow())
        doc.save()
        data = open(app.config['UPLOADED_FILES_DEST']+'/'+filename, 'rb')
        s3 = boto3.client('s3')
        s3.put_object(Bucket=app.config['S3_BUCKET'], Key=filename, Body=data)
        flash('Your paper has been sent for Review. You can check your review status in the Submitted Papers section')
        users=User.query.all()
        emails=users.email
        msg = Message('A new paper is up on the open web space!',sender='skilllauncher7@gmail.com',recipients=emails)
        msg.html=render_template('pages/new_paper.html',new_paper=url_for('dashboard',_external=True), _external=True)
        mail.send(msg)
        return redirect(url_for('dashboard'))

@app.route('/narrow_down',methods=['POST','GET'])
def narrow_down():
    if request.method=='POST':
        if session['user_type'] == 'Subscriber':
            try:
                if request.form['select-domain'] == 'all':
                    files = Journal.query.filter(Journal.status=='Accepted').all()

                else:
                    files = Journal.query.filter(Journal.domain==request.form['select-domain']).all()
                return render_template('pages/sub.html',files=files)
            except Exception as e:
                return str(e)

        if session['user_type'] == 'Reviewer':
            if request.form['select-domain'] == "all":
                files = Journal.query.filter_by(status="submission received").all()
                return render_template('pages/rev.html',files=files)
            else:
                files = Journal.query.filter_by(status="submission received").all()
                return render_template('pages/rev.html',files=files)

        elif session['user_type'] == 'Editor':
            if request.form['select-domain'] == 'all':
                files = Journal.query.filter(Journal.status=='Under Editor Review').all()
                return render_template('pages/editor.html',files=files)
            else:
                files = Journal.query.filter(Journal.domain==request.form['select-domain'] and Journal.status == 'Under Editor Review').all()
                return render_template('pages/editor.html',files=files)

@app.route('/narrow_down_peer_review',methods=['POST','GET'])
def narrow_down_peer_review():
    if request.method=='POST':
        try:
            if request.form['select-domain'] == 'all':
                files = Journal.query.filter(Journal.status=='submission received').all()
                return render_template('pages/sub_peer.html',files=files)
            else:
                files = Journal.query.filter(Journal.domain==request.form['select-domain']).all()
                return render_template('pages/sub_peer.html',files=files)
        except Exception as e:
            return str(e)

### DASHBOARD
@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    if session['user_type'] == 'Publisher':
        return render_template('pages/pub.html',papers=Journal.query.filter(Journal.user_email==session['email']).all(),
                                comments=Comments.query.filter_by(user=session['email']).all())

    elif session['user_type'] == 'Reviewer':
        return render_template('pages/rev.html',files=Journal.query.filter(Journal.status=='Peer Review Completed').all())

    elif session['user_type'] == 'Subscriber':
        return render_template('pages/sub.html',files=Journal.query.filter(Journal.status=='Accepted').all())
    elif session['user_type'] == 'Editor':
        return render_template('pages/editor.html',files=Journal.query.filter(Journal.status=='Under Editor Review').all())

    return redirect(url_for('home'))







# paper logic

@app.route('/paper_editor/<title>',methods=['POST','GET'])
def paper_editor(title):
    paper = Journal.query.filter(Journal.title==title).first()
    paper.status = 'Under Editor Review'
    paper.save()
    flash('The Journal Paper has been reviewed under a Reviewer. Information will be communicated to the Publisher.')
    return redirect(url_for('dashboard'))

@app.route('/paper_peer_review/<title>',methods=['POST','GET'])
def paper_peer_review(title):
    paper=Journal.query.filter_by(title=title).first()
    paper.status = 'Under Peer Review'
    paper.save()
    flash('The Journal Paper has been reviewed. Information will be communicated to the Publisher.')
    return redirect(url_for('dashboard'))

@app.route('/paper_revision/<title>',methods=['POST','GET'])
def paper_revision(title):
    paper=Journal.query.filter_by(title=title).first()
    paper.status = 'Needs Revision'
    paper.save()
    flash('The Journal Paper has been reviewed. Information will be communicated to the Publisher.')
    return redirect(url_for('dashboard'))

@app.route('/paper_reject/<title>',methods=['POST','GET'])
def paper_reject(title):
    paper = Journal.query.filter_by(title=title).first()
    paper.status = 'Rejected'
    paper.save()
    flash('The Journal Paper has been reviewed. Information will be communicated to the Publisher.')
    return redirect(url_for('dashboard'))

@app.route('/paper_accept/<title>',methods=['POST','GET'])
def paper_accept(title):
    paper = Journal.query.filter_by(title=title).first()
    paper.status = 'Accepted'
    paper.save()
    flash('The Journal Paper has been reviewed. Information will be communicated to the Publisher.')
    return redirect(url_for('dashboard'))

@app.route('/sub_peer',methods=['POST','GET'])
def sub_peer():
    return render_template('pages/sub_peer.html',files=Journal.query.filter(Journal.status=='submission received').all())








@app.route('/logout',methods=['POST','GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/check_notification',methods=['POST','GET'])
def check_notification():
    data = Comments.query.filter_by(user = session['email']).first()
    if data != None:
        data.remove()
    return redirect(url_for('dashboard'))


@app.route('/paper_error_submit',methods=['POST','GET'])
def paper_error_submit():
        comment = Comments(user=request.form['Email'],commenter=session['email'],title=request.form['Title'],desc=request.form['Detailed Description'])
        comment.save()
        data = Journal.query.filter(Journal.title==request.form['paper-title']).first()
        data.status='Peer Review Completed'
        data.save()
        flash('Relevance/Errors in paper notified. Peer Review for the respective paper completed')
        return redirect(url_for('dashboard'))

@app.route('/paper_error',methods=['POST','GET'])
def paper_error():
    email = form.email.data
    return render_template('pages/paper_error.html',email=email)

@app.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt(10))
        if request.form['type'] == 'sub':
            user_type = 'Subscriber'
        elif request.form['type'] == 'rev':
            user_type = 'Reviewer'
        elif request.form['type'] == 'pub':
            user_type = 'Publisher'
        data = User(name=form.name.data,email=form.email.data,password=hashed_password.decode('utf-8'),type=user_type)
        data.save()
        return redirect(url_for('home'))

    return render_template('forms/register.html', form=form)


@app.route('/forgot',methods=['POST','GET'])
def forgot():
    form = ForgotForm(request.form)
    forgot_url = url_for('reset',_external=True)
    if request.method == 'POST':
        users = User.query.all()
        for user in users:
            if user.email == form.email.data:
                msg = Message('Reset Password',sender='skilllauncher7@gmail.com',recipients=[form.email.data])
                msg.html=render_template('pages/forgot_password.html',forgot_url=forgot_url, _external=True)
                mail.send(msg)
                session.clear()
                session['user_email'] = form.email.data
                flash('A reset confirmation e-mail has been sent to the specified email address')
                return redirect(url_for('home'))
        flash('The provided mail is not a valid email address.')
        return redirect(url_for('forgot'))
    if request.method == 'GET':
        return render_template('forms/forgot.html', form=form)

@app.route('/reset',methods=['POST','GET'])
def reset():
    form = ResetForm(request.form)
    if request.method=='POST':
        if form.password.data!=form.repeat_password.data:
            flash('Passwords do not match')
            return redirect(url_for('reset'))
        hashed_password_new = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt(10))
        data = User.query.filter_by(email=session['email']).first()
        data.password=hashed_password_new
        data.save()
        session.clear()
        flash('Your password has been reset successfully. Please login with the updated credentials.')
        return redirect(url_for('login'))
    else:
        return render_template('forms/reset.html')



# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
