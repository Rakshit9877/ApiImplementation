from django import forms
from .models import Item, Group, GroupAttribute, InventoryLog

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'sku', 'unit', 'returnable', 'selling_price', 'cost_price', 'tax_rate', 
                 'quantity_in_hand', 'quantity_to_receive', 'reorder_point']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'item-name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'id': 'item-sku'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'id': 'item-unit'}),
            'returnable': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'returnable'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'selling-price', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'cost-price', 'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'id': 'tax-rate', 'step': '0.01'}),
            'quantity_in_hand': forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity-in-hand'}),
            'quantity_to_receive': forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity-to-receive'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control', 'id': 'reorder-point'}),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['type', 'name', 'description', 'returnable', 'unit', 'manufacturer', 'brand']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select', 'id': 'type'}, choices=[('goods', 'Goods'), ('service', 'Service')]),
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'itemGroupName'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'id': 'description', 'rows': 3}),
            'returnable': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'returnable'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'id': 'unit'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'id': 'manufacturer'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'id': 'brand'}),
        }

class GroupAttributeForm(forms.ModelForm):
    class Meta:
        model = GroupAttribute
        fields = ['attribute_name', 'options']
        widgets = {
            'attribute_name': forms.TextInput(attrs={'class': 'form-control attribute-input', 'placeholder': 'Attribute Name'}),
            'options': forms.TextInput(attrs={'class': 'form-control options-input', 'placeholder': 'Options (comma separated)'}),
        }

GroupAttributeFormSet = forms.inlineformset_factory(
    Group, GroupAttribute, form=GroupAttributeForm, extra=1, can_delete=True
)

class InventoryLogForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ['item', 'action', 'quantity', 'notes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select', 'id': 'item'}),
            'action': forms.Select(attrs={'class': 'form-select', 'id': 'action'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'id': 'notes', 'rows': 3}),
        } 