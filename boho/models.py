from django.core.validators import MinLengthValidator
from django.db import models
from pandas import notnull
from sqlalchemy import null

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class Cart(models.Model):
    no_of_cart = models.AutoField(primary_key=True)
    cust_id = models.IntegerField()
    product_id = models.CharField(max_length=10)
    qty=models.IntegerField(null=True)
    name=models.CharField( max_length=40)
    description=models.CharField( max_length=300)
    cost=models.CharField( max_length=10)
    totalcost=models.IntegerField(null=True)
    pickuplocation=models.CharField( max_length=100)
    image=models.CharField( max_length=300)
    checkingavailability=models.CharField(max_length=40)
    availability=models.CharField(max_length=40 ,null=True)
    

class Catlog(models.Model):
    no_of_catlogs = models.AutoField(primary_key=True)
    cust_id = models.IntegerField()
    product_id = models.CharField(max_length=10)
    qty=models.IntegerField(null=True)
    name=models.CharField( max_length=40)
    description=models.CharField( max_length=300)
    cost=models.CharField( max_length=10)
    pickuplocation=models.CharField( max_length=100)
    image=models.CharField( max_length=300)


class ContactUsCustomers(models.Model):
    cust_id = models.IntegerField()
    name=models.CharField(max_length=40)
    query = models.CharField(db_column='Query', max_length=400)  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TimeField(db_column='Time')  # Field name made lowercase.
    no_of_queries = models.AutoField(primary_key=True)
    mobile_no = models.CharField(db_column='mobile_no',max_length=10)


class ContactUsSellers(models.Model):
    no_of_queries = models.AutoField(primary_key=True)
    seller_id = models.IntegerField()
    name=models.CharField(max_length=40)
    query = models.CharField(max_length=400)
    date = models.DateField()
    time = models.TimeField()
    mobileno = models.CharField(max_length=10)


class CustomerDetails(models.Model):
    cust_id = models.AutoField(primary_key=True)
    cust_name = models.CharField(max_length=40)
    cust_phone_no = models.CharField(unique=True, max_length=10, validators=[MinLengthValidator(10)])
    email=models.CharField(unique=True,max_length=40)
    companyname=models.CharField(max_length=40)
    cust_role = models.CharField(db_column='Cust_role', max_length=40)  # Field name made lowercase.
    lookingfor = models.CharField(max_length=40)
    no_of_samples_viewed = models.IntegerField(db_column='No_of_samples_viewed',default='0')  # Field name made lowercase.

    def __str__(self):
        return (self.cust_name)


class Installers(models.Model):
    team_leader_id = models.AutoField(primary_key=True)
    team_leader_name = models.CharField(max_length=40)
    leaders_phone_no = models.CharField(max_length=10)
    installers_address = models.CharField(db_column='Installers_address', max_length=300)  # Field name made lowercase.
    rating = models.IntegerField()


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=10)
    productname=models.CharField(max_length=40)
    quantity = models.CharField(max_length=10)
    cust_name = models.CharField(db_column='Cust_name', max_length=40)  # Field name made lowercase.
    seller_id = models.CharField(max_length=10)
    sellers_name = models.CharField(max_length=40)
    needinstallers=models.CharField(max_length=10)
    installers_phoneno = models.CharField(max_length=10)
    installers_leader_name = models.CharField(max_length=40)
    transporter_leaders_phoneno = models.CharField(max_length=10)
    traporter_leaders_name = models.CharField(max_length=40)
    dropaddress = models.CharField(max_length=300)
    customer_phone_no = models.CharField(max_length=10)
    total_price = models.IntegerField(db_column='Total_price')  # Field name made lowercase.
    date = models.DateField()
    fifty_percent_payment=models.CharField(max_length=10)
    hundred_percent_payment=models.CharField(max_length=10)
    pickupaddress = models.CharField(max_length=300)
    image=models.CharField(max_length=300)


class Products(models.Model):
    product_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    color = models.CharField(max_length=40)
    size = models.CharField(max_length=40)
    material = models.CharField(max_length=40)
    description = models.CharField(max_length=300)
    seller_id = models.IntegerField()
    seller_phone_no = models.CharField(max_length=10)
    seller_name = models.CharField(max_length=40)
    cost = models.IntegerField()
    pickup_location = models.CharField(max_length=300)
    image=models.ImageField(upload_to="boho/images",default="")


    def __str__(self):
        return str(self.product_id)+" "+self.name


class SalesDone(models.Model):
    no_of_sales = models.AutoField(primary_key=True)
    seller_id = models.IntegerField()
    product_id = models.IntegerField()
    seller_name = models.CharField(max_length=40)
    product_name = models.CharField(max_length=40)
    qty = models.IntegerField()
    price = models.IntegerField()
    seller_phoneno = models.CharField(max_length=10)
    date = models.DateField()


    def __str__(self):
        return self.seller_name+" "+self.seller_phoneno


class SellerDetails(models.Model):
    seller_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    phoneno = models.CharField(max_length=10)
    default_pickup_address = models.CharField(db_column='default pickup address', max_length=300)  # Field renamed to remove unsuitable characters.

    def __str__(self):
        return self.name+" "+self.phoneno


class Transporters(models.Model):
    team_leader_id = models.AutoField(primary_key=True)
    team_leader_name = models.CharField(max_length=40)
    leaders_phone_no = models.CharField(max_length=10)
    address = models.CharField(max_length=300)

    def __str__(self):
        return self.team_leader_name+" "+self.leaders_phone_no


class check_availability(models.Model):
    no_of_requests=models.AutoField(primary_key=True)
    product_id = models.IntegerField()
    qty = models.IntegerField()
    availability=models.CharField(max_length=10)
    seller_id=models.CharField(max_length=40)

    
    def __str__(self):
        return "product_id is:"+str(self.product_id)+" "+"required quantity is:"+str(self.qty)+" status is:"+str(self.availability)+" Seller_id is:"+str(self.seller_id)


class sponsors(models.Model):
    no_of_sponsors=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    image=models.ImageField(upload_to="boho/sponsorimages",default="") 
    def __str__(self):
        return "Sponsor name is:"+str(self.name)


class brands(models.Model):
    id = models.IntegerField(primary_key=True)
    name=models.CharField(max_length=50)
    link =  models.CharField(default='', max_length=50)
    image=models.ImageField(upload_to="boho/brandsimages",default="")
    
    def __str__(self):
        return (self.name)


class offers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.TextField(default='')
    link =  models.CharField(default='', max_length=50)
    image = models.ImageField(upload_to="boho/offerimages",default="")
    accent_color = models.CharField(default='', max_length=30)

    def __str__(self):
        return  (self.name)