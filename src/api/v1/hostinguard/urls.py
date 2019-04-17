from django.conf.urls import url

from api.v1.hostinguard.views import HostinGuardView

urlpatterns = [
    url(r'^hostinguard-update$', HostinGuardView.as_view(), name='hostinguard-update'),
]
