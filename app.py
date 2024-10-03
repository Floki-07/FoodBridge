from flask import Flask,render_template,redirect,request,session,jsonify
from flask_mysqldb import MySQL
from MySQLdb._exceptions import IntegrityError
app= Flask(__name__)


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='*********'
app.config['MYSQL_DB']='foodbridge'
app.secret_key='******'
mysql= MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')





@app.route('/ngo_login',methods=['GET','POST'])
def ngo_login():

    if request.method=='POST':
        print('inside post')
        fusername=request.form['username']
        fpassword=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute('select * from Ngos where username=%s',(fusername,))
        user=cur.fetchone()
        # print(user)
        cur.close()
        if user is None:
            print('usernot found')
            return render_template('usernotfound.html',res=False)

        if user[5]==fusername and user[6]==fpassword:
            session['username']=fusername
            session['name']=user[1]
            session['nid']=user[0]
            # print(session['username'])
            return redirect('/ngo-dashboard')

        else:
           return render_template('incorrect-password.html',res=False)

    return render_template('ngo-login.html')

@app.route('/NGO-registration',methods=['GET','POST'])
def ngo_reg():
    if request.method=='POST':
        name=request.form['name']
        address=request.form['address']
        phone=request.form['phone']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']

        cur=mysql.connection.cursor()
        query='select * from Ngos where username=%s'
        data=(username,)
        cur.execute(query,data)
        user=cur.fetchone()
        if user is None :
            cur=mysql.connection.cursor()
            query='insert into NGos(name,address,phone,email ,username,password) values(%s,%s,%s,%s,%s,%s)'
            data=(name,address,phone,email,username,password)
            cur.execute(query,data)
            cur.close()
            mysql.connection.commit()
            return render_template('ngo-login.html')
        else:
            return render_template('user-already-present.html',res=False)
    return render_template('ngo-reg.html')
    
@app.route('/restaurant_login' ,methods=['GET','POST'])
def res_login():
    if request.method=='POST':
        fusername=request.form['username']
        fpassword=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute('select * from Restaurants where username=%s',(fusername,))
        user=cur.fetchone()
        print(user)
        
        cur.close()
        if user is None:
            print('usernot found')
            return render_template('usernotfound.html',res=True)

        if user[5]==fusername and user[6]==fpassword:
            session['username']=fusername
            session['rid']=user[0]
            session['name']=user[1]
            print(session['username'])
            return render_template('res-dashboard.html')

        else:
            return render_template('incorrect-password.html',res=True)
    return render_template('res-login.html')



@app.route('/res-registration',methods=['GET','POST'])
def res_reg():
    if request.method=='POST':
        name=request.form['name']
        address=request.form['address']
        phone=request.form['phone']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']

        cur=mysql.connection.cursor()
        query='select * from Restaurants where username=%s'
        data=(username,)
        cur.execute(query,data)
        user=cur.fetchone()
        print(user)
        if user is None:
            cur=mysql.connection.cursor()
            query='insert into Restaurants(name,address,phone,email ,username,password) values(%s,%s,%s,%s,%s,%s)'
            data=(name,address,phone,email,username,password)
            cur.execute(query,data)
            cur.close()
            mysql.connection.commit()
            return render_template('res-login.html')
        else:
            return render_template('user-already-present.html',res=True)
    return render_template('res-reg.html')

all_res=[]
@app.route('/ngo-dashboard',methods=['GET','POST'])
def ngo_dashboard():
    cur=mysql.connection.cursor()
    query="select *from restaurants"
    cur.execute(query)
    all_res=cur.fetchall()
    return render_template('ngo-dashboard.html',all_res=all_res)




@app.route('/res-dashboard',methods=['GET','POST'])
def res_dashboard():
    cur=mysql.connection.cursor()
    query="select *from ngos"
    cur.execute(query)
    all_ngos=cur.fetchall()
    print(all_ngos)
    return jsonify(all_ngos)
    # return render_template('res-dashboard.html',all_ngos=all_ngos)


@app.route("/logout")
def logout():
    session['username']=None
    session['rid']=None
    session['name']=None
    print('logout')
    return redirect("/")


    
@app.route("/get_hotel_data/<int:hid>",methods=['GET','POST'])
def data(hid):
    cur=mysql.connection.cursor()
    cur.execute(f"select * from restaurants where rid={hid}")
    data=cur.fetchone()
    cur.close()
    print(data)
    return jsonify(data)

@app.route("/send_request/<int:hid>/<int:nid>/<int:no_of_meals>/<int:status>",methods=['POST','GET'])
def send_req_hotel(hid,nid,no_of_meals,status=0):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO requests (hid, nid, meals,status) VALUES (%s, %s, %s,%s)", (hid, nid, no_of_meals,status))
        mysql.connection.commit()
        cur.close()
        print("Request ok")
        return "ok",200
    
    except IntegrityError:
        print("Duplicate")
        mysql.connection.rollback()
        return ("IntegrityError", 400)
    except Exception :
        return ("Exception",400)
  

@app.route('/get_request_details/<int:cur_nid>',methods=['POST','GET'])
def get_req_details(cur_nid):
    cur=mysql.connection.cursor()
    cur.execute(f"select * from requests where nid={cur_nid}")
    data=cur.fetchall()
    cur.close()
    print(data)
    return jsonify(data)



@app.route('/hotel_name/<int:curr_hid>',methods=['POST','GET'])
def hotel_name(curr_hid):
    cur=mysql.connection.cursor()
    cur.execute("SELECT name FROM restaurants WHERE rid = %s", (curr_hid,))
    hname=cur.fetchone()
    cur.close()
    return jsonify({'name': hname[0]}), 200




'''''
# NGO- ngo_dashboard
'''''

@app.route('/get_requests_res/<int:hid>',methods=['POST','GET'])
def get_req(hid):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM requests WHERE hid=%s AND status != %s", (hid, 2))
    data=cur.fetchall()
    cur.close()
    print(data)
    return jsonify(data)



@app.route('/ngo_name/<int:nid>',methods=['POST','GET'])
def get_ngo_name(nid):
    cur=mysql.connection.cursor()
    cur.execute("SELECT name FROM Ngos WHERE nid = %s", (nid,))
    hname=cur.fetchone()
    cur.close()
    return jsonify({'name': hname[0]}), 200


@app.route('/accept_req/<int:rid>/<int:nid>', methods=['POST', 'GET'])
def accept_req(nid, rid):
    try:
        cur = mysql.connection.cursor()
        # Check if record exists
        check_query = 'SELECT * FROM requests WHERE hid=%s AND nid=%s'
        cur.execute(check_query, (rid, nid))
        record = cur.fetchone()
        if not record:
            return 'Record not found', 404

        # Update status
        update_query = 'UPDATE requests SET status=%s WHERE hid=%s AND nid=%s'
        cur.execute(update_query, (2, rid, nid))
        mysql.connection.commit()
        cur.close()
        return 'accepted', 200
    except Exception as e:
        print(f"Error: {e}")  # Log the error
        return 'Error in updating request', 500

@app.route('/reject_req/<int:rid>/<int:nid>', methods=['POST', 'GET'])
def reject_req(nid, rid):
        cur = mysql.connection.cursor()
        update_query = 'UPDATE requests SET status=%s WHERE hid=%s AND nid=%s'
        cur.execute(update_query, (0, rid, nid))
        mysql.connection.commit()
        cur.close()
        return 'accepted', 200




@app.route('/remove_req/<int:nid>/<int:hid>', methods=['POST', 'GET'])
def dele_req(nid, hid):
    cur = mysql.connection.cursor()
    cur.execute('delete from requests where hid=%s and nid=%s',(hid,nid))
    mysql.connection.commit()
    cur.close()
    return ("ok",200)


@app.route('/remove_donation/<int:nid>/<int:hid>', methods=['POST', 'GET'])
def dele_don(nid, hid):
    cur = mysql.connection.cursor()
    cur.execute('delete from donations where hid=%s and nid=%s',(hid,nid))
    mysql.connection.commit()
    cur.close()
    return ("ok",200)



@app.route('/donate/<int:nid>/<int:hid>/<int:meals>', methods=['POST', 'GET'])
def donation(nid,hid,meals):
    cur = mysql.connection.cursor()
    query="insert into donations values(%s,%s,%s)"
    cur.execute(query,(hid,nid,meals))
    mysql.connection.commit()
    cur.close()
    return ('ok',200)


@app.route('/get_donations/<int:nid>', methods=['POST', 'GET'])
def get_donations(nid):
    cur=mysql.connection.cursor()
    cur.execute(f"select * from donations where nid={nid}")
    data=cur.fetchall()
    cur.close()
    print(data)
    return jsonify(data)


if __name__=='__main__':
    app.run(debug=True)
0