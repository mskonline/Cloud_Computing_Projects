from flask import Flask, request, redirect, render_template, send_from_directory, url_for, Response
from simplecrypt import encrypt, decrypt

import os
import swiftclient.client as swiftclient
import json

app = Flask(__name__)

storageSetup = False
bluemix_conn = None
container_name = "bluemix_container"
passphrase = "BLUEMIXENCRY"

@app.route("/")
def index():

    global storageSetup

    if not storageSetup:
        print("Connecting to BlueMix Storage...")

        connectToStorage()

        global bluemix_conn
        if bluemix_conn:
            print("Connection is setup")

    return render_template("index.html")

@app.route("/upload", methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        #file.save(UPLOAD_LOCATION + file.filename);

        global bluemix_conn, passphrase

        if not bluemix_conn:
            print("Connection not setup...")
            return

        fileContent = encrypt(passphrase, file.read())

        try:
            bluemix_conn.put_object(container_name,
                file.filename,
                contents= fileContent,
                content_type='text/plain')

            return redirect(url_for('index'))
        except:
            return 'Error in uploading file'

@app.route("/downloadFile/<fileName>", methods = ['GET'])
def downloadFile(fileName):

    global bluemix_conn, passphrase

    try:
        obj = bluemix_conn.get_object(container_name, fileName)
        mimeType = obj[0]['content-type']
        data = decrypt(passphrase, obj[1])
        return Response(data, mimetype=mimeType, headers={"Content-Disposition":"attachment;filename=" + fileName})
    except:
        return "{}"

@app.route("/listFiles", methods = ['GET', 'POST'])
def listFiles():

    global bluemix_conn

    try:
        container = bluemix_conn.get_container(container_name)
    except:
        print("Error in getting the container")

    fileList = {}
    files = []

    for container in bluemix_conn.get_account()[1]:
        for data in bluemix_conn.get_container(container['name'])[1]:
            fileinfo = {}
            fileinfo['name'] = data['name']
            fileinfo['size'] = data['bytes']
            fileinfo['lastModified'] = data['last_modified']
            files.append(fileinfo)

    fileList['files'] = files
    return json.dumps(fileList)

@app.route("/deleteFile/<fileName>", methods = ['GET', 'POST'])
def deleteFile(fileName):

    global bluemix_conn

    try:
        bluemix_conn.delete_object(container_name, fileName)
        return '{"status":"success"}'
    except:
        return '{"status":"error"}'

def connectToStorage():

    global storageSetup

    auth_url = "" + "/v3"
    project = ""
    projectId = ""
    region = ""
    userId = ""
    username = ""
    password = ""
    domainId = ""
    domainName = ""

    global bluemix_conn

    try:
        bluemix_conn = swiftclient.Connection(
                key=password,
                authurl=auth_url,
                auth_version='3',
                os_options={"project_id": projectId,
                            "user_id": userId,
                            "region_name": region})
    except:
        print("Error connecting BlueMix")
        storageSetup = False
        return None

    try:
        container = bluemix_conn.get_container(container_name)
    except:
        print("Container not found. Creating...")
        bluemix_conn.put_container(container_name)

    storageSetup = True

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)

appport = os.getenv('PORT', '5000')

if __name__ == '__main__':
    #app.run(debug = True)
    app.run(host='0.0.0.0', port=int(appport))
