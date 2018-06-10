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
S3_KEY                    = "AKIAJ7FYBZBFOY4DUJ5A"
S3_SECRET                 = "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"
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
