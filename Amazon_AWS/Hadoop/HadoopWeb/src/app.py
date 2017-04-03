from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from sklearn.cluster import KMeans

import os
import time
import subprocess
import math
import csv
import numpy as np
import json

app = Flask(__name__)

UPLOAD_FOLDER = '/var/www/HadoopCloud/hadoopupload'
HADOOP_OUTPUT = '/var/www/HadoopCloud/hadoopoutput'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/upload", methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        #uploadTime = int(request.form.get('uploadTime'))
        #currentTime = int(round(time.time() * 1000))
        #totalTime = currentTime - uploadTime
        
        # Save the file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Place the csv into hadoop hdfs
        hadoopInputFile = UPLOAD_FOLDER + '/' + filename
        command = '/usr/local/hadoop/bin/hadoop fs -put ' + hadoopInputFile + ' /cloud/data'
        returnCode = subprocess.call(command, shell=True)
        
        if returnCode != 0:
            print 'Error occurred in placing file in Hadoop'
        
        # Run the hadoop command
        folderName = 'output_' + str(math.ceil(time.time()))
        outputFolder = '/cloud/' + folderName
        command = '/usr/local/hadoop/bin/hadoop jar /home/hduser/jar/CloudProject.jar DataAnalytics2 /cloud/data '  + outputFolder
        returnCode = subprocess.call(command, shell=True)
        
        if returnCode != 0:
            print 'Error occurred in running Hadoop'
        
        # Get the output file
        command = '/usr/local/hadoop/bin/hadoop fs -get ' + outputFolder + ' ' + HADOOP_OUTPUT
        returnCode = subprocess.call(command, shell=True)
        
        resultOutput = ''
        
        for filename in os.listdir(HADOOP_OUTPUT + '/' + folderName):
            
            if filename != '_SUCCESS':
                f = open(HADOOP_OUTPUT + '/' + folderName + '/' + filename, 'r')
                resultOutput += f.read()
                
                f.close()
        
        return '<div style="white-space:pre">' + resultOutput + '</div>'


@app.route("/doCluster", methods = ['GET', 'POST'])
def doCluster():
    
    if request.method == 'POST':
        csv_data = csv.reader(open("/home/hduser/data/titanic.csv", 'r'))
        
        numClusters = 4
        values = []
        count = 0
        
        for row in csv_data:
            age = 0
            try:
                age = int(row[4])
            except:
                continue
            
            count+=1
            
            values.append([count, age])    
        
        
        narray = np.array(values)
        
        km = KMeans(numClusters).fit(narray)
        labels = km.labels_
        centroids = []
        
        for v in km.cluster_centers_:
            centroids.append([v[0],v[1]])
        
        data = {'numClusters': numClusters, 'centroids' : centroids}
        
        for i in range(0, numClusters):
            ds = narray[np.where(labels==i)]
            cdata = []
            dist = 0
            max = 0
            centroid = centroids[i]
            
            for d in ds:
                cdata.append([d[0],d[1]])
                
                dist = math.hypot(centroid[0] - d[0], centroid[1] - d[1])
                if dist >= max:
                    max = dist
                    
            data['maxdist_' + str(i)] = max
            data['cluster_' + str(i)] = cdata
            
        return json.dumps(data)
    else:
        return render_template('doCluster.html')

@app.route("/doCustomCluster", methods = ['GET', 'POST'])
def doCustomCluster():
    
    if request.method == 'POST':
        
        numClusters = int(request.form['numClusters'])
        col1 = int(request.form['col1'])
        col2 = int(request.form['col2'])
        file = request.files['file']
        
        # Save the file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        data = {'filename':filename, 'numClusters' : numClusters, 'col1' : col1, 'col2' : col2}
        return render_template('doCustomCluster.html', jsdata = json.dumps(data))
    
    else:
        line = 1
        xaxis_label = ''
        yaxis_label = ''
        
        numClusters = int(request.args['numClusters'])
        col1 = int(request.args['col1'])
        col2 = int(request.args['col2'])
        filename = request.args['filename']
        
        csvFile = UPLOAD_FOLDER + '/' + filename
        csv_data = csv.reader(open(csvFile, 'r'))
        chartTitle = filename
        
        values = []
        
        for row in csv_data:
            col1_data = 0
            col2_data = 0
            try:
                col1_data = float(row[col1])
                col2_data = float(row[col2])
            except Exception as e:
                if line == 1:
                    xaxis_label = row[col1]
                    yaxis_label = row[col2]
                    line = line - 1
                continue
            
            values.append([col1_data, col2_data])    
        
        
        narray = np.array(values)
        
        km = KMeans(numClusters).fit(narray)
        labels = km.labels_
        centroids = []
        
        for v in km.cluster_centers_:
            centroids.append([v[0],v[1]])
        
        data = {'chartTitle' : chartTitle, 'numClusters': numClusters, 'centroids' : centroids, 'xaxis_label' : xaxis_label, 'yaxis_label' : yaxis_label}
        
        for i in range(0, numClusters):
            ds = narray[np.where(labels==i)]
            cdata = []
            
            for d in ds:
                cdata.append([d[0],d[1]])
            
            data['cluster_' + str(i)] = cdata
        
        return json.dumps(data)
        
        
@app.route('/q6')
def q6():
    
    if request.method == 'GET':
        csv_data = csv.reader(open("/home/hduser/data/Data.csv", 'r'))
        
        numClusters = int(request.args['numClusters'])
        col1 = int(request.args['col1'])
        col2 = int(request.args['col2'])
        
        values = []
        currentTime = int(round(time.time() * 1000))
        
        for row in csv_data:
            col1_data = 0
            col2_data = 0
            try:
                col1_data = float(row[col1])
                col2_data = float(row[col2])
            except Exception as e:
                continue
            
            values.append([col1_data, col2_data])    
        
        
        narray = np.array(values)
        
        km = KMeans(numClusters).fit(narray)
        labels = km.labels_
        centroids = []
        
        for v in km.cluster_centers_:
            centroids.append([v[0],v[1]])
        
        data = {'numClusters': numClusters, 'centroids' : centroids}
        
        for i in range(0, numClusters):
            ds = narray[np.where(labels==i)]
            cdata = []
            dist = 0
            max = 0
            centroid = centroids[i]
            
            for d in ds:
                cdata.append([d[0],d[1]])
                
                dist = math.hypot(centroid[0] - d[0], centroid[1] - d[1])
                if dist >= max:
                    max = dist
                    
            data['maxdist_' + str(i)] = max
            data['cluster_' + str(i)] = cdata
            data['cluster_' + str(i) + '_size'] = len(cdata)
        
        
        runtime = int(round(time.time() * 1000))
        totalTime = runtime - currentTime
        data['totalTime'] = str(totalTime) + ' msecs'
        
        return json.dumps(data)

@app.route('/q7', methods = ['GET', 'POST'])
def q7():
    if request.method == 'POST':
        numClusters = int(request.form['numClusters'])
        col1 = int(request.form['col1'])
        col2 = int(request.form['col2'])
        file = request.files['file']
        
        # Save the file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        line = 1
        xaxis_label = ''
        yaxis_label = ''
        
        csvFile = UPLOAD_FOLDER + '/' + filename
        csv_data = csv.reader(open(csvFile, 'r'))
        chartTitle = filename
        
        values = []
        
        for row in csv_data:
            col1_data = 0
            col2_data = 0
            try:
                col1_data = float(row[col1])
                col2_data = float(row[col2])
            except Exception as e:
                if line == 1:
                    xaxis_label = row[col1]
                    yaxis_label = row[col2]
                    line = line - 1
                continue
            
            values.append([col1_data, col2_data])    
        
        
        narray = np.array(values)
        
        km = KMeans(numClusters).fit(narray)
        labels = km.labels_
        centroids = []
        
        for v in km.cluster_centers_:
            centroids.append([v[0],v[1]])
        
        data = {'chartTitle' : chartTitle, 'numClusters': numClusters, 'centroids' : centroids, 'xaxis_label' : xaxis_label, 'yaxis_label' : yaxis_label}
        
        for i in range(0, numClusters):
            ds = narray[np.where(labels==i)]
            cdata = []
            
            for d in ds:
                cdata.append([d[0],d[1]])
            
            data['cluster_' + str(i)] = cdata
        
        return render_template('q7.html', jsdata = json.dumps(data))

@app.route("/q8")
def q8():
    return render_template('indexq8.html')

@app.route("/execProcess")
def execProcess():
    
    print 'Download started...'
    
    returnCode = subprocess.call(['wget',
                              'https://pypi.python.org/packages/55/8a/78e165d30f0c8bb5d57c429a30ee5749825ed461ad6c959688872643ffb3/Flask-0.11.1.tar.gz#md5=d2af95d8fe79cf7da099f062dd122a08',
                              '-P',
                              '/home/hduser/HDownload'])
    
    print 'Download complete...'
    
    return str(returnCode)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)

if __name__ == '__main__':
    #app.run()
    app.run(debug = True)