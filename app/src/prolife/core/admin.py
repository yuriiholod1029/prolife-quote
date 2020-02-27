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
    CustomerAddress,
    Order,
    OrderedProduct,
)



@register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku']
    search_fields = ['name', 'sku']


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 1


@register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [
        CustomerAddressInline,
    ]

    list_display = ['id', 'name', 'phone_number']
    search_fields = ['name', 'phone_number']


# TODO: Move to forms.py
class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):

    def clean(self):
        """Check that at least one product has been entered."""
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
            for cleaned_data in self.cleaned_data):
            raise ValidationError('At least one item required.')


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    raw_id_fields = ['product']
    autocomplete_fields = ['product']
    extra = 1
    formset = AtLeastOneRequiredInlineFormSet


# TODO: Move to forms.py
class OrderForm(ModelForm):

    class Meta:
        model = Order
        exclude = ('sales_rep',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.email:
            raise ValidationError("You don't have email which is mandatory to add orders")
        else:
            return self.cleaned_data


@register(Order)
class OrderAdmin(admin.ModelAdmin):

    form = OrderForm
    inlines = [
        OrderedProductInline,
    ]
    list_display = ['id', 'status', 'get_sales_rep_email', 'get_customer_name']
    list_filter = ['status']

    search_fields = ['id',]

    autocomplete_fields = ('customer_address',)
    # raw_id_fields = ['customer_address',]

    def get_sales_rep_email(self, obj):
        return obj.sales_rep.email


    get_sales_rep_email.admin_order_field = 'sales_rep_email'  # Allows column order sorting
    get_sales_rep_email.short_description = 'Sales rep email'  # Renames column head

    def get_customer_name(self, obj):
        return obj.customer_address.customer.name

    get_customer_name.admin_order_field = 'customer'
    get_customer_name.short_description = 'Customer'

    def save_model(self, request, obj, form, change):
        pass

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def save_formset(self, request, form, formset, change):
        is_send_email = not form.instance.pk
        form.instance.sales_rep = request.user
        form.instance.save()
        formset.save()
        if is_send_email:
            self.send_order_created_email(form.instance)

    def send_order_created_email(self, order):
        ordered_products = []
        for ordered_product in OrderedProduct.objects.filter(order=order).select_related('product'):
            ordered_products.append({
                'name': ordered_product.product.name,
                'quantity': ordered_product.quantity,
                'amount': ordered_product.quantity * ordered_product.product.price
            })
        send_email.delay(
            ORDER_CREATED_EMAIL,
            settings.ORDER_CREATED_TO_EMAILS + [order.sales_rep.email],
            {
                'order_url': order.url,
                'order_id': order.id,
                'order_notes': order.notes,
                'products': ordered_products,
                'customer_address': order.customer_address.address,
            },
        )


@register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    search_fields = ['id', 'address', 'customer__name',]
    list_filter = ['customer__name']

    def get_customer_name(self, obj):
        return obj.customer.name

    get_customer_name.admin_order_field = 'customer_name'  # Allows column order sorting
    get_customer_name.short_description = 'customer_name'  # Renames column head
