from django.conf.urls import url

from api.v1.health.views import HealthView

urlpatterns = [
    url(r'^health$', HealthView.as_view(), name='health'),
]
