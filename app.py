from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

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
    if request.method == 'POST':
        if 'login-btn' in request.form:
            # grab data from website
            endport = PersonalPage
            password = request.form['password']

            # authentication of user
            conn = sqlite3.connect('pagedetail.db')
            GET_DATA = conn.execute(f"SELECT ENDPORT, PASSWORD FROM endports WHERE ENDPORT='{endport}'")
            for row in GET_DATA:
                if row[0] == endport and row[1] == password:
                    GET_DATA = conn.execute(f"SELECT DATA FROM endports WHERE ENDPORT='{endport}'")
                    for data_row in GET_DATA:
                        params = {'endport': PersonalPage, 'userdata': data_row[0], 'alert_updated': 'none', 'alert_match': 'none'}
                        conn.close()
                        return render_template('PersonalPageHome.html', data=params)
                else:
                    params = {'endport': PersonalPage, 'alert_match': 'block'}
                    return render_template('PersonalPageLogin.html', data=params)
        elif 'register-btn' in request.form:
            
            endport = PersonalPage
            password = request.form['newpassword']
            passwordConf = request.form['newpasswordConf']

            # checking password and create page
            if password == passwordConf:
                if len(password) < 21:
                    conn = sqlite3.connect('pagedetail.db')
                    conn.execute(f"INSERT INTO endports (ENDPORT, PASSWORD, DATA) VALUES ('{endport}', '{password}', 'Your Text')")
                    conn.commit()
                    # for row in GET_DATA:

                    conn.close()
                    params = {'endport': PersonalPage, 'userdata': 'Your Text', 'alert_updated': 'none', 'alert_match': 'none'}
                    # conn.close()
                    return render_template('PersonalPageHome.html', data=params)
                else:
                    params = {'endport': PersonalPage, 'alert_match': 'none', 'alert_long': 'block'}
                    return render_template('PersonalPageCreate.html', data=params)
            else:
                params = {'endport': PersonalPage, 'alert_match': 'block', 'alert_long': 'none'}
                return render_template('PersonalPageCreate.html', data=params)
        
        elif 'update-data-btn' in request.form:
            # grab data from website 
            endport = PersonalPage
            userdata = request.form['userdata']
            
            # add chanages to database
            if len(userdata) < 10000:
                conn = sqlite3.connect('pagedetail.db')
                conn.execute(f"UPDATE endports SET DATA = '{userdata}' WHERE ENDPORT='{endport}'")
                conn.commit()
                conn.close()
                params = {'endport': endport, 'userdata': userdata, 'alert_updated': 'block', 'alert_match': 'none'}
                return render_template('PersonalPageHome.html', data=params)
        
        elif 'delete-data-btn' in request.form:
            # grab data from website 
            endport = PersonalPage
            userdata = request.form['userdata']
            password = request.form['password']

            # delete from database
            conn = sqlite3.connect('pagedetail.db')
            GET_DATA = conn.execute(f"SELECT ENDPORT, PASSWORD FROM endports WHERE ENDPORT='{endport}'")
            for raw in GET_DATA:
                if endport == raw[0] and password == raw[1]:
                    conn.execute(f"DELETE FROM endports WHERE ENDPORT='{endport}'")
                    conn.commit()
                    conn.close()
                    return redirect('/')
                else:
                    params = {'endport': endport, 'userdata': userdata, 'alert_updated': 'none', 'alert_match': 'block'}
                    return render_template('PersonalPageHome.html', data=params)

    else:
        # check that page is available or not
        conn = sqlite3.connect('pagedetail.db')
        ENDPORT_PRESENT = False
        try:
            GET_DATA = conn.execute(f"SELECT ENDPORT FROM endports WHERE ENDPORT='{PersonalPage}'")
            for row in GET_DATA:
                ENDPORT_PRESENT = True
            conn.close()
        except:
            pass
        
        if ENDPORT_PRESENT == True:
            params = {'endport': PersonalPage, 'alert_match': 'none'}
            return render_template('PersonalPageLogin.html', data=params)
        else:
            params = {'endport': PersonalPage, 'alert_match': 'none', 'alert_long': 'none'}
            return render_template('PersonalPageCreate.html', data=params)


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
    app.run(debug=True)