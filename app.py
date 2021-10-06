import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
from sqlalchemy import orm

app = Flask(__name__)

# postgress
db = SQLAlchemy()
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3307/dtm"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dtm.db"
app.config['SECRET_KEY'] = "random string"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "abcabc"
db.init_app(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DATE, default=datetime.now(), nullable=False)
    


class Ser(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(20))
    sprice = db.Column(db.Float(11))


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    service_id = db.Column(db.Integer)
    details = db.Column(db.Text(100))
    height = db.Column((db.Float), nullable=False)
    width = db.Column((db.Float), nullable=False)
    order_date = db.Column(db.DATE, default=datetime.now(), nullable=False)
    price = db.Column(db.Float(30))


class Image(db.Model):
    __tablenmae__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300))


@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":

        email = request.form.get("email1")
        password = request.form.get("password1")
        
       

        user = User.query.filter_by(email=email, password=password).first()
        
    
        if user :
            session['username'] = email
            session['name'] = user.name
            session['id'] = user.id
            session['phone'] = user.phone
            
            if not session['username']=='khan.ar920@gmail.com':
                flash('Wellcome in DTM ','success')
                return redirect(url_for("home"))
                
            else:
                session['admin']= user.email
                flash('Wellcome!','success')
                return redirect(url_for("admin"))
            

        else:
            flash('Username and password doesnot match','warning')

    return render_template("login2.html")


@app.route("/", methods=['GET'])
def home():
    return render_template("Home.html")


@app.route("/About", methods=['GET', 'POST'])
def about():
    return render_template("About.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template("Contact.html")


@app.route("/portfolio", methods=['GET', 'POST'])
def portfolio():
    img = Image.query.all()
    servic = Ser.query.all()

    if request.method == "POST":
        if 'username' in session:
            uid = session['id']
            service = request.form.get("Service")
            details = request.form.get("message")
            height = request.form.get("height")
            wight = request.form.get("weight")

            price = Ser.query.filter(
            Ser.id == request.form.get('Service')).first()

            service = Order(user_id=uid, service_id=service, order_date=datetime.now(),
                            details=details, height=height, width=wight, price=price.sprice)

            db.session.add(service)
            db.session.commit()
            flash('Thank you! Your Order has been Placed','success')
            return redirect(url_for('order'))
        else:
            flash('There is some Error Please check are you login!','danger')
            return redirect(url_for('login'))

    else:

        return render_template("PORTFOLIO3.html", service=servic,img=img)


@app.route("/order", methods=['GET', 'POST'])
def order():
    if not session.get('username'):
        flash('Please login first','warning')
        return render_template("login2.html")

    ord = db.session.query(User, Order, Ser).\
        filter(Order.service_id == Ser.id).\
        filter(Order.user_id == User.id).\
        filter(User.id == session['id']).order_by(
            Order.order_date.desc()).all()

    return render_template("Orders.html", ord=ord)



@app.route('/masteruser', methods=['GET', 'POST'])
def admin():
    
    
    if session.get('admin') :
        
        user = User.query.all()
        service = Ser.query.all()

        ord = db.session.query(User, Order, Ser).\
        filter(Order.service_id == Ser.id).\
        filter(Order.user_id == User.id).order_by(
        Order.order_date.desc()).all()
        return render_template('admin2.html', user=user,service=service, ord=ord)

    else:
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login2.html")

    return render_template('admin2.html', user=user,service=service, ord=ord)
      



@app.route("/reg", methods=['GET', 'POST'])
def reg():

    if request.method == "POST":
        name = request.form.get("name").lower()
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        user = User.query.filter_by(email=email).first()
        if not user:
            # Creat new record

            usere = User(name=name, email=email,
                         password=password, phone=phone)

            db.session.add(usere)
            db.session.commit()
            flash('Successfully register!','success')
            return render_template("login2.html")

        else:
            flash('Username or Email already exists','danger')
            return render_template("reg.html")

    return render_template("reg.html")

@app.route("/table/orders",methods=['GET', 'POST'])
def ordtab():

    if session.get('admin') :
        user = User.query.all()
        service = Ser.query.all()
        
        ord = db.session.query(User, Order, Ser).\
        filter(Order.service_id == Ser.id).\
        filter(Order.user_id == User.id).order_by(Order.order_date.desc()).all()
        
        if request.method == 'POST' and 'tag' in request.form:
            name = request.form.get("name")
       
       
            tag = request.form["tag"]
            search = "%{}%".format(tag) 


            ord = db.session.query(User, Order, Ser).\
            filter(Order.service_id == Ser.id).\
            filter(Order.user_id == User.id).order_by(
            Order.order_date.desc()).filter(User.name.like(search)).all()
            return render_template('ordtab.html', user=user,service=service, ord=ord , tag=tag)
        
    else:
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login2.html")
    
    return render_template('ordtab.html', user=user,service=service, ord=ord)

    
@app.route("/table/users",methods=['GET', 'POST'])
def ustab():

    if session.get('admin') :
        user = User.query.all()
        ord = db.session.query(User, Order, Ser).\
        filter(Order.service_id == Ser.id).\
        filter(Order.user_id == User.id).order_by(Order.order_date.desc()).all()
        
        if request.method == 'POST' and 'tag' in request.form:
            name = request.form.get("name")
       
       
            tag = request.form["tag"]
            search = "%{}%".format(tag) 

            user = User.query.filter(User.name.like(search)) 
       

            return render_template('ustab.html', user=user,tag=tag, ord=ord)
        
        else:
            return render_template('ustab.html', user=user,ord=ord )
    else:
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login2.html")

@app.route("/table/service",methods=['GET', 'POST'])
def sertab():

     if session.get('admin') :
         
         service = Ser.query.all()
         ord = db.session.query(User, Order, Ser).\
         filter(Order.service_id == Ser.id).\
         filter(Order.user_id == User.id).order_by(Order.order_date.desc()).all()
         
         if request.method == 'POST':
             
             if 'tag' in request.form:
                 
                 tag = request.form["tag"]
                 search = "%{}%".format(tag) 

                 service = Ser.query.filter(Ser.sname.like(search))
                 return render_template('sertab.html', service=service,tag=tag,ord=ord)

             else:
                 price = request.form.get("price")
                 name = request.form.get("name").lower()
                 chek = Ser.query.filter_by(sname=name).first()
                 
                 if not chek:
                    new = Ser(sprice=price, sname=name)
                    db.session.add(new)
                    db.session.commit() 
                    service = Ser.query.all()
                    flash('Successfully Entered!','success')
                    return render_template('sertab.html', service=service, ord=ord)
                 else:
                    flash('Already Exists!','danger')
                    return render_template('sertab.html', service=service,ord=ord)
    
         else:
               return render_template('sertab.html', service=service,ord=ord )

     else:
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login2.html")

@app.route("/update/service/<id>", methods=['GET', 'POST'])
def update_ser(id):

    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login2.html")
    else:
        ord = db.session.query(User, Order, Ser).\
        filter(Order.service_id == Ser.id).\
        filter(Order.user_id == User.id).order_by(Order.order_date.desc()).all()
        
        if request.method=="POST":
            price = request.form.get("price")
            name = request.form.get("name")
            
            #serv = db.session.query(Ser).filter_by(id=id).first()
            serv = Ser.query.filter_by(id = id).first()
            serv.sname = name
            serv.sprice = price
            db.session.commit()
            return redirect(url_for('sertab'))
        else:
            serv = Ser.query.filter(Ser.id == id).first()
            return render_template("upser.html", serv=serv,ord=ord)
@app.route("/update/user/<id>", methods=['GET', 'POST'])
def update_user(id):
    ord = db.session.query(User, Order, Ser).\
    filter(Order.service_id == Ser.id).\
    filter(Order.user_id == User.id).order_by(Order.order_date.desc()).all()
    
    if request.method=="POST":
        
        name = request.form.get("name").lower()
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
            
        #serv = db.session.query(Ser).filter_by(id=id).first()
        useru = User.query.filter_by(id = id).first()
        useru.name = name
        useru.email = email
        useru.password = password
        useru.phone= phone
        db.session.commit()
        flash('Successfully Updated!','success')
        return redirect(url_for('ustab'))

    else:
        serv = User.query.filter(User.id == id).first()
        return render_template("upuser.html", serv=serv,ord=ord)

@app.route("/delete/user/<id>", methods=['GET', 'POST'])
def delete_user(id):
    
             
       
        duser = User.query.filter(User.id==id).first()

        db.session.delete(duser)
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('ustab'))

@app.route("/delete/service/<id>", methods=['GET', 'POST'])
def delete_ser(id):
    
             
       
        serv = Ser.query.filter(Ser.id==id).first()

        db.session.delete(serv)
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('sertab'))

@app.route("/delete/order/<id>", methods=['GET', 'POST'])
def delete_ord(id):
    
             
       
        uord = Order.query.filter(Order.id==id).first()

        db.session.delete(uord)
        
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('ordtab'))


@app.route("/add/user", methods=['GET', 'POST'])
def adduser():
    
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login2.html")
    else:
        user = User.query.all()
        ord = db.session.query(User, Order, Ser).\
        filter(Order.service_id == Ser.id).\
        filter(Order.user_id == User.id).order_by(Order.order_date.desc()).all()
        
        if request.method == "POST":
            name = request.form.get("name").lower()
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")

            user = User.query.filter_by(email=email).first()
            if not user:
            # Creat new record
                usere = User(name=name, email=email,password=password, phone=phone)

                db.session.add(usere)
                db.session.commit()
                flash('Successfully added!','success')
                return redirect(url_for('ustab'))

            else:
                flash('Username or Email already exists','danger')
                return redirect (url_for(('adduser')))
 
        return render_template('adduser.html', user=user,ord=ord)    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


    


if __name__ == "__main__":
    app.run()
