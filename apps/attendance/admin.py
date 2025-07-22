from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Region, Filial, Employee, Terminal, Camera, Admin, 
    Image, AttendanceRecord, UnknownFace
)

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'employees_count', 'is_active', 'created_at']
    list_filter = ['name', 'is_active', 'created_at']
    search_fields = ['name', 'label']
    readonly_fields = ['employees_count', 'arrivals_count', 'departures_count', 'absentees_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('employees')

@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'value']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'full_name', 'position', 'region', 
        'status', 'is_active', 'created_at'
    ]
    list_filter = ['position', 'status', 'region', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    readonly_fields = ['employee_id', 'full_name']
    raw_id_fields = ['region', 'terminal']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'first_name', 'middle_name', 'last_name', 'full_name')
        }),
        ('Work Information', {
            'fields': ('position', 'region', 'terminal', 'hire_date')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('region', 'terminal')

@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'port', 'region', 'filial', 'status', 'is_online']
    list_filter = ['status', 'region', 'filial', 'created_at']
    search_fields = ['name', 'ip_address', 'location']
    raw_id_fields = ['region', 'filial']
    
    def is_online(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">●</span> Online')
        return format_html('<span style="color: red;">●</span> Offline')
    is_online.short_description = 'Status'

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'port', 'region', 'status', 'is_online', 'created_at']
    list_filter = ['status', 'region', 'created_at']
    search_fields = ['name', 'ip_address', 'location']
    raw_id_fields = ['region']
    
    def is_online(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">●</span> Online')
        return format_html('<span style="color: red;">●</span> Offline')
    is_online.short_description = 'Status'

@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'login', 'region', 'filial', 'status', 'last_login']
    list_filter = ['status', 'region', 'filial', 'created_at']
    search_fields = ['name', 'login']
    raw_id_fields = ['region', 'filial']

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0
    readonly_fields = ['image_preview', 'uploaded_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['employee', 'camera', 'image_preview', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at', 'camera']
    search_fields = ['employee__first_name', 'employee__last_name']
    raw_id_fields = ['employee', 'camera']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'date', 'check_in', 'check_out', 
        'status', 'camera', 'region', 'recorded_at'
    ]
    list_filter = ['status', 'date', 'region', 'camera', 'recorded_at']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    raw_id_fields = ['employee', 'camera', 'region']
    date_hierarchy = 'date'
    readonly_fields = ['face_image_preview', 'work_duration']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'date', 'status')
        }),
        ('Time Information', {
            'fields': ('check_in', 'check_out', 'work_duration')
        }),
        ('Location Information', {
            'fields': ('camera', 'region')
        }),
        ('Face Recognition', {
            'fields': ('face_image', 'face_image_preview', 'distance')
        }),
        ('Additional Information', {
            'fields': ('notes', 'recorded_at')
        }),
    )
    
    def face_image_preview(self, obj):
        if obj.face_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.face_image.url
            )
        return "No image"
    face_image_preview.short_description = 'Face Image'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'camera', 'region')

@admin.register(UnknownFace)
class UnknownFaceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'camera', 'region', 'face_image_preview', 
        'is_processed', 'linked_employee', 'recorded_at'
    ]
    list_filter = ['is_processed', 'camera', 'region', 'recorded_at']
    raw_id_fields = ['camera', 'region', 'linked_employee']
    readonly_fields = ['face_image_preview']
    date_hierarchy = 'recorded_at'
    
    actions = ['mark_as_processed']
    
    def face_image_preview(self, obj):
        if obj.face_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.face_image.url
            )
        return "No image"
    face_image_preview.short_description = 'Face'
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f'{updated} unknown faces marked as processed.')
    mark_as_processed.short_description = 'Mark selected faces as processed'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('camera', 'region', 'linked_employee')

# Customize admin site
admin.site.site_header = "Attendance System Administration"
admin.site.site_title = "Attendance Admin"
admin.site.index_title = "Welcome to Attendance System Administration"
