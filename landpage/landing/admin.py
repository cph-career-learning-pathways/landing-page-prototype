from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Source)
admin.site.register(PriceModel)
admin.site.register(Category)
admin.site.register(Filter)
admin.site.register(Resource)
admin.site.register(CuratedCollection)
admin.site.register(ResourceCategory)
admin.site.register(ResourceFilter)
admin.site.register(CollectionResource)