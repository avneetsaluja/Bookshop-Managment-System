# -*- coding: utf-8 -*-
from flask import Flask,render_template,request,flash,url_for,redirect
from connectDB import connection

app = Flask(__name__)
app.secret_key = "my name is ali"

@app.route('/login/<flag>',methods = ["GET","POST"])
def login(flag):
	if request.method == "GET":
		return render_template('frontPage.html',flag = flag)
	else :
		name = request.form['Username']
		password = request.form['Password']
		c,conn = connection()
		data = c.execute("select username,password from user where username = (%s)",str(name))
		if data:
			data = c.fetchone()[1]
			if data!=str(password):
				flash("Invalid Credentials, try again!!")
				return redirect(url_for('login',flag = "0"))
			return redirect(url_for('myHome',username = str(name)))
		flash("Please SignUp First !!")
		return redirect(url_for('login',flag = "0"))

@app.route('/signup',methods = ['GET','POST'])
def signup():
	if request.method == 'GET':
		return render_template('signup.html')
	else:
		name = request.form['Username']
		pwd = request.form['Password']
		repwd = request.form['Confirm Password']
		email = request.form['Email']
		addr = request.form['Address']
		if pwd != repwd :
			flash("Passwords Don't Match, Try Again!!")
			return redirect(url_for('signup'))
		else :
			c,conn = connection()
			data = c.execute("select username from user where username = (%s)",str(name))
			if data :
				flash("Username already taken, try another!!")
				return redirect(url_for('signup'))
			data = c.execute("select email from user where email = (%s)",str(email))
			if data :
				flash("Email Id already taken, try another!!")
				return redirect(url_for('signup'))
			c.execute("insert into user values(%s,%s,%s,%s)",(str(name),str(email),str(pwd),addr))
			conn.commit()
			return render_template('frontPage.html',flag = "0")

@app.route('/home/<username>')
def myHome(username):
	flash(username)
	return render_template('home.html')

@app.route('/pay/<username>/<bid>/<pid>', methods = ['GET','POST'])
def pay(username,bid,pid):
	if request.method == 'GET':
		c,conn = connection()
		data = c.execute("select * from buys where username = (%s) and b_id = (%s) and p_id = (%s)",(username,bid,pid))
		if data :
			flash("This book can be bought only once per user !!")
			return redirect(url_for('func',username = username,bid = bid,pid = pid,flag = 0))
		else :
			data = c.execute("select price from books natural join published_by natural join publisher where b_id = (%s) and p_id = (%s)",(bid,pid))
			data = c.fetchall()[0]
			flash(data[0])
			flag= "0"
			return render_template('payment.html',user = username,bid = bid,flag = flag,pid = pid)
	flag = "1"
	c,conn = connection()
	data = c.execute("select price from published_by where p_id = (%s) and b_id = (%s)",(pid,bid))
	data = c.fetchall()
	price = data[0][0]
	c.execute("insert into buys values ((%s),(%s),(%s),(%s),(%s))",(username,bid,pid,"Pending",price))
	c.execute("update published_by set stock = stock -1 where p_id = (%s) and b_id = (%s)",(pid,bid))
	conn.commit()	
	return render_template('payment.html',user = username,flag = flag,bid = bid,pid = pid)

@app.route('/<username>/<bid>/<pid>/<int:flag>')
def func(username,bid,pid,flag):
	c,conn = connection()
	data = c.execute("select * from (books natural join published_by) natural join publisher where b_id = (%s) and p_id = %s",(bid, pid))
	data = c.fetchall()
	if flag == 0:
		c.execute("select stock from published_by where b_id = (%s) and p_id = (%s)",(bid,pid))
		stock = c.fetchall()[0][0]
		return render_template('bookDetails.html',data=data,name = username,flag = "1",b_id = bid,stock = stock, p_id = pid)
	else :
		flash("Out Of STOCK !!")
		return redirect(url_for('func',username = username,bid = bid,pid = pid ,flag = 0))

@app.route('/order/<username>')
def order(username):
	if username == "Guest":
		flash("Please Log in First !!");
		return redirect(url_for('login',flag="0"))
	c,conn = connection()
	data = c.execute("select * from books natural join buys natural join publisher where username = (%s) order by status desc",username)
	data =  c.fetchall()
	status = []
	for row in data :
		if row[8] == "Pending" :
			status.append("darkred")
		else :
			status.append("forestgreen")
	return render_template('history.html',data = data,status = status)

if __name__ == "__main__":
	app.run(debug=True,port = 5000)