from django.http import JsonResponse
from django.shortcuts import redirect, render
from sqlalchemy import false, true
from twilio.rest import Client
import random as r
# from .models import Cart, Catlog, ContactUsCustomers, ContactUsSellers, CustomerDetails, SalesDone, SellerDetails, Installers, Transporters, Orders, Products, check_availability, Offers
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
import re
import os
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from datetime import date
from website.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY,BASE_DIR
import razorpay
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib import colors
from django.contrib.auth.decorators import login_required
# Create your views here.

def test(request):
    context = { "Status" : "200", "Response" : "OK from test"}
    return JsonResponse(context)

# This will fetch all the products from the table and show to the user
def index(request):
    allproducts = []
    Offers = []
    top_brands = []
    top_categories = []
    resp = {"offers" : Offers, "top_brands" : top_brands, "top_categories": top_categories, "top_products": allproducts }
    catblogs = Products.objects.values('category', 'product_id')
    cats = {post['category'] for post in catblogs}

    for cat in cats:
        cat1 = Products.objects.filter(category=cat).values()
        allproducts.append(cat1[0])


    offer_details = offers.objects.all().values()
    for temp in offer_details:
        Offers.append(temp)

    brand = brands.objects.all().values()
    for temp in brand:
        top_brands.append(temp)

    category = Products.objects.values_list("category", flat=True)
    for temp in category:
        top_categories.append(temp)

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
@csrf_exempt
def productdetails(request):
    print (request.POST.get('id'))
    try :
        product=Products.objects.filter(product_id = request.POST.get("id")).values()
        resp={'product':product[0]}
    except:
        resp = {'status' : "404", 'Error' : 'Product not found'}
    return JsonResponse(resp)


def SendOTP(request):
    context = {"Status" : "200"}
    if request.user.is_authenticated:
        context["IsUserAuthenticated"] = True
    if request.method == 'POST' :
        MobileNumber = request.POST.get('MobileNumber')
        client = Client("ACd91fd2c97943ea0815f5acf1acca3c5e", "d757a5d65582d49ffe8e76fcd9ae6c67")
        try:
            otp = str(r.randint(1000, 9999))
            request.session['OTP'] = otp
            request.session['MobileNumber'] = MobileNumber
            client.messages.create(to=["+91"+MobileNumber], from_="+19803755068", body=otp)
            context["Response"] = "OTP SENT"
            context["ExistingUser"] = False
            registered_nos = CustomerDetails.objects.all().values_list('cust_phone_no')
            list_of_nos = ()
            for i in registered_nos :
                list_of_nos += i
            if MobileNumber in list_of_nos :
                context['ExistingUser'] = True

        except Exception as e:
            context["Status"] = "500"
            context["Response"] = "Inernal Server Error"
            # raise(e)
    else :
        context["Status"] = "400"
        context["Response"] = "Bad Request"
    
    return JsonResponse(context)


def ValidateOTP(request):
    context = {"Status" : "200"}
    if request.user.is_authenticated:
        context["IsUserAuthenticated"] = True

    if request.method == 'POST' :
        otp = request.session.get("OTP")
        EnteredOTP = request.POST.get("otp")
        if otp == EnteredOTP :
            context['IsUserAuthenticated'] = True
        else:
            context['IsUserAuthenticated'] = False
    else :
        context["Status"] = "400"
        context["Response"] = "Bad Request"

    return JsonResponse(context)
    

def GetCostumerDetails(request):
    context = { "Status" : "200"}
    if request.method == 'POST':
        try:
            cust_name = request.POST.get('name')
            phoneno = request.session.get('MobileNumber')
            email=request.POST.get('email')
            role = request.POST.get('role')
            lookingfor = request.POST.get('lookingfor')
            companyname=request.POST.get('companyname')
            user = User.objects.create_user(
                    username=phoneno, password=phoneno, email=email, first_name=cust_name, last_name=cust_name)
            user.save()
            Customer_Details = CustomerDetails(
                    cust_name=cust_name, cust_phone_no=phoneno, cust_role=role, lookingfor=lookingfor,email=email,companyname=companyname)
            Customer_Details.save()
            context["Response" : "User Created"]
        except:
            context["Status"] = "500"
            context["Response"] = "Internal Server Error"
    else :
        context["Status"] = "400"
        context["Response"] = "Bad Request"

    return JsonResponse(context)


def Logout(request):
    context = { "Status" : "200"}
    if request.user.is_authenticated:
            logout(request)
            context["Response" : "OK"]
            return JsonResponse(context)
    else:
        logout(request)
        return JsonResponse(context)


def accountDetails(request):
    details = []
    resp = {"status" : "OK", "details" : details}
    if request.user.is_authenticated:
        user = CustomerDetails.objects.filter(cust_name = request.user).values()
        for temp in user:
            details.append(temp)
        return (JsonResponse(resp))
    
    else :
        resp["error"] = "Unauthenticated User"
        return (JsonResponse(resp))

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
        search=request.POST.get("searchQuery")
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
        return JsonResponse(context)

        # return render(request, "search.html",context)

# This will fetch the user phoneno and after that it will fetch product data from cart which has the phonenumber of the requested user
def cartproducts(request):
    if request.user.is_authenticated:
        username = request.user
        cart_items = []
        custid=CustomerDetails.objects.get(cust_phone_no=username)
        custid2=custid.cust_id
        catblogs = Cart.objects.values('cust_id')
        cat1=""
        cats = {ords['cust_id'] for ords in catblogs}
        for cat in cats:
            cat1 = list(Cart.objects.filter(cust_id=custid2).values())
            cart_items.append(cat1)
        if cart_items==['']:
            resp={'status' : '200' , 'response' : "No Products Found"}
        else:
            resp = {'status' : '200' , 'cart_items': cart_items}
        return JsonResponse(resp)
        # return render(request, "cart.html",context)
    else:
        respn = {}
        respn['status'] = '401'
        respn['response'] = 'Unauthenticated User'
        return (JsonResponse(respn))



# This will fetch the user phoneno and after that it will fetch product data from catlog which has the phonenumber of the requested user
def catlogproducts(request):
    if request.user.is_authenticated:
        username = request.user
        cart_items = []
        custid=CustomerDetails.objects.get(cust_phone_no=username)
        custid2=custid.cust_id
        catblogs = Catlog.objects.values('cust_id')
        cat1=""
        cats = {ords['cust_id'] for ords in catblogs}
        for cat in cats:
            cat1 = Catlog.objects.filter(cust_id=custid2)
        cart_items.append(cat1)
        noproducts="no"
        if cart_items==['']:
            context={'noproducts':noproducts}
        else:
            context = {'cart_items':cart_items}
        return JsonResponse(context)

        # return render(request, "catlog-page.html",context)
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
def addToCart(request):
    respn = {}
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
            respn['status'] = '200'
            respn['response'] = 'added to cart'
            return (JsonResponse(respn))
        else:
            respn['status'] = '401'
            respn['response'] = 'Unauthenticated User'
            return (JsonResponse(respn))
    else:
        respn['status'] = '500'
        respn['response'] = 'Internal Server Error'
        return (JsonResponse(respn))

# This will fetch the user phoneno and after that it will fetch product data from orders which has the phonenumber of the requested user
def myorders(request):
    if request.user.is_authenticated:
        username = request.user
        cart_items = []
        catblogs = Orders.objects.values('customer_phone_no')
        cat1=""
        cats = {ords['customer_phone_no'] for ords in catblogs}
        for cat in cats:
            cat1 = Orders.objects.filter(customer_phone_no=username)
        cart_items.append(cat1)
        noproducts="no"
        if cart_items==[''] :
            context={'noproducts':noproducts}
        else:
            context = {'cart_items':cart_items}
        return JsonResponse(context)

        # return render(request, "order-page.html", context)
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
    context = {'Status' : ' ' }
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
        context={ 'Staus': 'OK' , 'account_created' : accounted_created}
        # return render(request,"sellersignup2.html",context)
        return JsonResponse(context)

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
            context = {'Status' : 'OK' ,'otp': otp, 'cust_no': phoneno}
            # return render(request, "sellersigninotp.html", context)
            return JsonResponse(context)
        else:
            invalid = "invalid"
            context = {'Status' : 'OK' , 'invalid': invalid}
            # return render(request, "sellerlogin.html", context)
            return JsonResponse(context)

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
                addedproducts= list(Products.objects.filter(seller_phone_no=cust_no).values())
                context = {'Status':'OK', 'loggedin': loggedin,'sellerdetails':Seller_details,"addedproducts":addedproducts}
                # return render(request, "seller1.html", context)
                return JsonResponse(context)
    else:
        wrongotp="true"
        context={'Status':'OK' ,"wrongotp" : wrongotp}
        # return render(request, "sellersigninotp.html",context)
        return JsonResponse(context)

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
                'Status' : 'OK',
                'productadded':productadded
            }
            # return render(request, "seller-addproduct.html",context)
            return JsonResponse(context)
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
            addedproducts= list(Products.objects.filter(seller_phone_no=username).values())
            Seller_details = list(SellerDetails.objects.filter(
                    phoneno=username).values())
            context = {'status':'OK', 'sellerdetails':Seller_details, "addedproducts":addedproducts}
            # return render(request, "seller1.html",context)
            return JsonResponse(context)
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
    respon = {"Status" : "OK"}
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
            cat1 = list(Products.objects.filter(category=cat).values())
            allproducts.append(cat1)
        hundredpaid='true'
        respon = {'status': 'ok', 'allproducts': allproducts,'hundredpaid':hundredpaid}
        # return render(request, "index1.html",params)
    return JsonResponse(respon)

        
# def newArrivals(request):
#     new = []
#     resp = {"status" : "200" , "new" : new }
@login_required
def timepass(request):
    return (JsonResponse({"test" : "hello"}))