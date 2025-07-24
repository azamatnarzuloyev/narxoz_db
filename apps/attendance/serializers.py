from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import (
    Region, Filial, Employee, Terminal, Camera, Admin, Image,
    AttendanceRecord, UnknownFace, REGION_CHOICES, POSITION_CHOICES,
    STATUS_CHOICES, ATTENDANCE_STATUS_CHOICES, PositionApi
)



class RegionSerializer(serializers.ModelSerializer):
    employees_count = serializers.SerializerMethodField()
    arrivals_count = serializers.SerializerMethodField()
    latecomers_count = serializers.SerializerMethodField()
    absentees_count = serializers.SerializerMethodField()
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Region
        fields = [
            'id', 'name', 'name_display', 'label', 'employees_count', 
            'arrivals_count', 'latecomers_count', 'absentees_count',
            'is_active', 'created_at', 'updated_at'
        ]

    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()

    def get_arrivals_count(self, obj):
        today = timezone.now().date()
        return obj.attendance_records.filter(date=today, status='come').count()

    def get_latecomers_count(self, obj):
        today = timezone.now().date()
        return obj.attendance_records.filter(date=today, status='latecomers').count()

    def get_absentees_count(self, obj):
        today = timezone.now().date()
        return obj.attendance_records.filter(date=today, status='not_come').count()

class FilialSerializer(serializers.ModelSerializer):
    terminals_count = serializers.SerializerMethodField()

    class Meta:
        model = Filial
        fields = ['id', 'name', 'value', 'address', 'is_active', 'terminals_count', 'created_at', 'universitet']

    def get_terminals_count(self, obj):
        return obj.terminals.filter(status='active').count()

class EmployeeListSerializer(serializers.ModelSerializer):
    """Simplified serializer for employee list view"""
    region_name = serializers.CharField(source='region.name', read_only=True)
    terminal_name = serializers.CharField(source='terminal.name', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    image = serializers.ImageField(source='images.first.image', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name','positions', 'image',
            'position', 'position_display', 'region_name', 'terminal_name', 'phone_number',
            'status', 'status_display', 'is_active', 'created_at'
        ]

class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for employee detail view"""
    region = RegionSerializer(read_only=True)
    terminal = serializers.StringRelatedField(read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    images_count = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()

    # Write fields
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    terminal_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'region_id','first_name', 'last_name', 'middle_name', 'full_name','positions',
            'position', 'position_display', 'region', 'region_id', 'terminal', 'terminal_id',
            'status', 'status_display', 'phone_number', 'email', 'hire_date',
            'is_active', 'images_count', 'attendance_count', 'created_at', 'updated_at'
        ]

    def get_images_count(self, obj):
        return obj.images.count()

    def get_attendance_count(self, obj):
        return obj.attendance_records.count()

    def validate_region_id(self, value):
        if value and not Region.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid region ID")
        return value

    def validate_terminal_id(self, value):
        if value and not Terminal.objects.filter(id=value, status='active').exists():
            raise serializers.ValidationError("Invalid terminal ID")
        return value

class TerminalSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.label', read_only=True)
    filial_name = serializers.CharField(source='filial.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    employees_count = serializers.SerializerMethodField()

    # Write fields
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    filial_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Terminal
        fields = [
            'id', 'ip_address', 'name', 'port', 'region_name', 'region_id',
            'filial_name', 'filial_id', 'status', 'status_display', 'location',
            'employees_count', 'is_online', 'last_ping', 'created_at'
        ]

    def get_employees_count(self, obj):
        return obj.employees.filter(is_active=True).count()

class CameraSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.label', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Write fields
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Camera
        fields = [
            'id', 'name', 'ip_address', 'port', 'login', 'password',
            'status', 'status_display', 'region_name', 'region_id',
            'location', 'rtsp_url', 'is_online', 'last_ping', 'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

class AdminSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.label', read_only=True)
    filial_name = serializers.CharField(source='filial.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Write fields
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    filial_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Admin
        fields = [
            'id', 'name', 'login', 'password', 'region_name', 'region_id',
            'filial_name', 'filial_id', 'status', 'status_display',
            'last_login', 'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        return make_password(value)

class ImageSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    image_url = serializers.SerializerMethodField()

    # Write fields
    employee_id = serializers.IntegerField(write_only=True)
    camera_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Image
        fields = [
            'id', 'employee_name', 'employee_id', 'camera_name', 'camera_id',
            'image', 'image_url', 'uploaded_at', 'faiss_id', 'is_primary'
        ]

    def get_image_url(self, obj):
        return obj.get_image_url

class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True)
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    region_name = serializers.CharField(source='region.label', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    face_image_url = serializers.SerializerMethodField()
    work_duration = serializers.SerializerMethodField()

    # Write fields
    employee_id = serializers.IntegerField(write_only=True)
    camera_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee_name', 'employee_id', 'employee_id_display',
            'camera_name', 'camera_id', 'region_name', 'region_id',
            'check_in', 'check_out', 'date', 'status', 'status_display',
            'face_image', 'face_image_url', 'distance', 'work_duration',
            'notes', 'recorded_at'
        ]

    def get_face_image_url(self, obj):
        return obj.get_face_image_url

    def get_work_duration(self, obj):
        duration = obj.work_duration
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return None

class UnknownFaceSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    linked_employee_name = serializers.CharField(source='linked_employee.full_name', read_only=True)
    face_image_url = serializers.SerializerMethodField()

    # Write fields
    camera_id = serializers.IntegerField(write_only=True)
    region_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = UnknownFace
        fields = [
            'id', 'camera_name', 'camera_id', 'region_name', 'region_id',
            'face_image', 'face_image_url', 'recorded_at', 'distance',
            'is_processed', 'linked_employee_name', 'linked_employee'
        ]

    def get_face_image_url(self, obj):
        return obj.get_face_image_url

class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    region = serializers.CharField()
    total_employees = serializers.IntegerField()
    arrivals = serializers.IntegerField()
    latecomers = serializers.IntegerField()
    absentees = serializers.IntegerField()
    attendance_rate = serializers.FloatField()

class UnknownFaceLinkSerializer(serializers.Serializer):
    """Serializer for linking unknown face to employee"""
    unknown_face_id = serializers.IntegerField()
    employee_id = serializers.IntegerField()

    def validate_unknown_face_id(self, value):
        if not UnknownFace.objects.filter(id=value, is_processed=False).exists():
            raise serializers.ValidationError("Invalid or already processed unknown face ID")
        return value

    def validate_employee_id(self, value):
        if not Employee.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid employee ID")
        return value

class FaceRecognitionResultSerializer(serializers.Serializer):
    """Serializer for face recognition API results"""
    status = serializers.CharField()
    employee_id = serializers.IntegerField()
    cosine_similarity = serializers.FloatField()
    saved_file = serializers.CharField()
    message = serializers.CharField(required=False)


class PositionApiSerializer(serializers.ModelSerializer):
    """Serializer for Position API"""
    class Meta:
        model = PositionApi
        fields = ['id', 'label', 'value']
        read_only_fields = ['id']

    def validate_label(self, label):
        if not label:
            raise serializers.ValidationError("Position name cannot be empty")
        return label

    def validate_value(self, value):
        if not value:
            raise serializers.ValidationError("Position value cannot be empty")
        return value

