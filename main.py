import os.path
from wsgiref.util import request_uri
from flask import *
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import random
app = Flask(__name__)
app.secret_key = "tamil12345"
app.config['UPLOAD_FOLDER']="static/uploads"

# app.secret_key="tamil@123"
conn = mysql.connector.connect(host="localhost", user="root", password="", database="gaming")
cursor = conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/adminviewproducts")
def adminviewproducts():
    sql = "Select * from products"
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("adminviewproducts.html",data=data)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/adminviewusers")
def adminviewusers():
    sql = "Select * from registration"
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("adminviewusers.html",data=data)

@app.route("/admindeleteproduct")
def admindeleteproduct():
    id=request.args['id']
    sql = "delete from products where product_id = "+str(id)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return redirect(url_for("adminviewproducts"))

@app.route("/adminaddproduct", methods=['POST','GET'])
def adminaddproduct():
    msg=""
    if(request.method=="POST"):
        pname = request.form["pname"]
        ptype = request.form["ptype"]
        qty = request.form["qty"]
        price = request.form["price"]
        file = request.files['file']
        filename = "Img"+str(random.randint(1000,9999))+".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        sql = ("INSERT INTO products (product_name, product_type, quantity, price, filename) "
               "VALUES ('%s', '%s', '%s', '%s', '%s')" % (pname, ptype, qty, price, filename))
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        msg = "New Product Added Success"
    return render_template("adminaddproduct.html", msg=msg)

@app.route("/RegistrationForm")
def RegistratioForm():
    return render_template("RegistrationForm.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/makepayment",methods=["POST","GET"])
def makepayment():
    userid = session['id']
    if(request.method=="POST"):
        bname = request.form['bname']
        accnum = request.form['accnum']
        ifsccode = request.form['ifsccode']
        cvv = request.form['cvv']
        expdate = request.form['expdate']
        total = request.form['total']
        sql = "INSERT INTO payments(userid, bankname, accnum, ifsccode, " \
              "cvv, expdate, amount) " \
              "values('%s','%s','%s','%s','%s','%s','%s')" \
              % (userid, bname, accnum, ifsccode, cvv, expdate, total)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        sql = "Update order_table set paymentstatus='PaymentDone' where userid = "+\
              str(userid) + " and paymentstatus = 'PaymentNotDone'"
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return redirect(url_for("userviewreports"))
    sql="SELECT SUM(total) FROM order_table WHERE userid = "+str(userid)+" AND paymentstatus='PaymentNotDone'"
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    return render_template("makepaymentpage.html", total=data[0])

@app.route("/usermainpage")
def usermainpage():
    sql = "Select * from products"
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("user.html",data=data)

@app.route("/useraddtocart")
def useraddtocart():
    id=request.args['id']
    sql = "SELECT * FROM products where product_id = "+str(id)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    return render_template("useraddtocart.html",data=data)

@app.route("/useraddtocart1",methods=["POST","GET"])
def useraddtocart1():
    msg=""
    if request.method=="POST":
        userid = session['id']
        pid = request.form["pid"]
        pname=request.form["pname"]
        price=request.form["price"]
        ptype=request.form["ptype"]
        rqty = request.form["rqty"]
        total = request.form["total"]
        sql="INSERT INTO order_table(userid, product_id, product_name, product_type, " \
            "quantity, price, total, paymentstatus) " \
            "values('%s','%s','%s','%s','%s','%s','%s','%s')" \
            %(userid, pid, pname, ptype, rqty, price, total, 'PaymentNotDone')
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        msg="Order Added Successfully"
    sql = "Select * from order_table where userid = "+str(userid)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("userviewaddtocart.html", data=data)

@app.route("/userviewreports")
def userviewreports():
    userid = session['id']
    sql = "Select * from payments where userid="+str(userid)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("userviewreports.html",data=data)

@app.route("/adminviewreports")
def adminviewreports():
    sql = "Select * from payments"
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("adminviewreports.html",data=data)

@app.route("/userviewaddtocart")
def userviewaddtocart():
    userid = session['id']
    sql = "Select * from order_table where userid="+str(userid)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("userviewaddtocart.html",data=data)

@app.route("/deletefromcart")
def deletefromcart():
    orderid = request.args['orderid']
    productid = request.args['prodictid']
    qty = request.args['qty']
    sql = "delete from order_table where orderid="+str(orderid)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    sql = "update products set quantity=quantity+"+str(qty)+" where product_id=" + str(productid)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return redirect(url_for("userviewaddtocart"))

@app.route("/adminviewaddtocart")
def adminviewaddtocart():
    sql = "Select * from order_table"
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template("adminviewaddtocart.html",data=data)


@app.route("/userviewprofile")
def userviewprofile():
    id=session['id']
    sql = "select * from registration where regid='%s'"%(id)
    print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    return render_template("userviewprofile.html", data=data)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["pwd"]
        sql = "select * from registration where Emailid like '%s' and password like '%s'" % (email, pwd)
        print(sql)
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchone()
        if (data):
            session['id'] = data[0]
            msg = "Login Successfully Done"
            return redirect(url_for("usermainpage"))
        else:
            msg = "invalid Username/Password"

            if(email == "admin@gmail.com" and pwd == "Admin@1234"):
                return render_template("admin.html", msg=msg)
            else:
                msg = "invalid Email/Password"
                return render_template("Login.html", msg=msg)
    return render_template("Login.html")

@app.route('/Reg', methods=['GET', 'POST'])
def Reg():
    msg = ""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phnum = request.form["phnum"]
        pwd = request.form["pwd"]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registration WHERE Username='%s' "
                       "or emailid = '%s' or phnum = '%s'" % (name,email,phnum))
        existing_user = cursor.fetchone()
        if existing_user:
            msg = "Username/PhoneNum/EmailId is already taken. Please choose a different username."
        else:
            sql = "INSERT INTO registration (Username, Emailid, Phnum, Password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, email, phnum, pwd))
            conn.commit()
            msg = "Registration successful! Welcome, {name}."

    return render_template("RegistrationForm.html", msg=msg)

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
@app.route("/forget")
def forget():
    return render_template("forgotpassword.html")

@app.route("/checkemail", methods=["POST","GET"])
def checkemail():
    try:
        email =request.form['email']
        sql="Select * from registration  where EmailId like '%s'" % (email)
        print("Sql : ", sql)
        cursor.execute(sql)
        row = cursor.fetchone()
        print(row)
        if(row):
            session['email']=email
            print(session['email'])
            subject = "OTP to reset the password"
            otp = random.randint(1000,9999)
            session['otp']=otp
            body = "Thank you for changing the Password, your OTP is : " + str(otp)
            sender = "tamizhempire00@gmail.com"
            recipients = [email]
            password = "mtizgumdkbqgvhlh"
            send_email(subject, body, sender, recipients, password)
            return render_template("enterotppage.html", email = email)
        else:
            flash("Login Not Success")
            msg = 'Invalid EmailId'
            return render_template("forgotpassword.html", msg=msg)
    except Exception as e:
        return render_template("Login.html", msg=e)

@app.route("/checkotp", methods=["POST","GET"])
def checkotp():
    try:
        sentotp = request.form['otp']
        savedotp = session['otp']
        email=session['email']
        print("Saved Otp : ", savedotp, " Sent Otp : ", sentotp)
        if(int(sentotp)==int(savedotp)):
            return render_template("passwordchangepage.html", email = email)
        else:
            return render_template("enterotppage.html", email = email,msg='Incorrect OTP')
    except Exception as e:
        return render_template("Login.html", msg=e)

@app.route("/changepwd", methods=["POST","GET"])
def changepwd():
    try:
        pwd = request.form['pwd']
        email=session['email']
        sql="Update registration set password = '%s' where emailid = '%s'" % (pwd, email)
        print("Sql : ", sql)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        msg="Password Changes Success"
        return render_template("Login.html", msg=msg)
    except Exception as e:
        return render_template("Login.html", msg=e)

@app.route("/order",methods=["POST","GET"])
def order():
    if request.method=="POST":
        id=session['id']
        name=request.form["name"]
        game=request.form["game"]
        quantity=request.method["quantity"]
        sql="INSERT INTO order_table(userid,order_name,game_name,game_quantity) values('%s','%s','%s','%s')"%(id,name,game,quantity)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return render_template("order_table.html")
    return render_template("order_table.html")

@app.route("/payment",methods=["POST","GET"])
def payments():
    if request.method=="POST":
        transactionid=session['transactionid']
        payment=request.form["payment"]
        amount=request.form["amount"]
        status=request.form["status"]

        sql="INSERT INTO payments(transaction_id,payment_method,amount,payments_status)values('%s','%s','%s','%s')"%(transactionid,payment,amount,status)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return render_template("payments.html")
    return render_template("payments.html")

@app.route("/product",methods=["POST","GET"])
def product():
    msg=""
    if request.method=="POST":
        pname=request.form["pname"]
        price=request.form["price"]
        type=request.form["type"]

        sql="INSERT INTO products(product_name,price,product_type)values('%s','%s','%s')"%(pname,price,type)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        msg="Product Added Successfully"
        return render_template("product.html")
    return render_template("product.html")

@app.route("/transaction")
def transaction():
    msg=""
    if request.method=="POST":
        transactionid = session['transactionid']
        product_id=session['product_id']
        quantity=request.form["quantity"]
        total=request.form["total"]

        sql="INSERT INTO transactiondetails(transaction_id,product_id,quantity,subtotal)values('%s','%s','%s','%s')"%(transactionid,product_id,quantity,total)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return render_template("transactiondetails.html")
    return render_template("transactiondetails.html")

if __name__ == '__main__':
    app.run(debug=True, port=5001)