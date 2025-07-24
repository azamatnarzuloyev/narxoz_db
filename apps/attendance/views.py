from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import os
import logging

from .models import (
    Employee, Region, Terminal, Camera, AttendanceRecord, 
    Admin, Image, UnknownFace, Filial , PositionApi , EmployeeCameraStats
)
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer, RegionSerializer, 
    TerminalSerializer, CameraSerializer, AttendanceRecordSerializer, 
    AdminSerializer, ImageSerializer, UnknownFaceSerializer, 
    FilialSerializer, AttendanceStatsSerializer, UnknownFaceLinkSerializer,
    FaceRecognitionResultSerializer , PositionApiSerializer
)
from .filters import (
    EmployeeFilter, RegionFilter, TerminalFilter, CameraFilter,
    AttendanceRecordFilter, AdminFilter, ImageFilter, UnknownFaceFilter,
    FilialFilter 
)
from datetime import datetime
from rest_framework.authentication import TokenAuthentication

logger = logging.getLogger(__name__)
site_url = 'http://127.0.0.1:8000'


class PositionApiView(APIView):
    def get(self, request):
        """
        Get all available positions.
        """
        positions = PositionApi.objects.all()
        data = [{'id': pos.pk, 'label': pos.label , 'value':pos.value} for pos in positions]
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        Create a new position.
        """
        serializer = PositionApiSerializer(data=request.data)
        if serializer.is_valid():
            position = serializer.save()
            return Response({'id': position.pk, 'label': position.label, 'value': position.value}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        """
        Update an existing position.
        """
        try:
            position = PositionApi.objects.get(pk=pk)
        except PositionApi.DoesNotExist:
            return Response({'error': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PositionApiSerializer(position, data=request.data, partial=True)
        if serializer.is_valid():
            position = serializer.save()
            return Response({'id': position.pk, 'label': position.label, 'value': position.value}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete a position.
        """
        try:
            position = PositionApi.objects.get(pk=pk)
            position.delete()
            data = {'message': 'Position deleted successfully', "status":200}
            return Response(data , status=status.HTTP_200_OK) 
        except PositionApi.DoesNotExist:
            return Response({'error': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)

# Employee Views
class EmployeeListCreateView(ListCreateAPIView):
    """
    List all employees or create a new employee.
    """
    queryset = Employee.objects.select_related('region', 'terminal').filter(is_active=True)
    filterset_class = EmployeeFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    ordering_fields = ['first_name', 'last_name', 'created_at', 'employee_id']
    ordering = ['first_name', 'last_name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmployeeListSerializer
        return EmployeeDetailSerializer

    @extend_schema(
        summary="List employees",
        description="Get a paginated list of employees with filtering and search capabilities",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Search in name, employee_id, email"),
            OpenApiParameter("position", OpenApiTypes.STR, description="Filter by position"),
            OpenApiParameter("region", OpenApiTypes.INT, description="Filter by region ID"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filter by status"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create employee",
        description="Create a new employee record"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class EmployeeDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an employee.
    """
    queryset = Employee.objects.select_related('region', 'terminal')
    serializer_class = EmployeeDetailSerializer

    @extend_schema(summary="Get employee details")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="Update employee")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(summary="Partially update employee")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(summary="Delete employee")
    def delete(self, request, *args, **kwargs):
        # Soft delete
        employee = self.get_object()
        employee.is_active = False
        employee.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Region Views
class RegionListCreateView(ListCreateAPIView):
    """
    List all regions or create a new region.
    """
    queryset = Region.objects.filter(is_active=True)
    serializer_class = RegionSerializer
    filterset_class = RegionFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'label']
    ordering = ['name']

class RegionDetailView(APIView):
    def get(self, request, pk):
        """
        Retrieve a region by ID.
        """
        try:
            region = Region.objects.get(pk=pk)
            serializer = RegionSerializer(region)
            return Response(serializer.data)
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)

class RegionDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

# Terminal Views
class TerminalListCreateView(ListCreateAPIView):
    """
    List all terminals or create a new terminal.
    """
    queryset = Terminal.objects.select_related('region', 'filial').filter(status='active')
    serializer_class = TerminalSerializer
    filterset_class = TerminalFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'ip_address', 'location']
    ordering = ['name']

class TerminalDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a terminal.
    """
    queryset = Terminal.objects.select_related('region', 'filial')
    serializer_class = TerminalSerializer

# Camera Views
class CameraListCreateView(ListCreateAPIView):
    """
    List all cameras or create a new camera.
    """
    queryset = Camera.objects.select_related('region').filter(status='active')
    serializer_class = CameraSerializer
    filterset_class = CameraFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'ip_address', 'location']
    ordering = ['name']

class CameraDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a camera.
    """
    queryset = Camera.objects.select_related('region')
    serializer_class = CameraSerializer

# Attendance Record Views
class AttendanceRecordListCreateView(ListCreateAPIView):
    """
    List all attendance records or create a new record.
    """
    queryset = AttendanceRecord.objects.select_related('employee', 'camera', 'region')
    serializer_class = AttendanceRecordSerializer
    filterset_class = AttendanceRecordFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-date', '-recorded_at']

class AttendanceRecordDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an attendance record.
    """
    queryset = AttendanceRecord.objects.select_related('employee', 'camera', 'region')
    serializer_class = AttendanceRecordSerializer

# Admin Views
class AdminListCreateView(ListCreateAPIView):
    """
    List all admins or create a new admin.
    """
    queryset = Admin.objects.select_related('region', 'filial').filter(status='active')
    serializer_class = AdminSerializer
    filterset_class = AdminFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'login']
    ordering = ['name']

class AdminDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an admin.
    """
    queryset = Admin.objects.select_related('region', 'filial')
    serializer_class = AdminSerializer

# Image Views
class ImageListCreateView(ListCreateAPIView):
    """
    List all employee images or upload a new image.
    """
    queryset = Image.objects.select_related('employee', 'camera')
    serializer_class = ImageSerializer
    filterset_class = ImageFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-uploaded_at']

class ImageDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an employee image.
    """
    queryset = Image.objects.select_related('employee', 'camera')
    serializer_class = ImageSerializer

# Unknown Face Views
class UnknownFaceListView(ListCreateAPIView):
    """
    List all unknown faces.
    """
    queryset = UnknownFace.objects.select_related('camera', 'region', 'linked_employee')
    serializer_class = UnknownFaceSerializer
    filterset_class = UnknownFaceFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ['-recorded_at']

class UnknownFaceDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an unknown face record.
    """
    queryset = UnknownFace.objects.select_related('camera', 'region', 'linked_employee')
    serializer_class = UnknownFaceSerializer

# Filial Views
class FilialListCreateView(ListCreateAPIView):
    """
    List all filials or create a new filial.
    """
    queryset = Filial.objects.filter(is_active=True)
    serializer_class = FilialSerializer
    filterset_class = FilialFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'value']
    ordering = ['name']

class FilialDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a filial.
    """
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer



# # Face Recognition API
# class FaceResultView(APIView):
#     """
#     Handle face recognition results from cameras.
#     """
#     parser_classes = (MultiPartParser, FormParser)

#     @extend_schema(
#         summary="Process face recognition result",
#         description="Handle face data from client. If 'user' == 'unrecognized', save to UnknownFace model. Otherwise, 'user' should be an integer (employee_id) -> save to AttendanceRecord.",
#         request={
#             'multipart/form-data': {
#                 'type': 'object',
#                 'properties': {
#                     'file': {'type': 'string', 'format': 'binary'},
#                     'user': {'type': 'string', 'description': 'Employee ID or "unrecognized"'},
#                     'cosine_similarity': {'type': 'number'},
#                     'camera_ip': {'type': 'string', 'description': 'Camera IP address'},
#                 }
#             }
#         },
#         responses={200: FaceRecognitionResultSerializer}
#     )
#     def post(self, request, format=None):
#         """
#         Handle face data from client.
#         If 'user' == 'unrecognized', save to UnknownFace model.
#         Otherwise, 'user' should be an integer (employee_id) -> save to AttendanceRecord.
#         """
#         try:
#             # Extract data from request
#             face_file = request.FILES.get('file')
#             cosine_similarity = request.data.get('cosine_similarity')
#             user_value = request.data.get('user')
#             camera_ip = request.data.get('camera_ip', "192.168.1.64")

#             # Basic validation
#             if not face_file:
#                 return Response(
#                     {"error": "Missing file (use 'file' in multipart form-data)."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             if not (cosine_similarity and user_value):
#                 return Response(
#                     {"error": "Missing required fields (user, cosine_similarity)."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Attempt to fetch camera
#             try:
#                 # camera_obj = Camera.objects.get(ip_address=camera_ip, status='active')
#                 camera_obj = Camera.objects.first()
#             except Camera.DoesNotExist:
#                 logger.warning(f"Camera with IP {camera_ip} not found")
#                 return Response(
#                     {"error": "Camera not found."}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # Create the face_results directory if not exists
#             save_dir = os.path.join(settings.MEDIA_ROOT, "face_results")
#             os.makedirs(save_dir, exist_ok=True)
#             file_path = os.path.join(save_dir, face_file.name)

#             # Save file to disk
#             try:
#                 with open(file_path, "wb") as f:
#                     for chunk in face_file.chunks():
#                         f.write(chunk)
#             except Exception as e:
#                 logger.error(f"Could not save file: {e}")
#                 return Response(
#                     {"error": f"Could not save file: {e}"}, 
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )

#             # Handle "unrecognized" user
#             if user_value == "unrecognized":
#                 try:
#                     unknown_face = UnknownFace.objects.create(
#                         face_image=face_file,
#                         distance=cosine_similarity,
#                         camera=camera_obj,
#                         region=camera_obj.region
#                     )
#                     logger.info(f"Unknown face recorded: {unknown_face.id}")
                    
#                     return Response({
#                         "status": "ok",
#                         "employee_id": 0,
#                         "cosine_similarity": cosine_similarity,
#                         "saved_file": file_path,
#                         "message": "Unknown face recorded successfully"
#                     }, status=status.HTTP_200_OK)
                    
#                 except Exception as e:
#                     logger.error(f"Error creating unknown face record: {e}")
#                     return Response(
#                         {"error": str(e)}, 
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                     )

#             # Handle "recognized" user (employee)
#             else:
#                 try:
#                     employee_id = int(user_value)
#                 except ValueError:
#                     return Response(
#                         {"error": "'user' must be an integer or 'unrecognized'."},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 try:
#                     employee = Employee.objects.get(id=employee_id, is_active=True)
#                 except Employee.DoesNotExist:
#                     return Response(
#                         {"error": "Employee not found."}, 
#                         status=status.HTTP_404_NOT_FOUND
#                     )

#                 try:
#                     today = timezone.now().date()
#                     current_time = timezone.now().time()
                    
#                     # Get or create attendance record for today
#                     attendance_record, created = AttendanceRecord.objects.get_or_create(
#                         employee=employee,
#                         date=today,
#                         defaults={
#                             'camera': camera_obj,
#                             'region': camera_obj.region,
#                             'check_in': current_time,
#                             'face_image': face_file,
#                             'distance': cosine_similarity,
#                             'status': 'come'
#                         }
#                     )
                    
#                     if not created:
#                         # Update check_out time if already exists
#                         attendance_record.check_out = current_time
#                         attendance_record.face_image = face_file
#                         attendance_record.distance = cosine_similarity
#                         attendance_record.save()
                    
#                     logger.info(f"Attendance recorded for employee {employee_id}")
                    
#                     return Response({
#                         "status": "ok",
#                         "employee_id": employee_id,
#                         "cosine_similarity": cosine_similarity,
#                         "saved_file": file_path,
#                         "message": "Attendance recorded successfully"
#                     }, status=status.HTTP_200_OK)
                    
#                 except Exception as e:
#                     logger.error(f"Error creating attendance record: {e}")
#                     return Response(
#                         {"error": str(e)}, 
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                     )

#         except Exception as e:
#             logger.error(f"Unexpected error in face recognition: {e}")
#             return Response(
#                 {"error": "Internal server error"}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )



class FaceResultView(APIView):
    """
    Handle face recognition results from cameras.
    """
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Process face recognition result",
        description="Handle face data from client. If 'user' == 'unrecognized', save to UnknownFace model. Otherwise, 'user' should be an integer (employee_id) -> save to AttendanceRecord and EmployeeCameraStats.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'user': {'type': 'string', 'description': 'Employee ID or "unrecognized"'},
                    'cosine_similarity': {'type': 'number'},
                    'camera_ip': {'type': 'string', 'description': 'Camera IP address'},
                    'timestamp': {'type': 'string', 'description': 'Timestamp in ISO format (optional)'}
                }
            }
        },
        responses={200: FaceRecognitionResultSerializer}
    )
    def post(self, request, format=None):
        """
        Handle face data from client and save to appropriate model.
        """
        try:
            # Extract data from request
            face_file = request.FILES.get('file')
            cosine_similarity = request.data.get('cosine_similarity')
            user_value = request.data.get('user')
            camera_ip = request.data.get('camera_ip', "192.168.1.64")
            timestamp_str = request.data.get('timestamp', None)

            # Validate inputs
            if not face_file or not cosine_similarity or not user_value:
                return Response(
                    {"error": "Missing required fields (file, user, cosine_similarity)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # try:
            #     cosine_similarity = cosine_similarity)
            # except (ValueError, TypeError):
            #     return Response(
            #         {"error": "cosine_similarity must be a number."},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # Parse timestamp if provided, else use current time
            timestamp = timezone.now()
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    return Response(
                        {"error": "Invalid timestamp format. Use ISO format (e.g., 2025-07-23T15:30:00)."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Fetch camera by IP
            try:
                # camera_obj = Camera.objects.get(ip_address=camera_ip, status='active')
                camera_obj = Camera.objects.first()
            except Camera.DoesNotExist:
                logger.warning(f"Camera with IP {camera_ip} not found")
                return Response(
                    {"error": "Camera not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Common response data
            response_data = {
                "status": "ok",
                "cosine_similarity": cosine_similarity,
                "saved_file": f"face_results/stats/{face_file.name}",
            }

            # Handle "unrecognized" user
            if user_value == "unrecognized":
                try:
                    unknown_face = UnknownFace.objects.create(
                        face_image=face_file,
                        distance=cosine_similarity,
                        camera=camera_obj,
                        region=camera_obj.region
                    )
                    logger.info(f"Unknown face recorded: {unknown_face.id}")
                    response_data.update({
                        "employee_id": 0,
                        "message": "Unknown face recorded successfully"
                    })
                    return Response(response_data, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Error creating unknown face record: {e}")
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Handle recognized user (employee)
            try:
                employee_id = int(user_value)
                employee = Employee.objects.get(id=employee_id, is_active=True)
            except ValueError:
                return Response(
                    {"error": "'user' must be an integer or 'unrecognized'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Employee not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                today = timezone.now().date()
                current_time = timezone.now().time()

                # Get or create attendance record for today
                attendance_record, created = AttendanceRecord.objects.get_or_create(
                    employee=employee,
                    date=today,
                    defaults={
                        'camera': camera_obj,
                        'region': camera_obj.region,
                        'check_in': current_time,
                        'face_image': face_file,
                        'distance': cosine_similarity,
                        'status': 'come'
                    }
                )

                if not created:
                    attendance_record.check_out = current_time
                    attendance_record.face_image = face_file
                    attendance_record.distance = cosine_similarity
                    attendance_record.save()

                # Create EmployeeCameraStats entry
                EmployeeCameraStats.objects.create(
                    employee=employee,
                    camera=camera_obj,
                    timestamp=timestamp,
                    face_image=face_file,
                    distance=cosine_similarity
                )

                logger.info(f"Attendance and stats recorded for employee {employee_id}")
                response_data.update({
                    "employee_id": employee_id,
                    "message": "Attendance and stats recorded successfully"
                })
                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Error creating attendance record: {e}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Unexpected error in face recognition: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class EmployeeCameraStatsView(APIView):
    """
    Retrieve statistics of face captures per employee per camera, with daily filtering.
    """
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get employee face capture statistics",
        description="Returns face captures for each employee per camera, filterable by date.",
        parameters=[
            {
                'name': 'date',
                'in': 'query',
                'description': 'Filter by date (YYYY-MM-DD)',
                'required': False,
                'type': 'string'
            }
        ],
        responses={
            200: {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'employee_id': {'type': 'integer'},
                        'employee_name': {'type': 'string'},
                        'camera_ip': {'type': 'string'},
                        'timestamp': {'type': 'string', 'format': 'date-time'},
                        'face_image': {'type': 'string'},
                        'distance': {'type': 'number'}
                    }
                }
            }
        }
    )
    def get(self, request,  format=None):
        try:
            # Get date filter from query params
            date_str = request.query_params.get('date')
            queryset = EmployeeCameraStats.objects.select_related('employee', 'camera').order_by('-timestamp')

            if date_str:
                try:
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    queryset = queryset.filter(timestamp__date=filter_date)
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            result = [
                {
                    "employee_id": stat.employee.id,
                    "last_name": stat.employee.first_name,
                    "firs_name": stat.employee.last_name,
                    "region": stat.employee.region.name if stat.employee.region else None,
                    "position": stat.employee.position if stat.employee.position else None,
                    "camera_ip": stat.camera.ip_address,
                    "timestamp": stat.timestamp.isoformat(),
                    "face_image":site_url + stat.face_image.url if stat.face_image else None,
                    "distance": stat.distance
                }
                for stat in queryset
            ]
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching employee camera stats: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class EmployeeCameraStatsDetailView(APIView):
    """
    Retrieve statistics of face captures per employee per camera, with daily filtering.
    """
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

   
    def get(self, request, pk, format=None):
        try:
            # Get date filter from query params
            date_str = request.query_params.get('date')
            queryset = EmployeeCameraStats.objects.select_related('employee', 'camera').filter(employee__employee_id=pk).order_by('-timestamp')

            if date_str:
                try:
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    queryset = queryset.filter(timestamp__date=filter_date)
                except ValueError:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            result = [
                {
                    "employee_id": stat.employee.id,
                    "last_name": stat.employee.first_name,
                    "firs_name": stat.employee.last_name,
                    "region": stat.employee.region.name if stat.employee.region else None,
                    "position": stat.employee.position if stat.employee.position else None,
                    "camera_ip": stat.camera.ip_address,
                    "timestamp": stat.timestamp.isoformat(),
                    "face_image":site_url + stat.face_image.url if stat.face_image else None,
                    "distance": stat.distance
                }
                for stat in queryset
            ]
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching employee camera stats: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Statistics and Reports
@extend_schema(
    summary="Get attendance statistics",
    description="Get attendance statistics by region for today",
    responses={200: AttendanceStatsSerializer(many=True)}
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def attendance_stats(request):
    """Get attendance statistics by region for today"""
    today = timezone.now().date()
    
    stats = []
    for region in Region.objects.filter(is_active=True):
        total_employees = region.employees.filter(is_active=True).count()
        arrivals = region.attendance_records.filter(date=today, status='come').count()
        latecomers = region.attendance_records.filter(date=today, status='latecomers').count()
        absentees = total_employees - arrivals - latecomers
        
        attendance_rate = (arrivals / total_employees * 100) if total_employees > 0 else 0
        
        stats.append({
            'region': region.label or region.get_name_display(),
            'total_employees': total_employees,
            'arrivals': arrivals,
            'latecomers': latecomers,
            'absentees': absentees,
            'attendance_rate': round(attendance_rate, 2)
        })
    
    serializer = AttendanceStatsSerializer(stats, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Link unknown face to employee",
    description="Link an unknown face record to an existing employee",
    request=UnknownFaceLinkSerializer,
    responses={200: {'description': 'Successfully linked'}}
)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def link_unknown_face(request):
    """Link unknown face to employee"""
    serializer = UnknownFaceLinkSerializer(data=request.data)
    if serializer.is_valid():
        unknown_face_id = serializer.validated_data['unknown_face_id']
        employee_id = serializer.validated_data['employee_id']
        
        try:
            unknown_face = UnknownFace.objects.get(id=unknown_face_id)
            employee = Employee.objects.get(id=employee_id)
            
            # Link the unknown face to employee
            unknown_face.linked_employee = employee
            unknown_face.is_processed = True
            unknown_face.save()
            
            # Create an image record for the employee
            Image.objects.create(
                employee=employee,
                camera=unknown_face.camera,
                image=unknown_face.face_image,
                face_encoding=unknown_face.face_encoding
            )
            
            logger.info(f"Unknown face {unknown_face_id} linked to employee {employee_id}")
            
            return Response({
                'message': 'Unknown face successfully linked to employee',
                'unknown_face_id': unknown_face_id,
                'employee_id': employee_id
            })
            
        except (UnknownFace.DoesNotExist, Employee.DoesNotExist) as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error linking unknown face: {e}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Get dashboard data",
    description="Get dashboard statistics and recent activities"
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Get dashboard statistics"""
    today = timezone.now().date()
    
    # Overall statistics
    total_employees = Employee.objects.filter(is_active=True).count()
    total_regions = Region.objects.filter(is_active=True).count()
    total_cameras = Camera.objects.filter(status='active').count()
    
    # Today's attendance
    today_attendance = AttendanceRecord.objects.filter(date=today).count()
    today_arrivals = AttendanceRecord.objects.filter(date=today, status='come').count()
    today_latecomers = AttendanceRecord.objects.filter(date=today, status='latecomers').count()
    
    # Recent unknown faces
    recent_unknown = UnknownFace.objects.filter(
        is_processed=False
    ).order_by('-recorded_at')[:5]
    
    # Recent attendance records
    recent_attendance = AttendanceRecord.objects.select_related(
        'employee', 'camera'
    ).order_by('-recorded_at')[:10]
    
    return Response({
        'overview': {
            'total_employees': total_employees,
            'total_regions': total_regions,
            'total_cameras': total_cameras,
            'today_attendance': today_attendance,
            'today_arrivals': today_arrivals,
            'today_latecomers': today_latecomers,
        },
        'recent_unknown_faces': UnknownFaceSerializer(recent_unknown, many=True).data,
        'recent_attendance': AttendanceRecordSerializer(recent_attendance, many=True).data,
    })

