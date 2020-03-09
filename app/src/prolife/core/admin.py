from decimal import Decimal

from django.contrib import admin
from django.contrib.admin import register
from django.forms import ModelForm, ValidationError
from django.forms.models import BaseInlineFormSet
from django.conf import settings

from prolife.core.tasks import send_email
from prolife.core.email_service import ORDER_CREATED_EMAIL

from prolife.core.models import (
    Product,
    Customer,
    Order,
    OrderedProduct,
)


class CustomModelAdmin(admin.ModelAdmin):
    exclude_list_display = []

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name not in self.exclude_list_display]
        super(CustomModelAdmin, self).__init__(model, admin_site)


@register(Product)
class ProductAdmin(CustomModelAdmin):
    exclude_list_display = ['id']
    search_fields = ['name', 'sku']


@register(Customer)
class CustomerAdmin(CustomModelAdmin):
    search_fields = ['name', 'phone_number', 'email']


# TODO: Move to forms.py
class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):

    def clean(self):
        """Check that at least one product has been entered."""
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False) for cleaned_data in self.cleaned_data):
            raise ValidationError('At least one item required.')


class OrderedProductInline(admin.TabularInline):
    template = 'admin/ordered_product_tabular.html'
    model = OrderedProduct
    raw_id_fields = ['product']
    autocomplete_fields = ['product']
    extra = 0
    formset = AtLeastOneRequiredInlineFormSet


# TODO: Move to forms.py
class OrderForm(ModelForm):

    class Meta:
        model = Order
        exclude = ('sales_rep',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.instance.pk is None and not self.request.user.email:
            raise ValidationError("You don't have email which is mandatory to add orders")
        else:
            self.cleaned_data['sales_rep'] = self.request.user
            return self.cleaned_data


@register(Order)
class OrderAdmin(admin.ModelAdmin):

    form = OrderForm
    inlines = [OrderedProductInline]
    list_display = ['id', 'status', 'get_sales_rep_email', 'customer']
    list_filter = ['status']

    search_fields = ['id', 'customer__email']

    autocomplete_fields = ('customer',)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('status',)
        return self.readonly_fields

    def get_sales_rep_email(self, obj):
        return obj.sales_rep.email

    get_sales_rep_email.admin_order_field = 'sales_rep_email'  # Allows column order sorting
    get_sales_rep_email.short_description = 'Sales rep email'  # Renames column head

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sales_rep=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.sales_rep = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def response_add(self, request, obj, post_url_continue=None):
        self.send_order_created_email(obj)
        return super().response_add(request, obj)

    def send_order_created_email(self, order):
        ordered_products = []
        total_amount = Decimal('0.00')
        for ordered_product in OrderedProduct.objects.filter(order=order).select_related('product'):
            amount = ordered_product.quantity * ordered_product.product.price
            ordered_products.append({
                'name': ordered_product.product.name,
                'quantity': ordered_product.quantity,
                'amount': amount,
            })
            total_amount += amount
        customer = order.customer
        send_email.delay(
            ORDER_CREATED_EMAIL,
            settings.ORDER_CREATED_TO_EMAILS + [order.sales_rep.email],
            settings.ORDER_CREATED_CC_EMAILS,
            {
                'order_url': order.url,
                'order_id': order.id,
                'order_notes': order.notes,
                'products': ordered_products,
                'customer_address': f'{customer.address}, {customer.city}, {customer.county}, {customer.postcode}',
                'customer_phone': customer.phone_number,
                'customer_mobile': customer.mobile,
                'customer_email': customer.email,
                'total_amount': f'£{total_amount} (EX VAT)',
                'sales_rep_id': order.sales_rep.get_full_name(),
            },
        )

    class Media:
        js = ('js/order.js',
            # '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',  # jquery
        )
