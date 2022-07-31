from flask import Flask, render_template, request, redirect
from config import Config as SETTING
from flask_pymongo import pymongo
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = SETTING.FLASK_KEY

# database Settings
myclient = pymongo.MongoClient(SETTING.MONGO_LINK)
EmergencySaveDatabase = myclient[SETTING.DATABASE_NAME]
EmergencySaveCollection = EmergencySaveDatabase[SETTING.DATABASE_COLLECTION]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['GET'])
def detect():
    if request.method == 'GET':
        endport = request.args.get("endport")
        return redirect(endport)

@app.route('/<string:PersonalPage>',  methods=['GET', 'POST'])
def PersonalPage(PersonalPage):
    if request.method == 'GET':
        # check that page is available or not
        userCheck = EmergencySaveCollection.count_documents({"endport" : PersonalPage})
        if userCheck != 0:
            # show Login page
            params = {'endport': PersonalPage, 'alert_match': 'none'}
            return render_template('PersonalPageLogin.html', data=params)
        else:
            # show Signup page
            params = {'endport': PersonalPage, 'alert_match': 'none', 'alert_long': 'none'}
            return render_template('PersonalPageCreate.html', data=params)

    elif request.method == 'POST':
        if 'login-btn' in request.form:
            # grab data from website
            password = request.form['password']

            # authentication of user
            userData = EmergencySaveCollection.find({"endport" : PersonalPage}, {"_id" : False})[0]
            if sha256_crypt.verify(password, userData["password"]):
                params = {'endport': PersonalPage, 'userdata': userData["data"], 'alert_updated': 'none', 'alert_match': 'none', 'alert_length':'none'}
                return render_template('PersonalPageHome.html', data=params)
            else:
                params = {'endport': PersonalPage, 'alert_match': 'block'}
                return render_template('PersonalPageLogin.html', data=params)

        elif 'register-btn' in request.form:
            password = request.form['newpassword']
            passwordConf = request.form['newpasswordConf']

            # Check password and add
            if password == passwordConf:
                newEndport = {
                    "endport" : PersonalPage,
                    "password" : sha256_crypt.hash(password),
                    "data" : ""
                }
                EmergencySaveCollection.insert_one(newEndport)
                userData = EmergencySaveCollection.find({"endport" : PersonalPage}, {"_id" : False})[0]
                params = {'endport': PersonalPage, 'userdata': userData["data"], 'alert_updated': 'none', 'alert_match': 'none', 'alert_length':'none'}
                return render_template('PersonalPageHome.html', data=params)
            else:
                params = {'endport': PersonalPage, 'alert_match': 'block', 'alert_long': 'none'}
                return render_template('PersonalPageCreate.html', data=params)
        
        elif 'update-data-btn' in request.form:
            # grab data from website 
            userData = request.form['userdata']
            password = request.form['password']
            
            # add chanages to database
            userDataCol = EmergencySaveCollection.find({"endport" : PersonalPage}, {"_id" : False})[0]
            if sha256_crypt.verify(password, userDataCol["password"]):
                if len(userData) < 100000:
                    EmergencySaveCollection.update_one({"endport" : PersonalPage}, {"$set" : {"data" : userData}})
                    params = {'endport': PersonalPage, 'userdata': userData, 'alert_updated': 'block', 'alert_match': 'none', 'alert_length':'none'}
                    return render_template('PersonalPageHome.html', data=params)
                else:
                    params = {'endport': PersonalPage, 'userdata': userData, 'alert_updated': 'none', 'alert_match': 'block', 'alert_length':'block'}
                    return render_template('PersonalPageHome.html', data=params)
            else:
                # password wrong
                params = {'endport': PersonalPage, 'userdata': userData, 'alert_updated': 'none', 'alert_match': 'block', 'alert_length':'none'}
                return render_template('PersonalPageHome.html', data=params)
        
        elif 'delete-data-btn' in request.form:
            # grab data from website
            userData = request.form['userdata']
            password = request.form['password']

            # delete from database
            userDataCol = EmergencySaveCollection.find({"endport" : PersonalPage, "password" : password}, {"_id" : False})[0]
            if sha256_crypt.verify(password, userDataCol["password"]):
                EmergencySaveCollection.delete_one({"endport" : PersonalPage})
                return redirect('/')
            else:
                # password wrong
                params = {'endport': PersonalPage, 'userdata': userData, 'alert_updated': 'none', 'alert_match': 'block', 'alert_length':'none'}
                return render_template('PersonalPageHome.html', data=params)



@app.errorhandler(400) 
def not_found400(e): 
  return render_template("400.html") 

@app.errorhandler(404) 
def not_found404(e): 
  return render_template("404.html") 

@app.errorhandler(500) 
def not_found500(e): 
  return render_template("500.html") 

if __name__ == "__main__":
    app.run(debug=SETTING.DEBUG)