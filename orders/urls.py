from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = (
    path(route='create/', view=views.order_create, name='order_create'),
    path(route='admin/order/<int:order_pk>/pdf/', view=views.admin_order_pdf, name='admin_order_pdf'),
    path(route='admin/order/<int:order_pk>/', view=views.admin_order_detail, name='admin_order_detail'),
)