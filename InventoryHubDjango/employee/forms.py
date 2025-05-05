from django import forms
from .models import Employee, Department, Role

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'department', 'salary', 'bonus',
            'role', 'phone', 'hire_date', 'email', 'address'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'salary': forms.NumberInput(attrs={'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'step': '0.01'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'location']

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name'] 