from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import AttendanceRecord, Employee, Region

@receiver(post_save, sender=AttendanceRecord)
def update_region_counts_on_save(sender, instance, created, **kwargs):
    """Update region counts when attendance record is saved"""
    if instance.region:
        instance.region.update_counts()

@receiver(post_delete, sender=AttendanceRecord)
def update_region_counts_on_delete(sender, instance, **kwargs):
    """Update region counts when attendance record is deleted"""
    if instance.region:
        instance.region.update_counts()

@receiver(post_save, sender=Employee)
def update_region_employee_count(sender, instance, created, **kwargs):
    """Update region employee count when employee is saved"""
    if instance.region:
        instance.region.update_counts()

@receiver(post_delete, sender=Employee)
def update_region_employee_count_on_delete(sender, instance, **kwargs):
    """Update region employee count when employee is deleted"""
    if instance.region:
        instance.region.update_counts()
