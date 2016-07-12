from flask import Flask, session, request, redirect, render_template, send_from_directory, url_for

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util

import base64
import datetime

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

mongoConnectionString = 'mongodb://104.197.4.247:27017/'
#mongoConnectionString = 'mongodb://localhost:27017/'

indexPageOption = 1

@app.route("/")
def index():

    if 'username' in session:
        userId = session['userId']
        userName = session['username']
        grp = str(session['group'])
        userdata = {'userId' : str(userId), 'userName' :  str(userName) , 'group' : grp}

        if indexPageOption == 1:
            return render_template("index.html", data = userdata)
        else:
            imageList = listAllImages()
            return render_template("allImagesIndex.html", images = imageList, data = userdata)

    else:
        return redirect(url_for('login'))

@app.route("/login", methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userId = -1

        userId = checkUser(username, password)

        if userId != -1:
            return '{"status":"true"}'
        else:
            return '{"status":"false"}'
    else:
        return render_template("login.html")

def checkUser(username, password):

    passwd = ''
    userId = -1

    try:
        client = MongoClient(mongoConnectionString)
        users = client.imagendb.users

        user = users.find_one({'username' : username})
        passwd = user['password']

        if  passwd == password:
            userId = int(user['userid'])
            session['username'] = username
            session['userId'] = userId
            session['group'] = user['group']

        client.close()
    except Exception as e:
        print e

    return userId

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userId', None)
    session.pop('group', None)
    return redirect(url_for('index'))

@app.route("/listFiles", methods = ['GET', 'POST'])
def listFiles():
    imageList = []
    imgname = request.form['imgname']
    grpname = request.form['grpname']

    try:
        client = MongoClient(mongoConnectionString)
        images = client.imagendb.images

        searchCriteria = {}

        if imgname != '':
            searchCriteria['name'] = imgname

        if grpname != '':
            searchCriteria['group'] = grpname

        for image in images.find(searchCriteria):
            imageList.append(image)

        client.close()
    except Exception as e:
        print e

    return json_util.dumps(imageList)

@app.route("/listAllImages", methods = ['GET', 'POST'])
def listAllImages():
    imageList = []
    userName = str(session['username'])
#     imgname = request.form['imgname']
#     grpname = request.form['grpname']

    try:
        client = MongoClient(mongoConnectionString)
        images = client.imagendb.images
        comments = client.imagendb.comments

        searchCriteria = {}

#         if imgname != '':
#             searchCriteria['name'] = imgname
#
#         if grpname != '':
#             searchCriteria['group'] = grpname

        for image in images.find(searchCriteria):

            imgid = image['imageid']
            imgcomments = comments.find({'imageid': imgid})

            image['comments'] = imgcomments
            image['username'] = userName
            imageList.append(image)

        client.close()
    except Exception as e:
        print e

    return imageList

@app.route("/uploadform")
def uploadForm():
    return render_template("uploadform.html")

@app.route("/changeGrpForm")
def changeGrpForm():
    try:
        client = MongoClient(mongoConnectionString)
        groups = client.imagendb.groups

        g = groups.find_one()

        gdata = {'groups' : g['groups']}

        client.close()
    except Exception as e:
        return str(e)

    return render_template("changegroup.html", data = gdata)

@app.route("/changeUserGroup", methods = ['GET', 'POST'])
def changeUserGroup():

    userName = str(session['username'])
    newGroup = request.form['group']

    print newGroup
    try:
        client = MongoClient(mongoConnectionString)
        users = client.imagendb.users

        result = users.update_one({'username':userName}, {'$set':{'group':newGroup}})
        print result.matched_count

        if result.matched_count == 1:
            session['group'] = newGroup

        client.close()
    except Exception as e:
        return str(e)

    return redirect(url_for('index'))

@app.route("/upload", methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        uploadFile = request.files['file']
        comment = request.form['comment']
        size = request.form['size']
        userId = session['userId']
        userName = str(session['username'])
        group = str(session['group'])
        imageFormat = uploadFile.filename.split('.')[1]
        imgStr = base64.b64encode(uploadFile.read())
        uploadtime = datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")

        try:
            client = MongoClient(mongoConnectionString)
            images = client.imagendb.images
            imagedata = client.imagendb.imagedata


            imageId = imagedata.insert_one({'image' : imgStr}).inserted_id

            images.insert_one({'imageid': str(imageId),
                               'userid': str(userId),
                               'size': size,
                               'format' : imageFormat,
                               'group' : group,
                               'uploadtime' : uploadtime,
                               'name': uploadFile.filename})

            if comment != '':
                comments = client.imagendb.comments

                comments.insert_one({'imageid': str(imageId),'username':userName,'comment' : comment})

            client.close()
        except Exception as e:
            return str(e)


        return redirect(url_for('index'))

@app.route('/deleteImage', methods = ['POST'])
def deleteImage():
    imageId = str(request.form['imageId'])
    try:
        client = MongoClient(mongoConnectionString)
        imagedata = client.imagendb.imagedata
        images = client.imagendb.images
        comments = client.imagendb.comments

        imagedata.remove({'_id': ObjectId(imageId)})
        images.remove({'imageid' :  imageId})
        comments.remove({'imageid' :  imageId})

        client.close()

        return '{"status":"success"}'
    except Exception as e:
        print e
        return '{"status":"error"}'

@app.route('/getImage')
def getImage():
    imageId = request.args['imageId']
    try:
        client = MongoClient(mongoConnectionString)
        imagedata = client.imagendb.imagedata

        imgData = imagedata.find_one({'_id': ObjectId(imageId)})

        client.close()
    except Exception as e:
        print e
        return ''

    return imgData['image'].decode('base64')

@app.route('/getImageViewer', methods = ['POST'])
def getImageViewer():
    imgid = request.form['imageId']
    userName = str(session['username'])
    try:
        client = MongoClient(mongoConnectionString)
        comments = client.imagendb.comments

        imgcomments = comments.find({'imageid': imgid})

        client.close()
        data = {'imageid' : imgid, 'comments' : imgcomments, 'username' : userName}

        return render_template("imageviewer.html", imageData = data)
    except Exception as e:
        print str(e)
        return render_template("imageviewer.html")

@app.route('/addComment', methods = ['POST'])
def addComment():
    imageId = request.form['imageId']
    comment = request.form['comment']
    userName = str(session['username'])
    try:
        client = MongoClient(mongoConnectionString)
        comments = client.imagendb.comments

        commentId = comments.insert_one({'imageid': imageId,'username':userName,'comment' : comment}).inserted_id

        return '{"status":"success","comment" : "' + comment + '", "cid" : "' + str(commentId) + '"}'
        client.close()
    except Exception as e:
        print e
        return '{"status":"error"}'

@app.route('/deleteComment', methods = ['POST'])
def deleteComment():
    commentId = str(request.form['cid'])

    try:
        client = MongoClient(mongoConnectionString)
        comments = client.imagendb.comments

        comments.remove({'_id': ObjectId(commentId)})

        client.close()
        return '{"status":"success"}'
    except Exception as e:
        print e
        return '{"status":"error"}'

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)

# if __name__ == '__main__':
#      app.run(debug = True)
#    app.run()