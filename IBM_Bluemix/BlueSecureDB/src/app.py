from flask import Flask, session, request, redirect, render_template, send_from_directory, url_for, Response
from simplecrypt import encrypt, decrypt
from mysql.connector import Error

import os
import json
import mysql.connector

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

mysql_conn = None
passphrase = "BLUEMIXENCRY"

host = 'us-cdbr-iron-east-04.cleardb.net'
port = 3306
dbusername = 'b7b209159c9b5c'
dbpassword = 'acdf1907'
dbname = 'ad_e6a92da2c27cfca'

@app.route("/")
def index():

    if 'username' in session:
        return render_template("index.html")
    else:
        return redirect(url_for('login'))

@app.route("/login", methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        isValidUser = checkUser(username, password)

        if isValidUser:
            session['username'] = username
            return '{"status":"true"}'
        else:
            return '{"status":"false"}'
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

def checkUser(username, password):

    passwd = ''

    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)

        query = "SELECT password FROM users WHERE username = %s"
        cursor = mysql_conn.cursor()
        cursor.execute(query,(username,))

        passwd = cursor.fetchone()[0]

        cursor.close()
        mysql_conn.close()
    except Exception as e:
        print(e)
        print('Unable to select user')

    if passwd == password:
        return True
    else:
        return False

@app.route("/upload", methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        size = request.form['size']
        username = session['username']

        fileContent = file.read()

        try:
            version = 1
            mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
            cursor = mysql_conn.cursor()

            query = "SELECT MAX(version) FROM files WHERE username = %s and filename = %s"
            cursor.execute(query, (username, file.filename))

            row = cursor.fetchone()
            fCount = row[0]

            if fCount != None and fCount >= 1:
                version = fCount + 1

            query = "INSERT INTO files(filename,description,size,contents, version, username) values(%s,%s,%s,%s,%s,%s)"

            args = (file.filename, description, size, fileContent, version, username)

            cursor.execute(query, args)
            mysql_conn.commit()
            mysql_conn.close()
            return redirect(url_for('index'))
        except Error as e:
            print(e)
            return redirect(url_for('index'))

@app.route("/downloadFile/<fileName>/<version>", methods = ['GET'])
def downloadFile(fileName, version):

    username = session['username']

    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)

        cursor = mysql_conn.cursor()
        query = "SELECT contents FROM files WHERE username = %s and filename = %s and version = %s"
        cursor.execute(query, (username, fileName, version))

        row = cursor.fetchone()

        cursor.close()
        mysql_conn.close()

        if row != None:
            return Response(row[0], headers={"Content-Disposition":"attachment;filename=" + fileName})
    except Error as e:
        print(e)
        return '{}'

@app.route("/listFiles", methods = ['GET', 'POST'])
def listFiles():

    username = session['username']
    fileList = {}
    files = []

    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)

        query = "SELECT filename, description, version, size from files WHERE username = %s"
        cursor = mysql_conn.cursor()
        cursor.execute(query,(username,))

        rows = cursor.fetchall()

        for row in rows:
            fileinfo = {}
            fileinfo['filename'] = row[0]
            fileinfo['description'] = row[1]
            fileinfo['version'] = row[2]
            fileinfo['size'] = row[3]

            files.append(fileinfo)

        cursor.close()
        mysql_conn.close()
    except Error as e:
        print(e)

    fileList['files'] = files

    return json.dumps(fileList)

@app.route("/deleteFile/<fileName>/<version>", methods = ['GET', 'POST'])
def deleteFile(fileName, version):

    username = session['username']

    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)

        cursor = mysql_conn.cursor()
        query = "DELETE FROM files WHERE username = %s and filename = %s and version = %s"
        cursor.execute(query, (username, fileName, version))

        mysql_conn.commit()
        mysql_conn.close()
        return '{"status":"success"}'
    except Error as e:
        print(e)
        return '{"status":"error"}'


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)

appport = os.getenv('PORT', '5000')

if __name__ == '__main__':
    #app.run(debug = True)
    app.run(host='0.0.0.0', port=int(appport))
