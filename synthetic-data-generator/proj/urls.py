from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import hello.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", hello.views.index, name="index"),
    path("v1/devices/<str:uuid>/status/", hello.views.tester),
    path("v1/devices/all/", hello.views.all_data),
    path("v1/devices/ground_truth/", hello.views.get_truth),
    path("v1/devices/", hello.views.get_devices),
    path("v1/locations/", hello.views.get_locations),
    path("admin/", admin.site.urls),
]
