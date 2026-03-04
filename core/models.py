from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Income(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    source=models.CharField(max_length=100)
    date=models.DateField()
    createdAt=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}--{self.amount}"
    
class Expense(models.Model):
    CATEGORY_CHOICES=[
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Bills', 'Bills'), 
        ('Other', 'Other'),
    ]
    
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    category=models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    description=models.TextField(null=True, blank=True)
    date=models.DateField()
    createdAt=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}--{self.category}--{self.amount}"
    
class Budget(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    monthlyLimit=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}--{self.monthlyLimit}"

    




