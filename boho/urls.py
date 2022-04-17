from django.contrib import admin
from django.urls import path, include
from boho import views


urlpatterns = [
    path("", views.index, name='homepage'),
    path("productdetail/<int:id>", views.productdetailedview, name='productdetailedview'),
    path("signup", views.signup, name='signup'),
    path("signup/otpverify", views.signupotp, name='signupotp'),
    path("signup/otpverify2", views.signupotp2, name='signupotp2'),
    path("signin", views.signin, name='signin'),
    path("signin/otpverify", views.signinotp, name='signinotp'),
    path("signin/otpverify2", views.signinotp2, name='signinotp2'),
    path("cuslogout",views.customerlogout,name="customerlogout"),
    path("aboutus", views.aboutus, name='aboutus'),
    path("contact", views.contactuscustomer, name='contactuscustomer'),
    path("search", views.search, name='search'),
    path("catlogproducts", views.catlogproducts, name='catlogproducts'),
    path("cartproducts", views.cartproducts, name='cartproducts'),
    path("removefromcart",views.removefromcart,name="removefromcart"),
    path("productaddedtocatlog",views.addtocatlogs,name='productaddedtocatlogs'),
    path("checking",views.checking,name='checking'),
    path("myorders",views.myorders,name='myorders'),
    path('sellersignup',views.sellersignup,name="sellerssignup"),
    path('sellersignup/otpverify',views.sellersignupotp,name="sellerssignupotp"),
    path('sellersignup/otpverify2',views.sellersignupotp2,name="sellerssignupotp2"),
    path('sellersignin',views.sellersignin,name='sellersignin'),
    path("sellersignin/otpverify", views.sellersigninotp, name='signinotp'),
    path("sellersignin/otpverify2", views.sellersigninotp2, name='signinotp2'),
    path("sellerlogout",views.sellerlogout,name="sellerlogout"),
    path('addproductpage',views.addproduct,name="addproduct"),
    path('addingproduct',views.addproduct2,name="addproduct2"),
    path('deleteproduct',views.deleteproduct,name="deleteproduct"),
    path('testrazorpay',views.testrazorpay,name='testrazorpay'),
    path('afterpayment',views.afterpaypage,name='afterpaypage'),
    path('fullpayment',views.fullpayment,name='fullpayment'),
    path('afterfullpayment',views.afterfullpayment,name='afterfullpayment'),
    path('header',views.header,name="header")
    
]