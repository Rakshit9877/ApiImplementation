from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Case, When, F, Count, Q, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from .models import Item, Group, GroupAttribute, InventoryLog
from .forms import ItemForm, GroupForm, GroupAttributeFormSet, InventoryLogForm
from django.utils import timezone
from django.http import JsonResponse
import datetime
from flask_api.client import FlaskAPIClient

@login_required
def inventory_home(request):
    messages.info(request, "Viewing inventory management section.")
    return render(request, 'inventory/inventory.html')

@login_required
def dashboard(request):
    # Get local statistics from Django DB
    django_items = Item.objects.count()
    
    # Get data from Flask API
    flask_data = FlaskAPIClient.get_dashboard_data()
    
    if flask_data:
        # Use Flask data for dashboard
        total_items = flask_data.get('total_items', 0)
        total_inventory_value = flask_data.get('total_inventory_value', 0)
        low_stock_items = flask_data.get('low_stock_items', 0)
        out_of_stock_items = flask_data.get('out_of_stock_items', 0)
        total_groups = flask_data.get('total_groups', 0)
        goods_groups = flask_data.get('goods_groups', 0)
        service_groups = flask_data.get('service_groups', 0)
    else:
        # Fallback to Django data if Flask API fails
        # Count statistics
        total_items = Item.objects.count()
        total_inventory_value = Item.objects.aggregate(
            total=Coalesce(Sum(F('cost_price') * F('quantity_in_hand')), 0.0, output_field=FloatField())
        )['total']
        
        low_stock_items = Item.objects.filter(quantity_in_hand__lte=F('reorder_point')).count()
        out_of_stock_items = Item.objects.filter(quantity_in_hand=0).count()
        total_groups = Group.objects.count()
        goods_groups = Group.objects.filter(type='goods').count()
        service_groups = Group.objects.filter(type='service').count()
    
    # Get Flask items for top value items
    flask_items = FlaskAPIClient.get_items()
    
    # Process Flask items for display
    top_value_items = []
    if flask_items:
        for item in flask_items:
            if item.get('cost_price') and item.get('quantity_in_hand', 0) > 0:
                item['calculated_value'] = item['cost_price'] * item['quantity_in_hand']
        
        # Sort by calculated value and take top 5
        top_value_items = sorted(
            [item for item in flask_items if item.get('calculated_value')],
            key=lambda x: x['calculated_value'], 
            reverse=True
        )[:5]
    else:
        # Fallback to Django data
        top_value_items = Item.objects.filter(
            cost_price__isnull=False, 
            quantity_in_hand__gt=0
        ).annotate(
            calculated_value=ExpressionWrapper(
                F('cost_price') * F('quantity_in_hand'), 
                output_field=FloatField()
            )
        ).order_by('-calculated_value')[:5]
    
    # Calculate top margin items from Flask data
    top_margin_items = []
    if flask_items:
        for item in flask_items:
            if item.get('cost_price') and item.get('selling_price') and item.get('cost_price') > 0:
                item['calculated_margin'] = ((item['selling_price'] - item['cost_price']) * 100) / item['cost_price']
        
        # Sort by margin and take top 5
        top_margin_items = sorted(
            [item for item in flask_items if item.get('calculated_margin')],
            key=lambda x: x['calculated_margin'], 
            reverse=True
        )[:5]
    else:
        # Fallback to Django data
        top_margin_items = Item.objects.filter(
            cost_price__isnull=False,
            selling_price__isnull=False,
            cost_price__gt=0
        ).annotate(
            calculated_margin=ExpressionWrapper(
                (F('selling_price') - F('cost_price')) * 100 / F('cost_price'),
                output_field=FloatField()
            )
        ).order_by('-calculated_margin')[:5]
    
    # Get Flask groups for recent groups
    flask_groups = FlaskAPIClient.get_groups()
    
    # Process Flask groups for display
    recent_groups = []
    unit_distribution = {}
    if flask_groups:
        # Sort by created_at (newest first)
        recent_groups = sorted(
            flask_groups,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:5]
        
        # Calculate unit distribution
        for group in flask_groups:
            unit = group.get('unit', 'Unknown')
            unit_distribution[unit] = unit_distribution.get(unit, 0) + 1
        
        unit_distribution = [{'unit': unit, 'count': count} for unit, count in unit_distribution.items()]
        
        # Get groups with most attributes
        groups_with_attributes = sorted(
            flask_groups,
            key=lambda x: len(x.get('attributes', [])),
            reverse=True
        )[:5]
    else:
        # Fallback to Django data
        recent_groups = Group.objects.order_by('-created_at')[:5]
        unit_distribution = Group.objects.values('unit').annotate(count=Count('id'))
        groups_with_attributes = Group.objects.annotate(
            attribute_count=Count('attributes')
        ).order_by('-attribute_count')[:5]
    
    # Calculate returnable groups
    returnable_groups = 0
    if flask_groups:
        returnable_groups = sum(1 for group in flask_groups if group.get('returnable', False))
    else:
        returnable_groups = Group.objects.filter(returnable=True).count()
    
    # Calculate group counts for chart
    group_counts = []
    if total_groups > 0:
        group_counts.append({
            'name': 'Goods',
            'count': goods_groups,
            'percentage': (goods_groups / total_groups) * 100 if total_groups > 0 else 0
        })
        group_counts.append({
            'name': 'Services',
            'count': service_groups,
            'percentage': (service_groups / total_groups) * 100 if total_groups > 0 else 0
        })
        group_counts.append({
            'name': 'Returnable',
            'count': returnable_groups,
            'percentage': (returnable_groups / total_groups) * 100 if total_groups > 0 else 0
        })
    
    # Calculate items stored only in Django
    items_in_django_only = django_items
    
    # Placeholder growth values
    items_growth = 5.3
    value_growth = 7.8
    
    # Add counts for returnable/non-returnable items
    if flask_items:
        returnable_items = sum(1 for item in flask_items if item.get('returnable', False))
        non_returnable_items = len(flask_items) - returnable_items
    else:
        returnable_items = Item.objects.filter(returnable=True).count()
        non_returnable_items = Item.objects.filter(returnable=False).count()
    
    # Placeholder for items to receive
    items_to_receive = 0
    if flask_items:
        items_to_receive = sum(1 for item in flask_items if item.get('quantity_to_receive', 0) > 0)
    else:
        items_to_receive = Item.objects.filter(quantity_to_receive__gt=0).count()
    
    # Placeholder for high value items
    high_value_items = 0
    if flask_items:
        high_value_items = sum(1 for item in flask_items if item.get('cost_price', 0) > 1000)
    else:
        high_value_items = Item.objects.filter(cost_price__gt=1000).count()
    
    # Calculate average item value
    avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
    
    return render(
        request, 
        'inventory/dashboard.html',
        {
            'total_items': total_items,
            'total_inventory_value': total_inventory_value,
            'avg_item_value': avg_item_value,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'items_to_receive': items_to_receive,
            'high_value_items': high_value_items,
            'returnable_items': returnable_items,
            'non_returnable_items': non_returnable_items,
            'top_value_items': top_value_items,
            'top_margin_items': top_margin_items,
            'total_groups': total_groups,
            'goods_groups': goods_groups,
            'service_groups': service_groups,
            'returnable_groups': returnable_groups,
            'recent_groups': recent_groups,
            'unit_distribution': unit_distribution,
            'groups_with_attributes': groups_with_attributes,
            'group_counts': group_counts,
            'items_growth': items_growth,
            'value_growth': value_growth,
            'current_date': datetime.datetime.now(),
            'items_in_django_only': items_in_django_only,
        }
    )

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            # Save to Django DB
            item = form.save()
            
            # Log the item creation in Django
            InventoryLog.objects.create(
                item=item,
                user=request.user,
                action='add',
                quantity=item.quantity_in_hand,
                notes=f"Initial creation with {item.quantity_in_hand} units"
            )
            
            # Also save to Flask API
            flask_item_data = {
                'name': item.name,
                'sku': item.sku,
                'unit': item.unit,
                'returnable': item.returnable,
                'selling_price': item.selling_price,
                'cost_price': item.cost_price,
                'tax_rate': item.tax_rate,
                'quantity_in_hand': item.quantity_in_hand,
                'quantity_to_receive': item.quantity_to_receive,
                'reorder_point': item.reorder_point
            }
            
            # Call Flask API to create item
            flask_response = FlaskAPIClient.create_item(flask_item_data)
            
            if 'error' in flask_response:
                messages.warning(request, f"Item saved to Django DB but failed to sync with Flask: {flask_response['error']}")
            else:
                messages.success(request, f"Item '{item.name}' has been added successfully to both databases!")
            
            return redirect('inventory:dashboard')
    else:
        form = ItemForm()
    
    return render(request, 'inventory/item_form.html', {'form': form})

@login_required
def item_list(request):
    # Get items from Flask API
    flask_items = FlaskAPIClient.get_items()
    
    if flask_items:
        # Use Flask data
        items = flask_items
        total_items = len(items)
        total_value = sum(item.get('selling_price', 0) for item in items if item.get('selling_price'))
    else:
        # Fallback to Django data
        items = Item.objects.all()
        total_items = items.count()
        total_value = items.filter(selling_price__isnull=False).aggregate(
            total=Coalesce(Sum('selling_price'), 0.0, output_field=FloatField())
        )['total']
    
    item_types = {
        "Goods": total_items
    }
    
    messages.info(request, f"Viewing list of {total_items} items. Data from Flask API.")
    return render(
        request,
        'inventory/item_list.html',
        {
            'items': items,
            'total_items': total_items,
            'total_value': total_value,
            'item_types': item_types,
            'from_flask_api': bool(flask_items),
        }
    )

@login_required
def delete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        is_django = True
    except Item.DoesNotExist:
        flask_item = FlaskAPIClient.get_item(item_id)
        if not flask_item:
            return render(request, 'inventory/not_found.html', {'type': 'item'})
        is_django = False
    if request.method == 'POST':
        if is_django:
            item_name = item.name
            item.delete()
            flask_response = FlaskAPIClient.delete_item(item_id)
            if 'error' in flask_response:
                messages.warning(request, f"Item deleted from Django DB but failed to delete from Flask: {flask_response['error']}")
            else:
                messages.success(request, f"Item '{item_name}' deleted from both databases.")
        else:
            flask_response = FlaskAPIClient.delete_item(item_id)
            if 'error' in flask_response:
                messages.warning(request, f"Failed to delete item from Flask: {flask_response['error']}")
            else:
                messages.success(request, f"Item deleted from Flask API.")
        return redirect('inventory:item_list')
    return render(request, 'inventory/confirm_delete.html', {'item': item if is_django else None, 'flask_item': flask_item if not is_django else None})

@login_required
def update_item(request, item_id):
    # Try Django DB first
    try:
        item = Item.objects.get(id=item_id)
        is_django = True
    except Item.DoesNotExist:
        flask_item = FlaskAPIClient.get_item(item_id)
        if not flask_item:
            return render(request, 'inventory/not_found.html', {'type': 'item'})
        form = ItemForm(initial=flask_item)
        is_django = False
    else:
        form = ItemForm(instance=item)
    
    if request.method == 'POST':
        if is_django:
            form = ItemForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                FlaskAPIClient.update_item(item_id, form.cleaned_data)
                messages.success(request, f"Item '{item.name}' updated in Django and Flask.")
                return redirect('inventory:item_list')
        else:
            form = ItemForm(request.POST)
            if form.is_valid():
                FlaskAPIClient.update_item(item_id, form.cleaned_data)
                messages.success(request, f"Item updated in Flask API.")
                return redirect('inventory:item_list')
    return render(request, 'inventory/item_form.html', {'form': form, 'item': item if is_django else None})

@login_required
def group_list(request):
    type_filter = request.GET.get('typeFilter')
    returnable_filter = request.GET.get('returnableFilter')
    sort_by = request.GET.get('sortBy', 'created_at')
    sort_order = request.GET.get('sortOrder', 'desc')
    
    # Get groups from Flask API
    flask_groups = FlaskAPIClient.get_groups()
    
    if flask_groups:
        # Filter groups based on request parameters
        filtered_groups = flask_groups
        
        # Apply type filter
        if type_filter:
            filtered_groups = [group for group in filtered_groups if group.get('type') == type_filter]
        
        # Apply returnable filter
        if returnable_filter:
            returnable_value = returnable_filter.lower() == 'true'
            filtered_groups = [group for group in filtered_groups if group.get('returnable') == returnable_value]
        
        # Sort groups
        if sort_by == 'name':
            filtered_groups = sorted(
                filtered_groups, 
                key=lambda x: x.get('name', ''),
                reverse=(sort_order == 'desc')
            )
        else:  # sort by created_at
            filtered_groups = sorted(
                filtered_groups, 
                key=lambda x: x.get('created_at', ''),
                reverse=(sort_order == 'desc')
            )
        
        groups = filtered_groups
        total_groups = len(flask_groups)
        goods_groups = sum(1 for g in flask_groups if g.get('type') == 'goods')
        service_groups = sum(1 for g in flask_groups if g.get('type') == 'service')
        returnable_groups = sum(1 for g in flask_groups if g.get('returnable', False))
    else:
        # Fallback to Django data
        groups_query = Group.objects.all()
        
        if type_filter:
            groups_query = groups_query.filter(type=type_filter)
        
        if returnable_filter:
            returnable_value = returnable_filter.lower() == 'true'
            groups_query = groups_query.filter(returnable=returnable_value)
        
        if sort_by == 'name':
            order_column = 'name'
        else:
            order_column = 'created_at'
        
        if sort_order == 'desc':
            groups_query = groups_query.order_by(f'-{order_column}')
        else:
            groups_query = groups_query.order_by(order_column)
        
        groups = groups_query.all()
        total_groups = Group.objects.count()
        goods_groups = Group.objects.filter(type='goods').count()
        service_groups = Group.objects.filter(type='service').count()
        returnable_groups = Group.objects.filter(returnable=True).count()
    
    context = {
        'groups': groups,
        'total_groups': total_groups,
        'goods_groups': goods_groups,
        'service_groups': service_groups,
        'returnable_groups': returnable_groups,
        'type_filter': type_filter,
        'returnable_filter': returnable_filter,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'from_flask_api': bool(flask_groups),
    }
    
    return render(request, 'inventory/group_list.html', context)

@login_required
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        formset = GroupAttributeFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Save to Django DB
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            # Process attributes for Django
            attributes = []
            for attribute_form in formset:
                if attribute_form.cleaned_data and not attribute_form.cleaned_data.get('DELETE', False):
                    attribute = attribute_form.save(commit=False)
                    attribute.group = group
                    attribute.save()
                    attributes.append({
                        'attribute_name': attribute.attribute_name,
                        'options': attribute.options
                    })
            
            # Also save to Flask API
            flask_group_data = {
                'type': group.type,
                'name': group.name,
                'description': group.description,
                'returnable': group.returnable,
                'unit': group.unit,
                'manufacturer': group.manufacturer,
                'brand': group.brand,
                'created_by': request.user.id,
                'attributes': attributes
            }
            
            # Call Flask API to create group
            flask_response = FlaskAPIClient.create_group(flask_group_data)
            
            if 'error' in flask_response:
                messages.warning(request, f"Group saved to Django DB but failed to sync with Flask: {flask_response['error']}")
            else:
                messages.success(request, f"Group '{group.name}' has been added successfully to both databases!")
            
            return redirect('inventory:group_list')
    else:
        form = GroupForm()
        formset = GroupAttributeFormSet()
    
    return render(request, 'inventory/group_form.html', {'form': form, 'formset': formset})

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        formset = GroupAttributeFormSet(request.POST, instance=group)
        
        if form.is_valid() and formset.is_valid():
            # Save to Django DB
            form.save()
            formset.save()
            
            # Process attributes for Flask API
            attributes = []
            for attribute in group.attributes.all():
                attributes.append({
                    'attribute_name': attribute.attribute_name,
                    'options': attribute.options
                })
            
            # Also update in Flask API
            flask_group_data = {
                'type': group.type,
                'name': group.name,
                'description': group.description,
                'returnable': group.returnable,
                'unit': group.unit,
                'manufacturer': group.manufacturer,
                'brand': group.brand,
                'attributes': attributes
            }
            
            # Call Flask API to update group
            flask_response = FlaskAPIClient.update_group(group_id, flask_group_data)
            
            if 'error' in flask_response:
                messages.warning(request, f"Group updated in Django DB but failed to update in Flask: {flask_response['error']}")
            else:
                messages.success(request, f"Group '{group.name}' has been updated successfully in both databases!")
            
            return redirect('inventory:group_list')
    else:
        form = GroupForm(instance=group)
        formset = GroupAttributeFormSet(instance=group)
    
    return render(request, 'inventory/group_form.html', {'form': form, 'formset': formset, 'group': group})

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        group_name = group.name
        
        # Delete from Django DB
        group.delete()
        
        # Also delete from Flask API
        flask_response = FlaskAPIClient.delete_group(group_id)
        
        if 'error' in flask_response:
            messages.warning(request, f"Group deleted from Django DB but failed to delete from Flask: {flask_response['error']}")
        else:
            messages.success(request, f"Group '{group_name}' has been deleted successfully from both databases.")
        
        return redirect('inventory:group_list')
    
    return render(request, 'inventory/confirm_delete_group.html', {'group': group})

@login_required
def group_attributes_api(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    attributes = group.attributes.all()
    
    # Convert attributes to list of dictionaries
    attributes_data = [
        {
            'id': attr.id,
            'name': attr.name,
            'value': attr.value,
        }
        for attr in attributes
    ]
    
    return JsonResponse(attributes_data, safe=False)

def about(request):
    page_title = "About InventoryHub"
    page_content = """
    InventoryHub is a comprehensive inventory management system designed to help businesses 
    track their inventory, manage items and categories, and monitor inventory movements.
    """
    
    return render(request, 'about.html', {
        'page_title': page_title,
        'page_content': page_content
    })
