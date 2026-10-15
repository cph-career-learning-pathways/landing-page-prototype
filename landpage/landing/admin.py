from django.contrib import admin
from .models import (
    Category,
    CuratedCollection,
    Filter,
    PriceModel,
    Resource,
    Source,
    User,
)

# Register your models here.
admin.site.register(User)
admin.site.register(Source)
admin.site.register(PriceModel)
admin.site.register(Category)
admin.site.register(Filter)
admin.site.register(Resource)
admin.site.register(CuratedCollection)