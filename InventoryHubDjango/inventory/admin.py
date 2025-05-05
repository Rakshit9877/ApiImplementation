from django.contrib import admin
from .models import Item, Group, GroupAttribute, InventoryLog

class GroupAttributeInline(admin.TabularInline):
    model = GroupAttribute
    extra = 1

class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupAttributeInline]
    list_display = ('name', 'type', 'unit', 'returnable', 'created_at')
    list_filter = ('type', 'returnable')
    search_fields = ('name', 'description')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit', 'selling_price', 'cost_price', 'quantity_in_hand', 'returnable')
    list_filter = ('returnable', 'unit')
    search_fields = ('name', 'sku')

class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'user', 'action', 'quantity', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('item__name', 'user__username', 'notes')

admin.site.register(Item, ItemAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupAttribute)
admin.site.register(InventoryLog, InventoryLogAdmin)
