from django.contrib import admin

# Register your models here.
import models
#admin.site.register(models.AccessPoint)
#admin.site.register(models.Group)
admin.site.register(models.Router)
admin.site.register(models.RouterGroup)
admin.site.register(models.Configuration)
admin.site.register(models.ApiQuery)
admin.site.register(models.CommandItem)
admin.site.register(models.NetworkProfile)