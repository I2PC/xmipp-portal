from django.contrib import admin
from web import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Version)
admin.site.register(models.Xmipp)
admin.site.register(models.Attempt)
