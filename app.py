from __future__ import print_function
from flask import Flask, request, render_template
import mysql.connector
from Google import Create_Service
from googleapiclient.http import MediaFileUpload
from flask import redirect, url_for
import tempfile
import os
CLIENT_SECRET_FILE = 'client_secret_file.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)



app = Flask(__name__)
db = mysql.connector.connect(host="127.0.0.1", user="root", password="Cj10856672", database="Bomberdb")


@app.route('/submit', methods=['POST'])
def submit():
    try:
        email = request.form['email']
        sender = request.form['sender']
        body = request.form['body']
        folder_file = request.files['folder']
        print("email:", email)
        print("sender:", sender)
        print("body:", body)
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Created temporary directory: {temp_dir}")
            folder_path = os.path.join(temp_dir, folder_file.filename)
            folder_file.save(folder_path)
            print("folder:", folder_path)

            folder_id = "1R-82SPa93htuMv729ZdUp1RPUnfgm_Wt"

            file_name = folder_file.filename
            mime_type = folder_file.mimetype

            file_metadata = {
                'name': file_name,
                'mime_type': mime_type,
                'parents': [folder_id],
            }

            media = MediaFileUpload(folder_path, mimetype=mime_type)

            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='webViewLink'
            ).execute()

            folder_link = uploaded_file.get('webViewLink')
            print("folder_link:", folder_link)


        cursor = db.cursor()
        query = "INSERT INTO mytable (email, email_password, body, folder) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (email, sender, body, folder_link))
        db.commit()
    except Exception as e:
        print(e)
        return "Error processing form data"

    return redirect(url_for('submitted'))

@app.route('/')
def index():
    return render_template('form.html')


@app.route('/submitted')
def submitted():
    message = "Data has been successfully uploaded to database and Google Drive!"
    return render_template('submitted.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)