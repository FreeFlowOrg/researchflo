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
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


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
                # publisher login


        if not user:
            error = 'Incorrect credentials'

    return render_template('forms/login.html', form=form, error=error)

@app.route('/paper_upload',methods=['POST','GET'])
def paper_upload(): # Journal Upload
    if  request.method == 'POST' and 'file' in request.files:
        filename = files.save(request.files['file'])

        doc = Journal(title=request.form['Title'],user_email=session['email'],
                    domain=request.form['domain'],status="Submission received",filename=filename)
        doc.save()
        flash('Journal Submitted')
        return redirect(url_for('dashboard'))

@app.route('/download/<filename>',methods=['POST','GET'])
def download(filename):
    try:
        return send_file(safe_join(app.config['UPLOADED_FILES_DEST'],filename),as_attachment=True)
    except Exception as e:
        return str(e)

@app.route('/narrow_down',methods=['POST','GET'])
def narrow_down():
    try:
        if request.form['select-domain'] == 'all':
            files = Journal.query.all()
        else:
            files = Journal.query.filter_by(domain=request.form['select-domain']).all()
        return render_template('pages/sub.html',files=files)
    except Exception as e:
        return str(e)


@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    if session['user_type'] == 'Publisher':
        return render_template('pages/pub.html',papers=Journal.query.filter_by(user_email=session['email']).all(),
                                date=datetime.datetime.now(),comments=Comments.query.all())

    elif session['user_type'] == 'Reviewer':
        return render_template('pages/rev.html')

    elif session['user_type'] == 'Subscriber':
        return render_template('pages/sub.html',files=Journal.query.all())

    return redirect(url_for('home'))

@app.route('/logout',methods=['POST','GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/paper_error_submit',methods=['POST','GET'])
def paper_error_submit():
        comment = Comments(user=request.form['Email'],commenter=session['email'],title=request.form['Title'],desc=request.form['Detailed Description'])
        comment.save()
        flash('Relevance/Errors in paper notified')
        return redirect(url_for('dashboard'))

@app.route('/paper_error',methods=['POST','GET'])
def paper_error():
    email = request.form['Email']
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
    return render_template('forms/forgot.html', form=form)

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
