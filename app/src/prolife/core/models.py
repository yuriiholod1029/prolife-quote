from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.conf import settings
from django.urls import reverse
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, ExpressionWrapper, F, DecimalField

class Product(models.Model):
    name = models.CharField(max_length=256, unique=True)
    sku = models.CharField(max_length=256, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.name} (sku: {self.sku}) {self.price}'

    class Meta:
        ordering = ['name']


class Customer(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=256)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{8,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=16)  # validators should be a list
    mobile = models.CharField(validators=[phone_regex], max_length=16, null=True, blank=True)
    city = models.CharField(max_length=256)
    county = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    postcode = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.name}, {self.address}, {self.city}, {self.county} ({self.postcode})'


class Order(models.Model):
    PROCESSING = 'processing'
    AWAITING_CUSTOMER_RESPONSE = 'awaiting'
    DISPATCHED = 'dispatched'

    STATUS_CHOICES = (
        (PROCESSING, 'Processing'),
        (AWAITING_CUSTOMER_RESPONSE, 'Awaiting customer response'),
        (DISPATCHED, 'Dispatched'),
    )

    sales_rep = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, default=PROCESSING, choices=STATUS_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderedProduct')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        return settings.BASE_URL + reverse(
            'admin:%s_%s_change' % (
                self._meta.app_label,
                self._meta.model_name),
            args=[self.id],
        )

    def __str__(self):
        return f'{self.customer.name} - {self.status}'

    @classmethod
    def get_dispatched_order_queryset_in_year_by_month(cls, year):
        return cls.objects.prefetch_related('orderedproduct').filter(
            created_at__year=year,
            status=cls.DISPATCHED,
        ).annotate(
            month=ExtractMonth('created_at'),
        ).values(
            'month',
        ).annotate(
            amount=Sum(
                ExpressionWrapper(
                    F('orderedproduct__quantity') * F('orderedproduct__product__price'),
                    output_field=DecimalField()
                )
            ),
        )

    @classmethod
    def get_dispatched_order_in_year_by_customers(cls, year):
        qs = cls.get_dispatched_order_queryset_in_year_by_month(year)
        return qs.values_list('month', 'amount', 'customer__name').order_by(
            'customer__email',
            'month'
        )

    @classmethod
    def get_dispatched_order_in_year_by_sales_rep(cls, year):
        qs = cls.get_dispatched_order_queryset_in_year_by_month(year)
        return qs.values_list('month', 'amount', 'sales_rep__email').order_by(
            'sales_rep__email',
            'month'
        )


class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['product', 'order']

    def __str__(self):
        return f'Product: {self.product.name}, Order: {self.order.id}'
