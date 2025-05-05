from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee, Department, Role
from .forms import EmployeeForm, DepartmentForm, RoleForm
from django.db.models import Q

# Create your views here.

@login_required
def employee_list(request):
    departments = Department.objects.all()
    roles = Role.objects.all()
    employees = Employee.objects.all()
    
    # Apply filters
    department_id = request.GET.get('department')
    role_id = request.GET.get('role')
    search = request.GET.get('search')
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    if role_id:
        employees = employees.filter(role_id=role_id)
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'employees': employees,
        'departments': departments,
        'roles': roles,
    }
    return render(request, 'employee/employee_list.html', context)

@login_required
def employee_add(request):
    departments = Department.objects.all()
    roles = Role.objects.all()
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.created_by = request.user
            employee.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee/employee_add.html', {
        'form': form,
        'departments': departments,
        'roles': roles
    })

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all()
    roles = Role.objects.all()
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee/employee_edit.html', {
        'form': form,
        'employee': employee,
        'departments': departments,
        'roles': roles
    })

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee:employee_list')
    return redirect('employee:employee_list')

@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'employee/department_list.html', {'departments': departments})

@login_required
def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        if name and location:
            department = Department.objects.create(
                name=name,
                location=location,
                created_by=request.user
            )
            messages.success(request, 'Department added successfully!')
        else:
            messages.error(request, 'Department name and location are required!')
    return redirect('employee:department_list')

@login_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        if name and location:
            department.name = name
            department.location = location
            department.save()
            messages.success(request, 'Department updated successfully!')
        else:
            messages.error(request, 'Department name and location are required!')
    return redirect('employee:department_list')

@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        if department.employee_set.exists():
            messages.error(request, 'Cannot delete department with employees!')
        else:
            department.delete()
            messages.success(request, 'Department deleted successfully!')
    return redirect('employee:department_list')

@login_required
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'employee/role_list.html', {'roles': roles})

@login_required
def role_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            role = Role.objects.create(
                name=name,
                created_by=request.user
            )
            messages.success(request, 'Role added successfully!')
        else:
            messages.error(request, 'Role name is required!')
    return redirect('employee:role_list')

@login_required
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            role.name = name
            role.save()
            messages.success(request, 'Role updated successfully!')
        else:
            messages.error(request, 'Role name is required!')
    return redirect('employee:role_list')

@login_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        if role.employee_set.exists():
            messages.error(request, 'Cannot delete role with employees!')
        else:
            role.delete()
            messages.success(request, 'Role deleted successfully!')
    return redirect('employee:role_list')

@login_required
def employee_management(request):
    return redirect('employee:employee_list')
