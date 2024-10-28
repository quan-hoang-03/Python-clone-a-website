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

STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'), 
    ('Cancel', 'Cancel'),
    ('Pending', 'Pending'),
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
    saving_amount = models.FloatField()
    discount_percentage = models.FloatField()
    def __str__(self):
        return self.title
    @property
    def saving_amount(self):
        return self.selling_price - self.discount_price if self.selling_price > self.discount_price else 0
    @property
    def discount_percentage(self):
        if self.selling_price > 0: 
            return round((self.saving_amount / self.selling_price) * 100, 2)
        return 0
    
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
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    vnpay_order_id = models.CharField(max_length=100, blank=True, null=True) 
    vnpay_payment_status = models.CharField(max_length=100, blank=True, null=True) 
    vnpay_payment_id = models.CharField(max_length=100, blank=True, null=True)  
    paid = models.BooleanField(default=False) 

class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    payment = models.ForeignKey(Payment,on_delete=models.CASCADE)
    @property
    def total_cost(self):
        return self.quantity * self.product.discount_price
    
class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)