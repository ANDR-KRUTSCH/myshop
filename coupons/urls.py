from django.urls import path

from . import views

app_name = 'coupons'

urlpatterns = (
    path(route='apply/', view=views.coupon_apply, name='apply'),
)