from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.conf import settings
from django.urls import reverse


class Product(models.Model):
    name = models.CharField(max_length=256, unique=True)
    sku = models.CharField(max_length=256, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.name} (sku: {self.sku})'

    class Meta:
        ordering = ['name']

class Customer(models.Model):
    name = models.CharField(max_length=256, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{8,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=16, blank=True)  # validators should be a list

    def __str__(self):
        return self.name


class CustomerAddress(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_address', on_delete=models.CASCADE)
    address = models.TextField()

    def __str__(self):
        return f'{self.customer.name}@{self.address}'

    class Meta:
        ordering = ['customer__name']


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
    customer_address = models.ForeignKey(CustomerAddress, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderedProduct')

    @property
    def url(self):
        return settings.BASE_URL + reverse(
            'admin:%s_%s_change' % (
                self._meta.app_label,
                self._meta.model_name),
            args=[self.id],
        )

    def __str__(self):
        return f'{self.customer_address.customer.name} - {self.status}'

class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['product', 'order']

    def __str__(self):
        return f'Product: {self.product.name}, Order: {self.order.id}'
