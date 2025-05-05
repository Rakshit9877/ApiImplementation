from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Item(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, blank=True, null=True)
    unit = models.CharField(max_length=20)
    returnable = models.BooleanField(default=True)
    selling_price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    tax_rate = models.FloatField(blank=True, null=True)
    quantity_in_hand = models.IntegerField(default=0)
    quantity_to_receive = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def total_value(self):
        if self.cost_price and self.quantity_in_hand:
            return self.cost_price * self.quantity_in_hand
        return 0
    
    @property
    def profit_margin(self):
        if self.cost_price and self.selling_price and self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0

class Group(models.Model):
    TYPE_CHOICES = (
        ('goods', 'Goods'),
        ('service', 'Service'),
    )
    
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    returnable = models.BooleanField(default=False)
    unit = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name

class GroupAttribute(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attributes')
    attribute_name = models.CharField(max_length=100)
    options = models.TextField()
    
    def __str__(self):
        return f"{self.group.name} - {self.attribute_name}"
    
    @property
    def options_list(self):
        return [option.strip() for option in self.options.split(',')]

class InventoryLog(models.Model):
    ACTION_CHOICES = (
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('adjust', 'Adjust'),
        ('transfer', 'Transfer'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='inventory_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.action} {self.quantity} of {self.item.name} by {self.user.username}"
