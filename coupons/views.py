from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Coupon
from .forms import CouponApplyForm

# Create your views here.
@require_POST
def coupon_apply(request: HttpRequest) -> HttpResponseRedirect:
    now = timezone.now()
    form = CouponApplyForm(data=request.POST)
    if form.is_valid():
        code: str = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            request.session['coupon_pk'] = coupon.pk
        except Coupon.DoesNotExist:
            request.session['coupon_pk'] = None
    return redirect(to='cart:cart_detail')