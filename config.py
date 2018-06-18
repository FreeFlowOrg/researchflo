import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = 'my precious'

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')

#AWS credentials
S3_BUCKET                 = "zappa-jepozm5pw"
S3_KEY                    = ""
S3_SECRET                 = ""
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

#Mail settings
