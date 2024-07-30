"""
URL configuration for myshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from payment import webhooks

urlpatterns = i18n_patterns(
    path(route='admin/', view=admin.site.urls),
    path(route='cart/', view=include(arg='cart.urls', namespace='cart')),
    path(route='orders/', view=include(arg='orders.urls', namespace='orders')),
    path(route='payment/', view=include(arg='payment.urls', namespace='payment')),
    path(route='coupons/', view=include(arg='coupons.urls', namespace='coupons')),
    path(route='rosetta/', view=include(arg='rosetta.urls')),
    path(route='', view=include(arg='shop.urls', namespace='shop')),
)

urlpatterns.insert(1, path(route='payment/webhook/', view=webhooks.stripe_webhook, name='stripe-webhook'))

if settings.DEBUG:
    urlpatterns += static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)