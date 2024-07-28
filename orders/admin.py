import csv
import datetime

from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Order, OrderItem

# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid', 'order_payment', 'created', 'updated', 'order_detail', 'order_pdf')
    list_filter = ('paid', 'created', 'updated')
    inlines = (OrderItemInline,)
    actions = ('export_to_csv',)

    @admin.display(description='Stripe payment')
    def order_payment(self, obj: Order) -> str:
        url = obj.get_stripe_url()
        if obj.stripe_id:
            html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
            return mark_safe(s=html)
        return ''
    
    @admin.display
    def order_detail(self, obj: Order):
        url = reverse(viewname='orders:admin_order_detail', args=[obj.pk])
        return mark_safe(s=f'<a href="{url}">View</a>')
    
    @admin.display(description='Invoice')
    def order_pdf(self, obj: Order):
        url = reverse(viewname='orders:admin_order_pdf', args=[obj.pk])
        return mark_safe(s=f'<a href="{url}">PDF</a>')

    @admin.action(description='Export to CSV')
    def export_to_csv(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={self.opts.verbose_name}.csv'

        fields = [field for field in self.opts.get_fields() if not field.many_to_many and not field.one_to_many]
        
        writer = csv.writer(csvfile=response)
        writer.writerow(row=[field.verbose_name for field in fields])

        for item in queryset:
            row = list()
            for field in fields:
                value = getattr(item, field.name)
                if isinstance(value, datetime.datetime):
                    value = value.strftime('%d/%m/%Y')
                row.append(value)
            writer.writerow(row=row)
        
        return response