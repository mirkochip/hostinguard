from django.conf.urls import url

from api.v1.hostinguard.app1.views import HostinGuardView

urlpatterns = [
    url(r'^app1-hostinguard-update$', HostinGuardView.as_view(), name='app1-hostinguard-update'),
]
