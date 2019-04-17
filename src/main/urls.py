from django.conf.urls import include, url

urlpatterns = [
    url(r'', include('api.v1.hostinguard.urls')),
]
