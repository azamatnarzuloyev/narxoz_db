import django_filters
from django.db import models
from .models import (
    Employee, Region, Terminal, Camera, Admin, Image,
    AttendanceRecord, UnknownFace, Filial
)

class EmployeeFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    employee_id = django_filters.CharFilter(lookup_expr='icontains')
    position = django_filters.ChoiceFilter(choices=Employee._meta.get_field('position').choices)
    status = django_filters.ChoiceFilter(choices=Employee._meta.get_field('status').choices)
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.filter(is_active=True))
    terminal = django_filters.ModelChoiceFilter(queryset=Terminal.objects.filter(status='active'))
    is_active = django_filters.BooleanFilter()
    hire_date_from = django_filters.DateFilter(field_name='hire_date', lookup_expr='gte')
    hire_date_to = django_filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'employee_id', 'position', 'status',
            'region', 'terminal', 'is_active'
        ]

class RegionFilter(django_filters.FilterSet):
    name = django_filters.ChoiceFilter(choices=Region._meta.get_field('name').choices)
    label = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Region
        fields = ['name', 'label', 'is_active']

class TerminalFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Terminal._meta.get_field('status').choices)
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.filter(is_active=True))
    filial = django_filters.ModelChoiceFilter(queryset=Filial.objects.filter(is_active=True))
    location = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Terminal
        fields = ['name', 'ip_address', 'status', 'region', 'filial', 'location']

class CameraFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    ip_address = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Camera._meta.get_field('status').choices)
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.filter(is_active=True))
    location = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Camera
        fields = ['name', 'ip_address', 'status', 'region', 'location']

class AdminFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    login = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Admin._meta.get_field('status').choices)
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.filter(is_active=True))
    filial = django_filters.ModelChoiceFilter(queryset=Filial.objects.filter(is_active=True))

    class Meta:
        model = Admin
        fields = ['name', 'login', 'status', 'region', 'filial']

class ImageFilter(django_filters.FilterSet):
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.filter(is_active=True))
    camera = django_filters.ModelChoiceFilter(queryset=Camera.objects.filter(status='active'))
    is_primary = django_filters.BooleanFilter()
    uploaded_from = django_filters.DateTimeFilter(field_name='uploaded_at', lookup_expr='gte')
    uploaded_to = django_filters.DateTimeFilter(field_name='uploaded_at', lookup_expr='lte')

    class Meta:
        model = Image
        fields = ['employee', 'camera', 'is_primary']

class AttendanceRecordFilter(django_filters.FilterSet):
    employee = django_filters.ModelChoiceFilter(queryset=Employee.objects.filter(is_active=True))
    camera = django_filters.ModelChoiceFilter(queryset=Camera.objects.filter(status='active'))
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.filter(is_active=True))
    status = django_filters.ChoiceFilter(choices=AttendanceRecord._meta.get_field('status').choices)
    date = django_filters.DateFilter()
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    recorded_from = django_filters.DateTimeFilter(field_name='recorded_at', lookup_expr='gte')
    recorded_to = django_filters.DateTimeFilter(field_name='recorded_at', lookup_expr='lte')

    class Meta:
        model = AttendanceRecord
        fields = ['employee', 'camera', 'region', 'status', 'date']

class UnknownFaceFilter(django_filters.FilterSet):
    camera = django_filters.ModelChoiceFilter(queryset=Camera.objects.filter(status='active'))
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.filter(is_active=True))
    is_processed = django_filters.BooleanFilter()
    recorded_from = django_filters.DateTimeFilter(field_name='recorded_at', lookup_expr='gte')
    recorded_to = django_filters.DateTimeFilter(field_name='recorded_at', lookup_expr='lte')

    class Meta:
        model = UnknownFace
        fields = ['camera', 'region', 'is_processed']

class FilialFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    value = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Filial
        fields = ['name', 'value', 'is_active']




# # filters.py (optional - for advanced filtering)
# import django_filters
# from django_filters import rest_framework as filters
# from .models import Employee, AttendanceRecord, UnknownFace

# class EmployeeFilter(filters.FilterSet):
#     name = filters.CharFilter(method='filter_by_name')
#     hire_date_from = filters.DateFilter(field_name='hire_date', lookup_expr='gte')
#     hire_date_to = filters.DateFilter(field_name='hire_date', lookup_expr='lte')
    
#     class Meta:
#         model = Employee
#         fields = {
#             'region': ['exact'],
#             'position': ['exact', 'in'],
#             'status': ['exact'],
#             'is_active': ['exact'],
#         }
    
#     def filter_by_name(self, queryset, name, value):
#         return queryset.filter(
#             models.Q(first_name__icontains=value) |
#             models.Q(last_name__icontains=value) |
#             models.Q(middle_name__icontains=value)
#         )

# class AttendanceRecordFilter(filters.FilterSet):
#     date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
#     date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
#     check_in_from = filters.TimeFilter(field_name='check_in', lookup_expr='gte')
#     check_in_to = filters.TimeFilter(field_name='check_in', lookup_expr='lte')
    
#     class Meta:
#         model = AttendanceRecord
#         fields = {
#             'employee': ['exact'],
#             'region': ['exact'],
#             'camera': ['exact'],
#             'status': ['exact', 'in'],
#             'date': ['exact', 'gte', 'lte'],
#         }

# class UnknownFaceFilter(filters.FilterSet):
#     recorded_from = filters.DateTimeFilter(field_name='recorded_at', lookup_expr='gte')
#     recorded_to = filters.DateTimeFilter(field_name='recorded_at', lookup_expr='lte')
    
#     class Meta:
#         model = UnknownFace
#         fields = {
#             'camera': ['exact'],
#             'region': ['exact'],
#             'is_processed': ['exact'],
#             'linked_employee': ['exact', 'isnull'],
#         }



