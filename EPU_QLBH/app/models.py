from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES=(
    ('ML','Milk'),
    ('CZ','Cheese')
)

STATE_CHOICES=(
    ('Quân Hoàng','Hoàng Quân'),
    ('Quân Hoàng','Hoàng Quân'),
    ('Quân Hoàng','Hoàng Quân'),
    ('Quân Hoàng','Hoàng Quân'),
    ('Quân Hoàng','Hoàng Quân'),
)

class Product(models.Model):
    title = models.CharField(max_length=1000)
    selling_price = models.FloatField()
    discount_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=100)
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discount_price