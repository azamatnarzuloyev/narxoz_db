from django.urls import path
from . import views

urlpatterns = [
    # Employee URLs
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),

    path('positions/', views.PositionApiView.as_view(), name='position-list'),
    path('positions/<int:pk>/', views.PositionApiView.as_view(), name='position-list'),
    
    # Region URLs
    path('regions/', views.RegionListCreateView.as_view(), name='region-list'),
    path('regions/<int:pk>/', views.RegionDetailView.as_view(), name='region-detail'),
    
    # Terminal URLs
    path('terminals/', views.TerminalListCreateView.as_view(), name='terminal-list'),
    path('terminals/<int:pk>/', views.TerminalDetailView.as_view(), name='terminal-detail'),
    
    # Camera URLs
    path('cameras/', views.CameraListCreateView.as_view(), name='camera-list'),
    path('cameras/<int:pk>/', views.CameraDetailView.as_view(), name='camera-detail'),
    
    # Attendance Record URLs
    path('attendance/', views.AttendanceRecordListCreateView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', views.AttendanceRecordDetailView.as_view(), name='attendance-detail'),
    
    # Admin URLs
    path('admins/', views.AdminListCreateView.as_view(), name='admin-list'),
    path('admins/<int:pk>/', views.AdminDetailView.as_view(), name='admin-detail'),
    
    # Image URLs
    path('images/', views.ImageListCreateView.as_view(), name='image-list'),
    path('images/<int:pk>/', views.ImageDetailView.as_view(), name='image-detail'),
    
    # Unknown Face URLs
    path('unknown-faces/', views.UnknownFaceListView.as_view(), name='unknown-face-list'),
    path('unknown-faces/<int:pk>/', views.UnknownFaceDetailView.as_view(), name='unknown-face-detail'),
    
    # Filial URLs
    path('filials/', views.FilialListCreateView.as_view(), name='filial-list'),
    path('filials/<int:pk>/', views.FilialDetailView.as_view(), name='filial-detail'),
    
    # Face Recognition API
    path('face-result/', views.FaceResultView.as_view(), name='face-result'),
    
    # Statistics and Reports
    path('stats/attendance/', views.attendance_stats, name='attendance-stats'),
    path('dashboard/', views.dashboard_data, name='dashboard-data'),
    path('link-unknown-face/', views.link_unknown_face, name='link-unknown-face'),
    path('employee-camera-stats/', views.EmployeeCameraStatsView.as_view(), name='employee-camera-stats'),
    path('employee-camera-stats/<str:pk>/', views.EmployeeCameraStatsDetailView.as_view(), name='employee-camera-stats'),
]

