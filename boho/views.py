from audioop import add
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from sqlalchemy import false, true
from twilio.rest import Client
import random as r
from .models import Cart, Catlog, ContactUsCustomers, ContactUsSellers, CustomerDetails, SalesDone, SellerDetails, Installers, Transporters, Orders, Products, check_availability
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
import re
import os
import smtplib
from email.message import EmailMessage
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from datetime import date
from website.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY,BASE_DIR
import razorpay
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# This will fetch all the products from the table and show to the user
def index(request):
    allproducts = []
    resp = {"Products": allproducts}
    catblogs = Products.objects.values('category', 'product_id')
    cats = {post['category'] for post in catblogs}
    for cat in cats:
        cat1 = list(Products.objects.filter(category=cat).values())
        allproducts.append(cat1)
        # resp["Products"].append(cat1)
        # params = {'allproducts': allproducts}
    if request.user.is_authenticated:
        username = request.user
        print(username)
        registered_nos = CustomerDetails.objects.get(cust_phone_no=username)
        check = []
        name=registered_nos.cust_phone_no
        if len(name)>0:
                params = {'allproducts': allproducts}
                # return render(request, "index.html", params)
                return JsonResponse(resp)
        else:
            Seller_details = SellerDetails.objects.filter(
                    phoneno=username)
            loggedin = 'true'
            addedproducts=Products.objects.filter(seller_phone_no=username)
            context = {'loggedin': loggedin,'sellerdetails':Seller_details,"addedproducts":addedproducts}
            # return render(request, "seller.html", context)
            return JsonResponse(resp)
    else:
        # params = {'allproducts': allproducts}
        # return render(request, "index.html", params)
        return JsonResponse(resp)

# This page will show the detailed view of the product 
def productdetailedview(request,id):
    product=Products.objects.filter(product_id=id)
    return render(request, "productDescriptionPage.html",{'product':product[0]})

# This function will fetch all the phone numbers and send them to the register.html
def signup(request):
    registered_nos = CustomerDetails.objects.values('cust_phone_no')
    check = []
    for check2 in registered_nos:
        check.append(check2['cust_phone_no'])
    context = {'check': check}
    return render(request, "createAccount.html", context)

# This will send the otp the number entered and collect the data of the customer
def signupotp(request):
    if request.user.is_authenticated:
        return redirect("/")
    otp = ''
    if request.method == 'POST':
        cust_name = request.POST.get('name')
        phoneno = request.POST.get('phoneno')
        email=request.POST.get('email')
        role = request.POST.get('role')
        lookingfor = request.POST.get('lookingfor')
        companyname=request.POST.get('companyname')
        registered_nos = User.objects.values('username')
        check = []
        for check2 in registered_nos:
            check.append(check2['username'])
        flag = true
        for i in check:
            if phoneno == i:
                flag = false

        if flag == true:
            client = Client("AC8a145f355071d06362834e5fad001b7b",
                            "798612b1735ee3e167e66d7a61416d9c")
            otp = str(r.randint(1000, 9999))
            client.messages.create(
                to=["+91"+phoneno], from_="+15185165876", body=otp)
            otpnumber = {'otp': otp, 'phoneno': phoneno,
                         'custname': cust_name, 'role': role, 'lookingfor': lookingfor,'email':email,'companyname':companyname}
            print("otp sent for signup")
            return render(request, "otpVerification.html", otpnumber)
        else:
            registered_nos = CustomerDetails.objects.values('cust_phone_no')
            check = []
            for check2 in registered_nos:
                check.append(check2['cust_phone_no'])
            wrongno = 'true'
            context = {'check': check, 'wrongno': wrongno}

            return render(request, "createAccount.html", context)

# This will check whether the entered otp and the required otp are same or not
def signupotp2(request):
    print("working")
    if request.user.is_authenticated:
        return redirect("/")
    accountcreated = 'false'
    if request.method == 'POST':
        enteredotp = request.POST.get('enteredotp')
        name = request.POST.get('name')
        phoneno = request.POST.get('phoneno')
        role = request.POST.get('role')
        lookingfor = request.POST.get('lookingfor')
        otp = request.POST.get('otp')
        companyname=request.POST.get('companyname')
        email=request.POST.get('email')
        if enteredotp == otp:
            user = User.objects.create_user(
                username=phoneno, password=phoneno, email=email, first_name=name, last_name=name)
            user.save()
            Customer_Details = CustomerDetails(
                cust_name=name, cust_phone_no=phoneno, cust_role=role, lookingfor=lookingfor,email=email,companyname=companyname)
            Customer_Details.save()
            accountcreated = 'true'
            context = {'accountcreated': accountcreated}
            return render(request, "login copy.html", context)
    return render(request, "otpVerification.html")


def signin(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "login copy.html")

# This will send the otp the number entered if the entered number has any account associated with it
def signinotp(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        phoneno = request.POST.get('phoneno')
        registered_nos = CustomerDetails.objects.values('cust_phone_no')
        check = []
        for check2 in registered_nos:
            check.append(check2['cust_phone_no'])
        flag = false
        for i in check:
            if phoneno == i:
                flag = true
        if flag == true:
            client = Client("AC8a145f355071d06362834e5fad001b7b",
                            "798612b1735ee3e167e66d7a61416d9c")
            otp = str(r.randint(1000, 9999))
            client.messages.create(
                to=["+91"+phoneno], from_="+15185165876", body=otp)
            context = {'otp': otp, 'cust_no': phoneno}
            return render(request, "loginotpverification.html", context)
        else:
            invalid = "invalid"
            context = {'invalid': invalid}
            return render(request, "login copy.html", context)

# This will check whether the entered otp and the required otp are same or not
def signinotp2(request):
    loggedin = 'false'
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        enteredotp = request.POST.get('enteredotp')
        requiredotp = request.POST.get('requiredotp')
        cust_no = request.POST.get('phoneno')
        if enteredotp == requiredotp:
            user = auth.authenticate(username=cust_no, password=cust_no)
            if user is not None:
                Cust_details = CustomerDetails.objects.filter(
                    cust_phone_no=cust_no)
                auth.login(request, user)
                loggedin = 'true'
                allproducts = []
                catblogs = Products.objects.values('category', 'product_id')
                cats = {post['category'] for post in catblogs}
                for cat in cats:
                    cat1 = Products.objects.filter(category=cat)
                    allproducts.append(cat1)
                params = {'allproducts': allproducts,'loggedin': loggedin}
                return render(request, "index1.html",params)
    return render(request, "loginotpverification.html")

# This is the logout function for the customer
def customerlogout(request):
    if request.user.is_authenticated:
            logout(request)
            return redirect("/")
    else:
        logout(request)
        return redirect("/")

            
def aboutus(request):
    return render(request, "aboutus.html")


def contactuscustomer(request):
    return render(request, "contactus.html")


def contactuscustomer2(request):
    if request.method=="POST":
        query=request.POST.get("query")
        if request.user.is_authenticated:
            username = request.user
            customerdetails = CustomerDetails.objects.get(cust_phone_no=username)
            cust_id = customerdetails.cust_id
            cust_name = customerdetails.cust_name
            cust_date="date"
            cust_time="time"
            cust_phoneno = username
            instance=ContactUsCustomers(cust_id=cust_id,name=cust_name,query=query,date=cust_date,time=cust_time,mobile_no=cust_phoneno)
            instance.save()
            return render(request, "contactus.html")
        else:
            return render(request,"login copy.html")

def contactusseller(request):
    return render(request, "contactus.html")

def contactusseller2(request):
    if request.method=="POST":
        query=request.POST.get("query")
        if request.user.is_authenticated:
            username = request.user
            customerdetails = SellerDetails.objects.get(cust_phone_no=username)
            cust_id = customerdetails.cust_id
            cust_name = customerdetails.cust_name
            cust_date="date"
            cust_time="time"
            cust_phoneno = username
            instance=ContactUsSellers(cust_id=cust_id,name=cust_name,query=query,date=cust_date,time=cust_time,mobile_no=cust_phoneno)
            instance.save()
            return render(request, "contactus.html")
        else:
            return render(request,"login copy.html")

# This will take a input from the search form and show the products that match the entered words
def search(request):
    if request.method == 'POST':
        search=request.POST.get("search")
        allproducts = []
        catblogs = Products.objects.values('category', 'product_id')
        cats = {post['category'] for post in catblogs}
        for cat in cats:
            cat1 = Products.objects.filter(category=cat)
            allproducts.append(cat1)
            params = {'allproducts': allproducts}

        allprods=[]
        for allprods2 in allproducts:
            for allprods3 in allprods2:
                if re.search(search,allprods3.name) or re.search(search,allprods3.category):
                    allprods.append(allprods3)
        context={'allprods':allprods}
        return render(request, "search.html",context)

# This will fetch the user phoneno and after that it will fetch product data from cart which has the phonenumber of the requested user
def cartproducts(request):
    if request.user.is_authenticated:
        username = request.user
        allords = []
        custid=CustomerDetails.objects.get(cust_phone_no=username)
        custid2=custid.cust_id
        catblogs = Cart.objects.values('cust_id')
        cat1=""
        cats = {ords['cust_id'] for ords in catblogs}
        for cat in cats:
            cat1 = Cart.objects.filter(cust_id=custid2)
        allords.append(cat1)
        noproducts="no"
        if allords==['']:
            context={'noproducts':noproducts}
        else:
            context = {'allords':allords}
        return render(request, "cart.html",context)
    else:
        return redirect("/signin")



# This will fetch the user phoneno and after that it will fetch product data from catlog which has the phonenumber of the requested user
def catlogproducts(request):
    if request.user.is_authenticated:
        username = request.user
        allords = []
        custid=CustomerDetails.objects.get(cust_phone_no=username)
        custid2=custid.cust_id
        catblogs = Catlog.objects.values('cust_id')
        cat1=""
        cats = {ords['cust_id'] for ords in catblogs}
        for cat in cats:
            cat1 = Catlog.objects.filter(cust_id=custid2)
        allords.append(cat1)
        noproducts="no"
        if allords==['']:
            context={'noproducts':noproducts}
        else:
            context = {'allords':allords}

        return render(request, "catlog-page.html",context)
    else:
        return redirect("/signin")

# This will send the request to check the availability of the requested product
def checking(request):
    if request.user.is_authenticated:
        noofcart=request.POST.get("noofcart")
        quantity=request.POST.get("qty")
        Cart.objects.filter(no_of_cart=noofcart).update(qty=quantity,checkingavailability="true")
        return redirect("/cartproducts")
    else:
         return redirect("/signin")




# It will add the product data to the catlog as well as to the cart simultaneously
def addtocatlogs(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user
            productid = request.POST.get('productid')
            productname=request.POST.get('productname')
            description=request.POST.get('description')
            cost=request.POST.get('cost')
            pickuplocation=request.POST.get('pickuplocation')
            image=request.POST.get('image')
            qty=request.POST.get('qty')
            totalcost=int(cost)*int(qty)
            customerdetails = CustomerDetails.objects.get(cust_phone_no=username)
            added_to_catlogs=Catlog(product_id=productid,cust_id=customerdetails.cust_id,name=productname,
            description=description,cost=cost,pickuplocation=pickuplocation,image=image).save()
            added_to_cart=Cart(product_id=productid,cust_id=customerdetails.cust_id,name=productname,
            description=description,cost=cost,totalcost=totalcost,pickuplocation=pickuplocation,image=image,checkingavailability="true",qty=qty)
            added_to_cart.save()
            noofcart=added_to_cart.no_of_cart
            return redirect("/signin")
        else:
            return redirect("/signin")
    else:
        return redirect("/signin")

# This will fetch the user phoneno and after that it will fetch product data from orders which has the phonenumber of the requested user
def myorders(request):
    if request.user.is_authenticated:
        username = request.user
        allords = []
        catblogs = Orders.objects.values('customer_phone_no')
        cat1=""
        cats = {ords['customer_phone_no'] for ords in catblogs}
        for cat in cats:
            cat1 = Orders.objects.filter(customer_phone_no=username)
        allords.append(cat1)
        noproducts="no"
        if allords==[''] :
            context={'noproducts':noproducts}
        else:
            context = {'allords':allords}
        return render(request, "order-page.html", context)
    else:
        return redirect("/signin")


# This will delete the product data from the cart
def removefromcart(request):
    if request.user.is_authenticated:
        noofcart=request.POST.get('noofcart')
        Cart.objects.filter(no_of_cart=noofcart).delete()
        return redirect("/cartproducts")
    else:
        return redirect("/signin")



def sellersignup(request):
    checkno=User.objects.values('username')
    return render(request, "sellersignup2.html")

def sellersignupotp(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        name=request.POST.get("name")
        phoneno=request.POST.get("phoneno")
        address=request.POST.get("product_pickup_address")
        registered_nos = User.objects.values('username')
        check = []
        for check2 in registered_nos:
            check.append(check2['username'])
        flag = true
        for i in check:
            if phoneno == i:
                flag = false

        if flag == true:
            client = Client("AC8a145f355071d06362834e5fad001b7b",
                            "798612b1735ee3e167e66d7a61416d9c")
            otp = str(r.randint(1000, 9999))
            client.messages.create(
                to=["+91"+phoneno], from_="+15185165876", body=otp)
            otpnumber = {'otp': otp, 'phoneno': phoneno,
                         'sellername': name, 'address':address}
            return render(request, "sellersignupotp.html",otpnumber)
        else:
            flag="false"
            context={'flag':flag}
            return render(request, "sellersignup2.html",context)

def sellersignupotp2(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        name=request.POST.get("name")
        phoneno=request.POST.get("phoneno")
        address=request.POST.get("address")
        email=request.POST.get("email")
        seller=SellerDetails(name=name,phoneno=phoneno,default_pickup_address=address).save()
        user = User.objects.create_user(
                username=phoneno, password=phoneno, email=email, first_name=name, last_name=name)
        user.save()
        accounted_created="true"
        context={'account_created':accounted_created}
        return render(request,"sellersignup2.html",context)

def sellersignin(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "sellerlogin.html")

def sellersigninotp(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        phoneno = request.POST.get('phoneno')
        registered_nos = SellerDetails.objects.values('phoneno')
        check = []
        for check2 in registered_nos:
            check.append(check2['phoneno'])
        flag = false
        for i in check:
            if phoneno == i:
                flag = true
        if flag == true:
            client = Client("AC8a145f355071d06362834e5fad001b7b",
                            "798612b1735ee3e167e66d7a61416d9c")
            otp = str(r.randint(1000, 9999))
            client.messages.create(
                to=["+91"+phoneno], from_="+15185165876", body=otp)
            context = {'otp': otp, 'cust_no': phoneno}
            return render(request, "sellersigninotp.html", context)
        else:
            invalid = "invalid"
            context = {'invalid': invalid}
            return render(request, "sellerlogin.html", context)

def sellersigninotp2(request):
    if request.user.is_authenticated:
        return redirect("/")
    loggedin = 'false'
    if request.method == 'POST':
        enteredotp = request.POST.get('enteredotp')
        requiredotp = request.POST.get('requiredotp')
        cust_no = request.POST.get('phoneno')
        if enteredotp == requiredotp:
            user = auth.authenticate(username=cust_no, password=cust_no)
            if user is not None:
                auth.login(request, user)
                Seller_details = SellerDetails.objects.filter(
                phoneno=cust_no)
                loggedin = 'true'
                addedproducts=Products.objects.filter(seller_phone_no=cust_no)
                context = {'loggedin': loggedin,'sellerdetails':Seller_details,"addedproducts":addedproducts}
                return render(request, "seller1.html", context)
    else:
        wrongotp="true"
        context={"wrongotp":wrongotp}
        return render(request, "sellersigninotp.html",context)

def addproduct(request):
    if request.user.is_authenticated:
        return render(request, "seller-addproduct.html")
    else:
        return redirect("/signin")

# Seller will add the product
def addproduct2(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user
            category=request.POST.get("category")
            name=request.POST.get("name")
            color=request.POST.get("color")
            size=request.POST.get("size")
            material=request.POST.get("material")
            description=request.POST.get("description")
            cost=request.POST.get("cost")
            pickuplocation=request.POST.get("pickuplocation")
            productpic=request.FILES['image']
            sellerdetails=SellerDetails.objects.get(phoneno=username)
            sellerid=sellerdetails.seller_id
            sellername=sellerdetails.name
            product=Products(category=category,name=name,color=color,size=size,material=material,description=description,seller_id=sellerid,seller_name=sellername,seller_phone_no=username,cost=cost,pickup_location=pickuplocation,image=productpic)
            product.save()
            productadded="true"
            context={
                'productadded':productadded
            }
            return render(request, "seller-addproduct.html",context)
        else:
            return redirect("/signin")
    else:
        return redirect("/signin")

# seller will delete the product
def deleteproduct(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            productid=request.POST.get("productid")
            instance = Products.objects.get(product_id=productid)
            instance.delete()
            productdelete="true"
            context={
                'productdelete':productdelete
            }
            username = request.user
            addedproducts=Products.objects.filter(seller_phone_no=username)
            Seller_details = SellerDetails.objects.filter(
                    phoneno=username)
            context = {'sellerdetails':Seller_details,"addedproducts":addedproducts}
            return render(request, "seller1.html",context)
        else:
            return redirect("/")
    else:
        return redirect("/signin")

# Seller will logout from here
def sellerlogout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return render(request, "sellerlogin.html")
    else:
        logout(request)
        return render(request, "sellerlogin.html")

# Here the order creation for the 50% amount of the  razorpay takes place
def testrazorpay(request):
    if request.method=="POST" and request.user.is_authenticated:
        productid=request.POST.get("productid")
        productname=request.POST.get("productname")
        cost=request.POST.get("cost")
        qty=request.POST.get("qty")
        dropaddress=request.POST.get("dropaddress")
        totalcost=request.POST.get("totalcost")
        noofcart=request.POST.get("noofcart")
        image=request.POST.get("image")
        needinstallers=request.POST.get('needinstallers')
        amount=(int(totalcost)*100)/2
        order_currency='INR'
        client=razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))
        # print("Total cost is rs:"+str(totalcost))
        payment=client.order.create({'amount':amount,'currency':order_currency,"payment_capture":"1"})
        context={'productid':productid,'productname':productname,'cost':cost,'qty':qty,
                    'dropaddress':dropaddress,'totalcost':totalcost,'amount':amount,'needinstallers':needinstallers,
                    'noofcart':noofcart,'image':image,'razorpay_api_key':RAZORPAY_API_KEY}
        return render(request,'testpay.html',context)
    else:
        return redirect("/signin")

# here after the 50% payment the order details get stored in the database and it gets deleted from the cart
# The bill also gets generated for the 50% payment in the form of pdf and it gets mailed to both the customer and the backend team
@csrf_exempt
def afterpaypage(request):
    if request.method=="POST" and request.user.is_authenticated:
        productid=request.POST.get("productid")
        productname=request.POST.get("productname")
        cost=request.POST.get("cost")
        qty=request.POST.get("qty")
        dropaddress=request.POST.get("dropaddress")
        custno=request.user
        customerdtails=CustomerDetails.objects.get(cust_phone_no=custno)
        custname=customerdtails.cust_name
        custno=customerdtails.cust_phone_no
        sellerdetails=Products.objects.get(product_id=productid)
        sellerid=sellerdetails.seller_id
        # sellerno=sellerdetails.seller_phone_no
        sellername=sellerdetails.seller_name
        pickuplocation=sellerdetails.pickup_location
        image=request.POST.get('image')
        totalcost=int(cost)*int(qty)
        orderdate=date.today()
        fiftypercent_payment="true"
        needinstallers=request.POST.get('needinstallers')
        confirmorder=Orders(product_id=productid,productname=productname,quantity=qty,
            cust_name=custname,seller_id=sellerid,sellers_name=sellername,
            needinstallers=needinstallers,dropaddress=dropaddress,
            customer_phone_no=custno,total_price=totalcost,date=orderdate,
            fifty_percent_payment=fiftypercent_payment,pickupaddress=pickuplocation,image=image)
        confirmorder.save()

        noofcart=request.POST.get("noofcart")
        deletecartproduct=Cart.objects.filter(no_of_cart=noofcart).delete()
        
        # Content
        fileName = str(confirmorder.order_id)+"_orderid_fiftypercent.pdf"
        documentTitle = 'Payment receipt'
        title = '50% Payemnt receipt for orderno'+str(confirmorder.order_id)
        subTitle = 'From Boho'

        orderdetails=Orders.objects.get(order_id=confirmorder.order_id)
        orderitemname=orderdetails.productname
        orderitemqty=orderdetails.quantity
        ordertotalprice=orderdetails.total_price
        ordersingleitemcost=int(ordertotalprice)/int(orderitemqty)

        textLines = [
            str(orderitemname)+
            str(ordersingleitemcost)+
            str(orderitemqty)+
           str(ordertotalprice)
        ]

        # 0) Create document  

        pdf = canvas.Canvas(fileName)
        pdf.setTitle(documentTitle)

        pdf.drawCentredString(300, 770, title)


        pdf.setFillColorRGB(0, 0, 255)
        pdf.setFont("Courier-Bold", 24)
        pdf.drawCentredString(290,720, subTitle)

        # 3) Draw a line
        pdf.line(30, 710, 550, 710)

        # 4) Text object :: for large amounts of text
        from reportlab.lib import colors

        text = pdf.beginText(40, 680)
        text.setFont("Courier", 18)
        text.setFillColor(colors.black)
        for line in textLines:
            text.textLine(line)

        pdf.drawText(text)

        pdf.save()


    # Sending the generated bill in pdf format to both the customer and admin
        contacts = ['boho0105@gmail.com', 'boho0105@gmail.com']

        msg = EmailMessage()
        msg['Subject'] = 'Payment receipt'
        msg['From'] = 'boho0105@gmail.com'
        msg['To'] = 'boho0105@gmail.com'

        msg.set_content('PDF attached')

        with open(fileName,'rb') as f:
            file_data=f.read()
            f_name=f.name
            

        msg.add_attachment(file_data,maintype='application',subtype='octet-stream',filename=f_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('boho0105@gmail.com', 'adiptkedia')
            # smtp.send_message(msg)
            smtp.sendmail("boho0105@gmail.com","boho0105@gmail.com", msg.as_string())
        
        print("mail sent")
        os.remove(fileName)
        print("file deleted")

        fiftypaid='true'
        allproducts = []
        catblogs = Products.objects.values('category', 'product_id')
        cats = {post['category'] for post in catblogs}
        for cat in cats:
            cat1 = Products.objects.filter(category=cat)
            allproducts.append(cat1)
        params = {'allproducts': allproducts,'fiftypaid':fiftypaid}
        return render(request, "index1.html", params)

    else:
        return redirect("/signin")

# Here the order creation for the 100% amount of the  razorpay takes place
def fullpayment(request):
    if request.method=="POST" and request.user.is_authenticated:
        orderid=request.POST.get("orderid")
        totalprice=request.POST.get('totalprice')
        remainingcost=(int(totalprice)/2)*100
        order_currency="INR"
        client=razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))
        payment=client.order.create({'amount':remainingcost,'currency':order_currency,"payment_capture":"1"})
        context={'amount':remainingcost,'razorpay_api_key':RAZORPAY_API_KEY,'orderid':orderid}
        return render(request,'fullpayment.html',context)


# here after the 100% payment the generated bill gets mailed to the customer as well as to the backend team as a proof
@csrf_exempt
def afterfullpayment(request):
    if request.method=="POST" and request.user.is_authenticated:
        orderid=request.POST.get("orderid")
        print(orderid)
        order=Orders.objects.filter(order_id=orderid).update(hundred_percent_payment='true')
        
        # Content
        fileName = str(orderid)+"_orderid_fullpayment.pdf"
        documentTitle = 'Payment receipt'
        title = '!00% Payemnt receipt for orderno'+str(orderid)
        subTitle = 'From Boho'

        orderdetails=Orders.objects.get(order_id=orderid)
        orderitemname=orderdetails.productname
        orderitemqty=orderdetails.quantity
        ordertotalprice=orderdetails.total_price
        ordersingleitemcost=int(ordertotalprice)/int(orderitemqty)
        # print(orderitemname,orderitemqty,ordertotalprice,ordersingleitemcost)

        textLines = [
            str(orderitemname)+
            str(ordersingleitemcost)+
            str(orderitemqty)+
           str(ordertotalprice)
        ]

        # 0) Create document  

        pdf = canvas.Canvas(fileName)
        pdf.setTitle(documentTitle)

        pdf.drawCentredString(300, 770, title)


        pdf.setFillColorRGB(0, 0, 255)
        pdf.setFont("Courier-Bold", 24)
        pdf.drawCentredString(290,720, subTitle)

        # 3) Draw a line
        pdf.line(30, 710, 550, 710)

        # 4) Text object :: for large amounts of text
        from reportlab.lib import colors

        text = pdf.beginText(40, 680)
        text.setFont("Courier", 18)
        text.setFillColor(colors.black)
        for line in textLines:
            text.textLine(line)

        pdf.drawText(text)

        pdf.save()


    # Sending the generated bill in pdf format to both the customer and admin
        contacts = ['boho0105@gmail.com', 'boho0105@gmail.com']

        msg = EmailMessage()
        msg['Subject'] = 'Payment receipt'
        msg['From'] = 'boho0105@gmail.com'
        msg['To'] = 'boho0105@gmail.com'

        msg.set_content('PDF attached')

        with open(fileName,'rb') as f:
            file_data=f.read()
            f_name=f.name
            

        msg.add_attachment(file_data,maintype='application',subtype='octet-stream',filename=f_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(' boho0105@gmail.com', 'adiptkedia')
            # smtp.send_message(msg)
            smtp.sendmail("boho0105@gmail.com","boho0105@gmail.com", msg.as_string())
        
        print("mail sent")
        os.remove(fileName)
        print("file deleted")
        allproducts = []
        catblogs = Products.objects.values('category', 'product_id')
        cats = {post['category'] for post in catblogs}
        for cat in cats:
            cat1 = Products.objects.filter(category=cat)
            allproducts.append(cat1)
        hundredpaid='true'
        params = {'allproducts': allproducts,'hundredpaid':hundredpaid}
        return render(request, "index1.html",params)


def header(request):
    return render(request,"header.html")