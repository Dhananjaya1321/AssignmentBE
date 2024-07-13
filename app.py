from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:samu1234weera@3306/applicationdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'  # Local upload folder

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    def _repr_(self):
        return f'<User {self.name}>'

@app.route('/users', methods=['POST'])
def create_user():
    data = request.form
    name = data['name']
    dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    image_file = request.files['image']

    # Save image to S3
    if image_file:
        image_url = upload_file_to_s3(image_file)
    else:
        image_url = None

    new_user = User(name=name, dob=dob, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

def upload_file_to_s3(file):
    s3_client = boto3.client('s3', region_name='AKIA3FLDXXLZN6FXXKH3')
    bucket_name = 'applications3'
    object_name = f'{app.config["UPLOAD_FOLDER"]}/{file.filename}'

    try:
        response = s3_client.upload_fileobj(file, bucket_name, object_name)
    except ClientError as e:
        print(e)
        return None

    return f'https://{bucket_name}.s3.amazonaws.com/{object_name}'

if __name__ == '_main_':
    app.run(debug=True)