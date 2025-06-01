from flask import Flask,render_template,request,jsonify,redirect, url_for
from flask_mail import Mail, Message
import json

from db1 import Database1
from db2 import Database2
from db3 import Database3
from db4 import Database4
app = Flask(_name_)





dbo1=Database1()
dbo2=Database2()
dbo3=Database3()
dbo4=Database4()


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'suryapadala04@gmail.com'
app.config['MAIL_PASSWORD'] = 'tgir qlmy deyn oncj'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@app.route("/")
def index():
    return render_template("start.html")
@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/suv")
def suv():
    return render_template("suv.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/loginforvendor")
def loginforvendor():
    return render_template("loginforvendor.html")


@app.route("/perform_registration" , methods=["post"])
def perform_registration():
    name=request.form.get("user_name")
    email=request.form.get("user_email")
    password=request.form.get("user_password")
    response=dbo1.insert(name,email,password)
    if response:
        return render_template("login.html",message="Registration successfull please log in to proceed")
    else:
        return render_template("register.html",message="Email already exists")



@app.route("/perform_login",methods=["post"])
def perform_login():
    email = request.form.get("user_email")
    password = request.form.get("user_password")
    response=dbo1.search(email,password)
    if response:
        return render_template("findvendor.html",email=email)
    else:
        return render_template("login.html",message="Incorrect Email/Password")

@app.route("/perform_registration2",methods=["post"])
def perform_registration2():
    name=request.form.get("store_name")
    email=request.form.get("store_email")
    mobile=request.form.get("store_mobile")
    password=request.form.get("store_password")
    type=request.form.get("shop_type")
    address=request.form.get("shop_address")
    city=request.form.get("city")
    response=dbo2.insert(name,email,mobile,password,type,address,city)
    if response==1:
        with open("vendors.json", "r") as rf:
            vendors = json.load(rf)
            if email in vendors:
                type = vendors[email][3]
                city = vendors[email][5]
            with open("wdb.json", "r") as rff:
                whole_orders = json.load(rff)
                specific_orders = {}
                for i in whole_orders:
                    if whole_orders[i][0] == type and whole_orders[i][2] == city:
                        prod = whole_orders[i][1]
                        specific_orders[i] = [type, prod, city]
            return render_template("vendororders.html", orders=specific_orders, email=email)
    else:
        return "Something went wrong"

@app.route("/perform_login2",methods=["post"])
def perform_login2():
    email = request.form.get("user_email")
    password = request.form.get("user_password")
    response=dbo2.search(email,password)
    if response:
        with open("vendors.json", "r") as rf:
            vendors = json.load(rf)
            if email in vendors:
                type = vendors[email][3]
                city = vendors[email][5]
        with open("wdb.json","r") as rff:
            whole_orders = json.load(rff)
            specific_orders={}
            for i in whole_orders:
                if whole_orders[i][0]==type and whole_orders[i][2]==city:
                    prod=whole_orders[i][1]
                    specific_orders[i]=[type,prod,city]
        return render_template("vendororders.html",orders=specific_orders,email=email)
    else:
        return render_template("loginforvendor.html",message="Incorrect Email/Password")


@app.route("/pushdetailstodb",methods=["post"])
def pushdetailstodb():
    price = request.form.get("price")
    orderid = request.form.get("order_id")
    email = request.form.get("vendor_email")
    with open("vendors.json", "r") as rf:
        vendors = json.load(rf)
        if email in vendors:
            address=vendors[email][4]
            city=vendors[email][5]

    response=dbo4.insert(orderid,email,price,address,city)
    if response:
        return "Order details sent to customer"







@app.route("/perform_fruits")
def perform_fruits():
    email = request.args.get('email')
    type = request.args.get('type')
    return render_template("fruits.html",email=email,type=type)



@app.route("/perform_wdb",methods=["post"])
def perform_wdb():
    name = request.form.get("name")
    type1 = request.form.get("type")
    address = request.form.get("address")
    email=request.form.get("user_email")
    response = dbo3.insert(name, type1, address, email)







    # Load vendors from JSON file
    with open("vendors.json", "r") as rf:
        vendors = json.load(rf)

    # Find vendors that match the product type and place
    for email, details in vendors.items():
        vendor_type = details[3]
        vendor_place = details[5]
        if vendor_type == type1 and vendor_place == address:
            # Send email notification
            msg = Message(
                'New Product Request',
                sender='suryapadala9441@gmail.com',
                recipients=[email]
            )
            msg.body = f"A new request for {type1} in {address} has been made."
            mail.send(msg)

    return "Product request sent and notifications dispatched."







































@app.route("/show_orders")
def show_orders():
    email = request.args.get('email')

    # Load the orders the user has made
    with open("wdb.json", "r") as rf:
        w_orders = json.load(rf)
        # Only select orders where email matches the user
        order_ids = [i for i in w_orders if len(w_orders[i]) > 3 and w_orders[i][3] == email]

    # Load the accepted orders from vendors
    with open("acceptedorders.json", "r") as rf:
        a_orders = json.load(rf)
        new_dict = {}
        for i in a_orders:
            order_id, vendor_email = i.split("_")
            if order_id in order_ids:
                # Ensure the order_id is initialized properly in the new_dict
                if order_id not in new_dict:
                    new_dict[order_id] = []
                # Append vendor email, price, and address to the list
                price, address = a_orders[i][0], a_orders[i][1]
                new_dict[order_id].append({"vendor_email": vendor_email, "price": price, "address": address})

    return render_template("show_orders.html", orders=new_dict,email=email)


@app.route("/accept_reject_order", methods=["POST"])
def accept_reject_order():
    order_id = request.form.get("order_id")
    vendor_email = request.form.get("vendor_email")
    action = request.form.get("action")
    user_email = request.form.get("user_email")

    with open("acceptedorders.json", "r") as rf:
        accepted_orders = json.load(rf)

    # Perform action based on whether the user accepted or rejected the order
    if action == "accept":
        # Update the order status to "confirmed"
        key = f"{order_id}_{vendor_email}"
        if key in accepted_orders:
            accepted_orders[key].append("confirmed")
        else:
            accepted_orders[key] = ["", "", "confirmed"]

        with open("acceptedorders.json", "w") as wf:
            json.dump(accepted_orders, wf, indent=4)

        with open("vendors.json", "r") as rf:
            vendors = json.load(rf)
            email, name, number, address = vendor_email, vendors[vendor_email][0], vendors[vendor_email][1], \
            vendors[vendor_email][4]
        return render_template("main_vendor_details.html", email=email, name=name, number=number, address=address)


    elif action == "reject":
        # You can also update the status to "rejected" if necessary
        key = f"{order_id}_{vendor_email}"
        if key in accepted_orders:
            del accepted_orders[key]

        # Save the updated orders back to the JSON file
        with open('acceptedorders.json', 'w') as wf:
            json.dump(accepted_orders, wf, indent=4)

        return redirect(url_for('show_orders', email=user_email))



@app.route("/request_product", methods=["POST"])
def request_product():
    product_type = request.form.get("product_type")
    place = request.form.get("place")

    # Load vendors from JSON file
    with open("vendors.json", "r") as rf:
        vendors = json.load(rf)

    # Find vendors that match the product type and place
    for email, details in vendors.items():
        vendor_type = details[3]
        vendor_place = details[5]
        if vendor_type == product_type and vendor_place == place:
            # Send email notification
            msg = Message(
                'New Product Request',
                sender='suryapadala04@gmail.com',
                recipients=[email]
            )
            msg.body = f"A new request for {product_type} in {place} has been made."
            mail.send(msg)

    return "Product request sent and notifications dispatched."




app.run(debug=True)     what is this code