from flask import Flask, session, request, redirect, render_template, send_from_directory, url_for

from pydocumentdb import document_client

import sys, os
import json
import base64
import datetime

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

host = 'https://quicknotes.documents.azure.com:443/'
masterKey = 'Q9N3CPUETiVnk6BXUWFfP0bfWN1XKSfmu4SSUuEbgUEatxvyD6kLqJvhiIdU3ZBK1vOI8UznFZRrMdKiBPOVBQ=='

DATABASE = 'quicknotesdb'
COLLECTION = 'quicknotes'

COLLECTION_ID = 'dbs/lk4bAA==/colls/lk4bAK7UHAA='
DOCUMENT_ID = 'dbs/lk4bAA==/colls/lk4bAK7UHAA=/docs/'

@app.route("/")
def index():

    if 'username' in session:

        userName = session['username']
        grp = str(session['group'])
        userdata = {'userName' :  str(userName) , 'group' : grp}

        return render_template("index.html", data = userdata)
    else:
        return render_template("login.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        isValid = False

        isValid = checkUser(username, password)

        if isValid:
            return '{"status":"true"}'
        else:
            return '{"status":"false"}'
    else:
        return render_template("login.html")

def checkUser(username, password):

    try:
        client = document_client.DocumentClient(host, {'masterKey': masterKey})
        databases = list(client.ReadDatabases())

        if not databases:
            return False

        db = databases[0]

        collections = list(client.QueryCollections(
                        db['_self'],
                        {
                            'query': 'SELECT * FROM root r WHERE r.id=@id',
                            'parameters': [
                                {'name':'@id', 'value': COLLECTION}
                            ]
                        }))

        if (len(collections) > 0):
            collection = collections[0]

        document = list(client.QueryDocuments(
                    collection['_self'],
                    {
                        'query': 'SELECT * FROM root r WHERE r.username=@username',
                        'parameters': [
                            {'name':'@username', 'value': username}
                        ]
                    }))

        if(len(document) == 1):
            user = document[0]
            if  user['password'] == password:
                session['username'] = username
                session['group'] = user['group']

                return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return False

@app.route("/listFiles", methods = ['GET', 'POST'])
def listFiles():

    username = session['username']

    subject = ''
    orderBy = ''
    order = ''

    try:
        subject = request.form['subject']
        orderBy = request.form['orderBy']
        order = request.form['order']
    except Exception as e:
        print ''

    try:
        client = document_client.DocumentClient(host, {'masterKey': masterKey})
        databases = list(client.ReadDatabases())

        if not databases:
            return False

        db = databases[0]

        collections = list(client.QueryCollections(
                        db['_self'],
                        {
                            'query': 'SELECT * FROM root r WHERE r.id=@id',
                            'parameters': [
                                {'name':'@id', 'value': COLLECTION}
                            ]
                        }))

        if (len(collections) > 0):
            collection = collections[0]

        query = 'SELECT * FROM root r WHERE r.owner=@username AND r.type="note"'

        if subject != '':
            query += ' AND r.subject=@subject'

        if orderBy != '':
            query += ' ORDER BY r.' + orderBy + ' ' + order

        print query

        documents = list(client.QueryDocuments(
                    collection['_self'],
                    {
                        'query': query,
                        'parameters': [
                            {'name':'@username', 'value': username},
                            {'name':'@subject', 'value': subject}
                        ]
                    }))

        print len(documents)
        return json.dumps(documents)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


    return json.dumps('[]')

@app.route("/upload", methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        try:
            contenttype = request.form['contenttype']
            userName = str(session['username'])
            subject = request.form['subject']
            priority = request.form['priority']

            data_document = {}
            data_document['type'] = 'data'
            data_document['owner'] = userName

            if contenttype == 'img':
                content = request.files['file']
                comment = request.form['comment']
                size = int(request.form['size'])

                data_document['data'] = base64.b64encode(content.read())
                data_document['comments'] = [comment]
            else:
                note = request.form['note']

                data_document['data'] = note
                size = sys.getsizeof(note)

            client = document_client.DocumentClient(host, {'masterKey': masterKey})

            d = client.CreateDocument(COLLECTION_ID, data_document)

            meta_document = {}
            meta_document['type'] = 'note'
            meta_document['subject'] = subject
            meta_document['owner'] = userName
            meta_document['priority'] = int(priority)
            meta_document['size'] = size
            meta_document['dataid'] = d['_rid']
            meta_document['contenttype'] = contenttype
            meta_document['uploadtime'] = datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")

            client.CreateDocument(COLLECTION_ID, meta_document)

        except Exception as e:
            return str(e)


        return redirect(url_for('index'))

@app.route('/getNoteViewer', methods = ['POST'])
def getNoteViewer():

    dataid = request.form['did']
    ctype = request.form['ctype']

    if ctype == 'img':
        return render_template("noteviewer.html", dataId = dataid, contenttype = ctype)
    else:
        try:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})

            query = 'SELECT * FROM root r WHERE r._rid=@id'

            documents = list(client.QueryDocuments(
                        COLLECTION_ID,
                        {
                            'query': query,
                            'parameters': [
                                {'name':'@id', 'value': dataid}
                            ]
                        }))

            if len(documents) <= 0:
                return ''

            data = documents[0]['data']
            return render_template("noteviewer.html", data = data, contenttype = ctype)
        except Exception as e:
            print e

    return render_template("noteviewer.html")

@app.route('/getImage')
def getImage():

    data_id = request.args['dataid']

    try:
        client = document_client.DocumentClient(host, {'masterKey': masterKey})

        query = 'SELECT * FROM root r WHERE r._rid=@id'

        documents = list(client.QueryDocuments(
                    COLLECTION_ID,
                    {
                        'query': query,
                        'parameters': [
                            {'name':'@id', 'value': data_id}
                        ]
                    }))

        if len(documents) <= 0:
            return ''

        imgData = documents[0]['data']
    except Exception as e:
        print e
        return ''

    return imgData.decode('base64')

@app.route('/deleteNote', methods = ['GET'])
def deleteNote():
    r_id = request.args['rid']
    data_id = request.args['dataid']

    try:
        client = document_client.DocumentClient(host, {'masterKey': masterKey})

        document_link = DOCUMENT_ID + r_id

        d = client.DeleteDocument(document_link)

        document_link = DOCUMENT_ID + data_id

        d = client.DeleteDocument(document_link)

        return '{"status":"success"}'
    except Exception as e:
        print e

    return '{"status":"failure"}'

@app.route("/uploadImageform")
def imageUploadForm():
    return render_template("uploadImageform.html")

@app.route("/uploadNoteform")
def noteUploadForm():
    return render_template("uploadNoteform.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('group', None)
    return redirect(url_for('index'))

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)

if __name__ == '__main__':
#    app.run(debug = True)
    app.run()