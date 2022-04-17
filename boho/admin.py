from django.contrib import admin
from .models import Cart,Catlog,ContactUsCustomers,ContactUsSellers,CustomerDetails,SalesDone,SellerDetails,Installers,sponsors,Transporters,Orders,Products,check_availability
# Register your models here.

admin.site.register(Cart)
admin.site.register(Catlog)
admin.site.register(ContactUsCustomers)
admin.site.register(ContactUsSellers)
admin.site.register(CustomerDetails)
admin.site.register(SalesDone)
admin.site.register(SellerDetails)
admin.site.register(Installers)
admin.site.register(Transporters)
admin.site.register(Orders)
admin.site.register(Products)
admin.site.register(check_availability)
admin.site.register(sponsors)