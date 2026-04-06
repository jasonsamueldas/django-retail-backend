from django.db import models
from django.contrib.auth.models import AbstractUser

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name
    
class Store(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ['product', 'store']
        
    def __str__(self):
        return f"{self.product} - {self.store}"
    
class InventoryTransaction(models.Model):
    TRANSACTION_TYPE = [
        ('sale','Sale'),
        ('restock','Restock'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    created_by = models.ForeignKey('User',on_delete=models.SET_NULL,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.product.name} - {self.quantity}"

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('manager','Manager')
    ]
    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default='manager')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.username
