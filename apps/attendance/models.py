from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os

# Choices for region, position, and status
REGION_CHOICES = (
    ('narxoz', 'Narxoz'),
    ('fiskal', 'Fiskal'),
    ('moliya', 'Moliya'),
)

POSITION_CHOICES = (
    ('director', 'Direktor'),
    ('manager', 'Menejer'),
    ('developer', 'Dasturchi'),
    ('designer', 'Dizayner'),
    ('accountant', 'Buxgalter'),
    ('hr', 'Kadrlar bo\'limi xodimi'),
    ('marketer', 'Marketolog'),
    ('operator', 'Operator'),
    ('engineer', 'Muhandis'),
    ('technician', 'Texnik xodim'),
)

STATUS_CHOICES = (
    ('active', 'Faol'),
    ('blocked', 'Faol emas'),
)

ATTENDANCE_STATUS_CHOICES = (
    ('come', 'Kelgan'),
    ('latecomers', 'Kechikkan'),
    ('not_come', 'Kelmagan'),
)

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Region(BaseModel):
    """Universitetlar yoki regionlar modeli."""
    name = models.CharField(max_length=50, unique=True, choices=REGION_CHOICES)
    label = models.CharField(max_length=100, blank=True)
    employees_count = models.PositiveIntegerField(default=0, blank=True)
    arrivals_count = models.PositiveIntegerField(default=0, blank=True)
    departures_count = models.PositiveIntegerField(default=0, blank=True)
    absentees_count = models.PositiveIntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.label or self.get_name_display()
    
    def update_counts(self):
        """Update employee and attendance counts"""
        from django.utils import timezone
        today = timezone.now().date()
        
        self.employees_count = self.employees.filter(is_active=True).count()
        self.arrivals_count = self.attendance_records.filter(
            date=today, status='come'
        ).count()
        self.absentees_count = self.attendance_records.filter(
            date=today, status='not_come'
        ).count()
        self.save(update_fields=['employees_count', 'arrivals_count', 'absentees_count'])

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ['name']

class Filial(BaseModel):
    """Filiallar modeli."""
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filials"
        ordering = ['name']

class Employee(BaseModel):
    """Xodimlar modeli. Xodimlar haqida asosiy ma'lumotlarni saqlaydi."""
    first_name = models.CharField(max_length=30, db_index=True)
    last_name = models.CharField(max_length=30, db_index=True)
    middle_name = models.CharField(max_length=30, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, blank=True)
    region = models.ForeignKey(
        Region, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees'
    )
    terminal = models.ForeignKey(
        'Terminal', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        names = [self.first_name]
        if self.middle_name:
            names.append(self.middle_name)
        names.append(self.last_name)
        return ' '.join(names)
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Generate employee ID
            last_employee = Employee.objects.filter(
                employee_id__startswith='EMP'
            ).order_by('employee_id').last()
            
            if last_employee:
                last_id = int(last_employee.employee_id[3:])
                self.employee_id = f'EMP{last_id + 1:04d}'
            else:
                self.employee_id = 'EMP0001'
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['status', 'is_active']),
        ]

class Terminal(BaseModel):
    """Terminallar modeli. IP, port va filial ma'lumotlarini saqlaydi."""
    ip_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    name = models.CharField(max_length=50, unique=True)
    port = models.PositiveIntegerField(
        default=80, 
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    region = models.ForeignKey(
        Region, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='terminals'
    )
    filial = models.ForeignKey(
        Filial, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='terminals'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=255, blank=True)
    last_ping = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def is_online(self):
        if not self.last_ping:
            return False
        return (timezone.now() - self.last_ping).seconds < 300  # 5 minutes

    class Meta:
        verbose_name = "Terminal"
        verbose_name_plural = "Terminals"
        ordering = ['name']

class Camera(BaseModel):
    """Kameralar modeli. Kamera ma'lumotlari va holatini saqlaydi."""
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    port = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(1), MaxValueValidator(65535)]
    )
    login = models.CharField(max_length=20, default='admin', blank=True)
    password = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    region = models.ForeignKey(
        Region, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cameras'
    )
    location = models.CharField(max_length=255, blank=True)
    rtsp_url = models.URLField(blank=True)
    last_ping = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def is_online(self):
        if not self.last_ping:
            return False
        return (timezone.now() - self.last_ping).seconds < 300  # 5 minutes

    class Meta:
        verbose_name = "Camera"
        verbose_name_plural = "Cameras"
        ordering = ['name']

class Admin(BaseModel):
    """Administratorlar modeli. Admin ma'lumotlari va autentifikatsiyasini saqlaydi."""
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='admins'
    )
    filial = models.ForeignKey(
        Filial, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='admins'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
        ordering = ['name']

class Image(BaseModel):
    """Xodimlarning rasmlari modeli. Yuzni tanish uchun ishlatiladi."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='images')
    camera = models.ForeignKey(
        Camera, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='images'
    )
    image = models.ImageField(upload_to='employee_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    faiss_id = models.IntegerField(null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    @property
    def get_image_url(self):
        if self.image:
            return f"{settings.MEDIA_URL}{self.image.name}"
        return None

    def __str__(self):
        return f"Image of {self.employee.full_name}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary images for this employee
        if self.is_primary:
            Image.objects.filter(employee=self.employee, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ['-uploaded_at']

class AttendanceRecord(BaseModel):
    """Davomat yozuvlari modeli. Xodimlarning kelish-ketish vaqtlarini saqlaydi."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    camera = models.ForeignKey(
        Camera, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='attendance_records'
    )
    region = models.ForeignKey(
        Region, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='attendance_records'
    )
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default='come')
    face_image = models.ImageField(upload_to='attendance_faces/', blank=True)
    distance = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    notes = models.TextField(blank=True)

    @property
    def get_face_image_url(self):
        if self.face_image:
            return f"{settings.MEDIA_URL}{self.face_image.name}"
        return None
    
    @property
    def work_duration(self):
        if self.check_in and self.check_out:
            from datetime import datetime, timedelta
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            return check_out_dt - check_in_dt
        return None

    def __str__(self):
        return f"Attendance for {self.employee.full_name} at {self.date}"

    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        ordering = ['-date', '-recorded_at']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['region', 'date']),
        ]

class UnknownFace(BaseModel):
    """Noma'lum yuzlar modeli. Tanishilmagan shaxslarning rasmlarini saqlaydi."""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='unknown_faces')
    region = models.ForeignKey(
        Region, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='unknown_faces'
    )
    face_image = models.ImageField(upload_to='unknown_faces/', blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    distance = models.FloatField(null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    linked_employee = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='unknown_faces'
    )

    @property
    def get_face_image_url(self):
        if self.face_image:
            return f"{settings.MEDIA_URL}{self.face_image.name}"
        return None

    def __str__(self):
        return f"Unknown face recorded at {self.recorded_at}"

    class Meta:
        verbose_name = "Unknown Face"
        verbose_name_plural = "Unknown Faces"
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['recorded_at', 'is_processed']),
            models.Index(fields=['camera', 'recorded_at']),
        ]
