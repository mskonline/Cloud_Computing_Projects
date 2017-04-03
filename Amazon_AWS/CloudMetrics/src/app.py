from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

from mysql.connector import Error

import csv
import os
import time
import glob
import mysql.connector
import random
import itertools
import memcache
import json
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = '/var/www/cloudmetrics/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

host = 'west2-mysql-instance1.c5gxp3u3tdxp.us-west-2.rds.amazonaws.com'
port = 3306
dbusername = 'mskawsrds'
dbpassword = 'mskrds123$'
dbname = 'cloud'

#localhost
# host = 'localhost'
# port = 3306
# dbusername = 'root'
# dbpassword = '123'
# dbname = 'cloud'


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/webquery")
def webquery():
    return render_template("webquery.html")

@app.route('/runqueries')
def runqueries():
    return render_template("runqueries.html")

@app.route('/execquery', methods = ['GET', 'POST'])
def execquery():
    
    name = request.form['fieldName']
    c1 = request.form['cclause1']
    c2 = request.form['cclause2']
    withMem =  request.form['withmem']
    
    if withMem == 'y':
        return  execqueryWithMem(name, c1, c2)
    
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        
        query = 'select ' + name + ' from cloud.unprecip where ' + c1 + ' and ' + c2
 
        starttime = int(round(time.time() * 1000))
         
        for i in range(0, 250):
                
            cursor = mysql_conn.cursor()
            cursor.execute(query)
            row = cursor.fetchall()
            count = cursor.rowcount
            cursor.close()
          
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
          
        mysql_conn.close()
         
        resultStr = '<div style="font-size:14px;margin-top: 30px;"><div> Last Name : Manakan </div><div> Last 4 digit ID : 6131 </div><div> Class Section : 10:30 AM </div></div>'
        resultStr = resultStr +  '<br> Time taken : ' + str(totalexectime) + ' msecs'
        resultStr = resultStr + '<br> Rows effected : ' + str(count)
        return resultStr
    except Exception as e:
        print e
        return 'Error ' + str(e)

def execqueryWithMem(name, c1, c2):
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        mc = memcache.Client([('mycachecluster.iw3rc7.0001.usw2.cache.amazonaws.com', 11211)])
        
        query = 'select ' + name + ' from cloud.unprecip where ' + c1 + ' and ' + c2
        hashVal = hashlib.sha224(query).hexdigest()
        
        starttime = int(round(time.time() * 1000))
        
        data = mc.get(hashVal)
        count = 0
        
        if not data:
            for i in range(0, 250):
                    
                cursor = mysql_conn.cursor()
                cursor.execute(query)
                row = cursor.fetchall()
                count = cursor.rowcount
                cursor.close()
            mc.set(hashVal,count)
              
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
          
        mysql_conn.close()
         
        resultStr = '<div style="font-size:14px;margin-top: 30px;"><div> Last Name : Manakan </div><div> Last 4 digit ID : 6131 </div><div> Class Section : 10:30 AM </div></div>'
        resultStr = resultStr +  '<br> Time taken : ' + str(totalexectime) + ' msecs'
        resultStr = resultStr + '<br> Rows effected : ' + str(count)
        return resultStr
    except Exception as e:
        print e
        return 'Error ' + str(e)
    
@app.route("/quiz3")
def quiz3():
     return render_template("quiz3.html")
 
# Testing the uploading time into the server
@app.route("/fileupload", methods = ['GET', 'POST'])
def fileupload():

    if request.method == 'POST':
        file = request.files['file']
        uploadTime = int(request.form.get('uploadTime'))
        currentTime = int(round(time.time() * 1000))

        totalTime = currentTime - uploadTime
        
        # Save the file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        resultStr = 'Time taken for upload : <b>' + str(totalTime) + '</b>  msecs <br>'
        resultStr = resultStr + loadDB(filename)
        
        try:
            mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        
            query = 'update cloud.unprecip set aug=-1, sep=-1, december=-1 where aug > 10000 or sep > 10000 or december > 10000'
 
            starttime = int(round(time.time() * 1000))
            cursor = mysql_conn.cursor()
            cursor.execute(query)
            upCount = cursor.rowcount 
            cursor.close()
            
            query = "DELETE FROM cloud.unprecip WHERE country_or_territory = 'CANADA'"
            
            cursor = mysql_conn.cursor()
            cursor.execute(query)
            delCount = cursor.rowcount
            endtime = int(round(time.time() * 1000))
            totalexectime = endtime - starttime
            
            cursor.close()
            
            mysql_conn.commit()
            
            mysql_conn.close()
            
            resultStr = resultStr + 'Time taken to change tuples ('+ str(upCount) + ') and remove tuples (' + str(delCount) + ') : <b>' + str(totalexectime) + '</b> msecs '
        except Exception as e:
            return str(e)
        
        
        return resultStr

@app.route("/jsonResult",methods = ['POST','GET'])
def jsonResult():
       
    query = request.form['query']
 
    hashVal = hashlib.sha224(query).hexdigest()
    
    try:
        mc = memcache.Client([('mycachecluster.iw3rc7.0001.usw2.cache.amazonaws.com', 11211)])
        
        data = mc.get(hashVal)
    
        starttime = int(round(time.time() * 1000))
        if not data:
            mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
            cursor = mysql_conn.cursor()
            
            cursor.execute(query)
            endtime = int(round(time.time() * 1000))
            
            desc = cursor.description
            data = [dict(itertools.izip([col[0] for col in desc], row)) 
                        for row in cursor.fetchall()]
            
            mc.set(hashVal, data)
            cursor.close()
            mysql_conn.close()
        else:
            print 'key found'
            endtime = int(round(time.time() * 1000))
        
        totalexectime = endtime - starttime
        
        results = {'status':'true', 'data': data, 'timeInmsecs' : str(totalexectime)}
    except Exception as e:
        results = {'status':'error', 'message': str(e)}
        
    
    return json.dumps(results)

@app.route("/testcache")
def testcache():
    
    try:
        mc = memcache.Client([('mycachecluster.iw3rc7.0001.usw2.cache.amazonaws.com', 11211)])
    except Exception as e:
        print e
        
        
    obj = mc.get("sample_user")
    
    if not obj:
        print 'sample user not found...'
        sample_obj = {"name": "Soliman","lang": "Python"}
        mc.set("sample_user", sample_obj)
        print "Stored to memcached"
    
    print mc.get("sample_user")
        
    return 'Done...'

@app.route("/clearcache")
def clearcache():
    mc = memcache.Client([('mycachecluster.iw3rc7.0001.usw2.cache.amazonaws.com', 11211)])
    mc.flush_all()
    
    return 'Flushed the cache...'
    

@app.route("/runRandomqueriesOnLargeSample/<int:qcount>")
def runRandomqueriesOnLargeSample(qcount):
   
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        
        query = 'select census2010pop from cloud.subcounty_population_estimates where place='
 
        starttime = int(round(time.time() * 1000))
         
        for i in range(1, qcount):
                
            cursor = mysql_conn.cursor()
              
            place = random.randint(0, qcount)
            q = query + str(place)
              
            cursor.execute(q)
            row = cursor.fetchall()
              
            cursor.close()
          
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
          
        mysql_conn.close()
         
        return 'Time taken : ' + str(totalexectime) + ' msecs'
        
    except Exception as e:
        print e
        return 'Error ' + str(e)

@app.route("/runRandomqueriesOnSmallSample/<int:qcount>")
def runRandomqueriesOnSmallSample(qcount):
   
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        
        query = 'select census2010pop from cloud.subcounty_population_estimates_small where place='
 
        starttime = int(round(time.time() * 1000))
         
        for i in range(1, qcount):
                
            cursor = mysql_conn.cursor()
              
            place = random.randint(0, qcount)
            q = query + str(place)
              
            cursor.execute(q)
            row = cursor.fetchall()
              
            cursor.close()
          
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
          
        mysql_conn.close()
         
        return 'Time taken : ' + str(totalexectime) + ' msecs'
        
    except Exception as e:
        print e
        return 'Error ' + str(e)

@app.route("/runRandomqueriesOnLargeSampleWithMemCache/<int:qcount>")
def runRandomqueriesOnLargeSampleWithMemCache(qcount):
   
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        mc = memcache.Client([('mycachecluster.iw3rc7.0001.usw2.cache.amazonaws.com', 11211)])
        
        query = 'select census2010pop from cloud.subcounty_population_estimates where place='
 
        starttime = int(round(time.time() * 1000))
         
        for i in range(1, qcount):
            
            place = str(random.randint(0, qcount))
            
            obj = mc.get(place)
            
            if not obj:
                cursor = mysql_conn.cursor()
                  
                q = query + place
                  
                cursor.execute(q)
                row = cursor.fetchall()
                  
                cursor.close()
            
                mc.set(place, 'data')
          
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
          
        mysql_conn.close()
         
        return 'Time taken : ' + str(totalexectime) + ' msecs'
        
    except Exception as e:
        print e
        return 'Error ' + str(e)

@app.route("/runRandomqueriesOnSmallSampleWithMemCache/<int:qcount>")
def runRandomqueriesOnSmallSampleWithMemCache(qcount):
   
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        mc = memcache.Client([('mycachecluster.iw3rc7.0001.usw2.cache.amazonaws.com', 11211)])
        
        query = 'select census2010pop from cloud.subcounty_population_estimates_small where place='
 
        starttime = int(round(time.time() * 1000))
         
        for i in range(1, qcount):
                
            place = str(random.randint(0, qcount))
            
            obj = mc.get(place)
            
            if not obj:
                cursor = mysql_conn.cursor()
                  
                q = query + place
                  
                cursor.execute(q)
                row = cursor.fetchall()
                  
                cursor.close()
                
                mc.set(place, 'data')
          
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
          
        mysql_conn.close()
         
        return 'Time taken : ' + str(totalexectime) + ' msecs'
        
    except Exception as e:
        print e
        return 'Error ' + str(e)
    
@app.route("/loaddb/<file>")
def loadDB(file):
    
    filename = UPLOAD_FOLDER + '/' + file
    
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        
        csv_data = csv.reader(open(filename, 'r'))
        
        query = 'insert into cloud.unprecip (country_or_territory,station_name,wmo_station_number,unit,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,december)' + ' values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        
        starttime = int(round(time.time() * 1000))
        
        for row in csv_data:
            cursor = mysql_conn.cursor()
            cursor.execute(query, row)
            
        endtime = int(round(time.time() * 1000))
        totalexectime = endtime - starttime
        cursor.close()
        mysql_conn.commit()
        mysql_conn.close()
        
        return 'Time taken to load table : <b>' + str(totalexectime) + '</b> msecs <br>'
    except Exception as e:
        print e
        return 'Error ' + str(e)
    
@app.route("/showMinMaxVals")
def showMinMaxVals():
    mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
    cursor = mysql_conn.cursor()
        
    query = 'SELECT country_or_territory FROM cloud.unprecip where aug = (select max(aug) from cloud.unprecip)'
    query_2 = 'SELECT country_or_territory FROM cloud.unprecip where sep = (select max(sep) from cloud.unprecip)'
    query_3 = 'SELECT country_or_territory FROM cloud.unprecip where aug = (select min(aug) from cloud.unprecip)'
    query_4 = 'SELECT country_or_territory FROM cloud.unprecip where sep = (select min(sep) from cloud.unprecip)'
    
    starttime = int(round(time.time() * 1000))
    
    cursor.execute(query)
    row = cursor.fetchall()
    resultStr = 'Max in Aug : ' + str(row[0][0]) + ' <br>'
    
    cursor.close()
    
    
    cursor = mysql_conn.cursor()
    cursor.execute(query_3)
    row = cursor.fetchall()
    
    resultStr = resultStr + 'Min in Aug : ' + str(row[0][0]) + ' <br>'
      
    cursor.close()
    
    cursor = mysql_conn.cursor()
    cursor.execute(query_2)
    row = cursor.fetchall()
    
    resultStr = resultStr + 'Max in Sep : ' + str(row[0][0]) + ' <br>'
      
    cursor.close()
    
    cursor = mysql_conn.cursor()
    cursor.execute(query_4)
    row = cursor.fetchall()
    
    resultStr = resultStr + 'Min in Sep : ' + str(row[0][0]) + ' <br>'
      
    cursor.close()
    
    endtime = int(round(time.time() * 1000))
    totalexectime = endtime - starttime
    
    mysql_conn.close()
    
    return resultStr + '<br><br>Time taken : ' + str(totalexectime) + ' msecs'

@app.route("/showCountryVals/<country>/<month>/<val>")
def showCountryVals(country, month, val):
    mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
    cursor = mysql_conn.cursor()
    
    query = 'select COUNT(*) from cloud.unprecip where country_or_territory="' + country.upper() + '" and ' + month + ' <= ' + val
    
    cursor = mysql_conn.cursor()
    
    starttime = int(round(time.time() * 1000))
    cursor.execute(query)
    row = cursor.fetchall()
    
    endtime = int(round(time.time() * 1000))
    totalexectime = endtime - starttime
    
    rf = str(row[0][0])
    cursor.close()
    mysql_conn.close()
    
    return 'Tuples matching : ' + rf + '<br> Total time : ' + str(totalexectime) + ' msecs'

# Testing the uploading time into the server
@app.route("/upload", methods = ['GET', 'POST'])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        uploadTime = int(request.form.get('uploadTime'))
        currentTime = int(round(time.time() * 1000))

        totalTime = currentTime - uploadTime
        
        # Save the file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        return 'Time taken for upload : ' + str(totalTime) + ' msecs'

@app.route("/cleanUploadDir", methods = ['GET'])
def cleanUploadDir():
    files = glob.glob('/var/www/cloudmetrics/upload/*')
    for f in files:
        os.remove(f)
        
    return 'Cleaned.'
        
@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)


def connectToDB():
    
    try:
        mysql_conn = mysql.connector.connect(host = host, user = dbusername, password = dbpassword, database = dbname , port = port)
        cursor = mysql_conn.cursor()
    
        query = "SELECT VERSION()"
        cursor.execute(query)
    
        row = cursor.fetchone()
        
        cursor.close()
        mysql_conn.close()
        
        print 'DB Connected. Version : ' + row[0]
    except Exception as e:
        print e


if __name__ == '__main__':
    #app.run()
    app.run(debug = True)