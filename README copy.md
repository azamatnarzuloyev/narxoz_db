# Django Attendance System with Face Recognition

A comprehensive employee attendance management system built with Django REST Framework, featuring face recognition capabilities, real-time monitoring, and comprehensive reporting.

## 🚀 Features

### Core Features
- **Employee Management**: Complete CRUD operations for employees with detailed profiles
- **Face Recognition**: AI-powered face recognition for attendance tracking
- **Real-time Monitoring**: Live attendance tracking with camera integration
- **Multi-location Support**: Support for multiple regions, filials, and terminals
- **Comprehensive Reporting**: Detailed attendance reports and statistics
- **Admin Dashboard**: Full-featured admin interface for system management

### Technical Features
- **REST API**: Complete RESTful API with OpenAPI documentation
- **Authentication**: Token-based authentication system
- **Database Optimization**: Optimized queries with proper indexing
- **Caching**: Redis-based caching for improved performance
- **Background Tasks**: Celery integration for async processing
- **Docker Support**: Complete containerization with Docker Compose
- **Production Ready**: Nginx, PostgreSQL, Redis integration

## 📋 Requirements

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

## 🛠️ Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd django-attendance-system
   \`\`\`

2. **Setup the project**
   \`\`\`bash
   make setup
   \`\`\`

3. **Start the services**
   \`\`\`bash
   make up
   \`\`\`

4. **Access the application**
   - API: http://localhost/api/v1/
   - Admin Panel: http://localhost/admin/
   - API Documentation: http://localhost/api/docs/
   - ReDoc: http://localhost/api/redoc/

### Default Credentials
- **Admin User**: admin / admin123
- **API Token**: Generate via admin panel or login endpoint

## 🏗️ Architecture

### Project Structure
\`\`\`
attendance_system/
├── apps/
│   ├── attendance/          # Main attendance app
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── serializers.py  # Data serializers
│   │   ├── filters.py      # Query filters
│   │   └── admin.py        # Admin interface
│   └── authentication/     # Authentication app
├── attendance_system/      # Project settings
├── scripts/               # Utility scripts
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker image definition
├── nginx.conf           # Nginx configuration
└── requirements.txt     # Python dependencies
\`\`\`

### Database Models
- **Region**: Geographic regions/departments
- **Filial**: Branch offices
- **Employee**: Employee information and profiles
- **Terminal**: Access control terminals
- **Camera**: Surveillance cameras for face recognition
- **AttendanceRecord**: Daily attendance records
- **UnknownFace**: Unrecognized face records
- **Image**: Employee face images for recognition

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - Get user profile
- `POST /api/v1/auth/change-password/` - Change password

### Employee Management
- `GET /api/v1/employees/` - List employees
- `POST /api/v1/employees/` - Create employee
- `GET /api/v1/employees/{id}/` - Get employee details
- `PUT /api/v1/employees/{id}/` - Update employee
- `DELETE /api/v1/employees/{id}/` - Delete employee

### Attendance
- `GET /api/v1/attendance/` - List attendance records
- `POST /api/v1/attendance/` - Create attendance record
- `GET /api/v1/attendance/{id}/` - Get attendance details
- `PUT /api/v1/attendance/{id}/` - Update attendance record

### Face Recognition
- `POST /api/v1/face-result/` - Process face recognition result
- `GET /api/v1/unknown-faces/` - List unknown faces
- `POST /api/v1/link-unknown-face/` - Link unknown face to employee

### Statistics
- `GET /api/v1/stats/attendance/` - Get attendance statistics
- `GET /api/v1/dashboard/` - Get dashboard data

### System Management
- `GET /api/v1/regions/` - List regions
- `GET /api/v1/cameras/` - List cameras
- `GET /api/v1/terminals/` - List terminals

## 🔍 Face Recognition API

### Processing Face Recognition Results

Send face recognition data to the system:

\`\`\`bash
curl -X POST http://localhost/api/v1/face-result/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@face_image.jpg" \
  -F "user=123" \
  -F "cosine_similarity=0.85" \
  -F "camera_ip=192.168.1.64"
\`\`\`

### Parameters
- `file`: Face image file (required)
- `user`: Employee ID or "unrecognized" (required)
- `cosine_similarity`: Recognition confidence score (required)
- `camera_ip`: Camera IP address (optional, defaults to 192.168.1.64)

### Response
\`\`\`json
{
  "status": "ok",
  "employee_id": 123,
  "cosine_similarity": 0.85,
  "saved_file": "/path/to/saved/file.jpg",
  "message": "Attendance recorded successfully"
}
\`\`\`

## 📊 Filtering and Search

### Employee Filtering
\`\`\`bash
# Search by name
GET /api/v1/employees/?search=john

# Filter by position
GET /api/v1/employees/?position=developer

# Filter by region
GET /api/v1/employees/?region=1

# Filter by status
GET /api/v1/employees/?status=active

# Date range filtering
GET /api/v1/employees/?created_from=2023-01-01&created_to=2023-12-31
\`\`\`

### Attendance Filtering
\`\`\`bash
# Filter by date
GET /api/v1/attendance/?date=2023-12-01

# Filter by date range
GET /api/v1/attendance/?date_from=2023-12-01&date_to=2023-12-31

# Filter by employee
GET /api/v1/attendance/?employee=1

# Filter by status
GET /api/v1/attendance/?status=come
\`\`\`

## 🚀 Deployment

### Production Deployment

1. **Update environment variables**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with production values
   \`\`\`

2. **Build and deploy**
   \`\`\`bash
   docker-compose -f docker-compose.yml up -d
   \`\`\`

3. **Setup SSL (recommended)**
   - Configure SSL certificates in nginx.conf
   - Update ALLOWED_HOSTS in settings

### Environment Variables

Key environment variables for production:

\`\`\`env
DEBUG=False
DJANGO_ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
\`\`\`

## 🧪 Testing

### Run Tests
\`\`\`bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test
docker-compose exec web python manage.py test apps.attendance.tests.test_models
\`\`\`

### Performance Testing
\`\`\`bash
make performance-test
\`\`\`

## 📝 Development

### Local Development Setup
\`\`\`bash
# Setup virtual environment
make dev-setup

# Run development server
make dev-run

# Or with Docker
make up
\`\`\`

### Code Quality
\`\`\`bash
# Format code
make format

# Lint code
make lint

# Security check
make security-check
\`\`\`

### Database Operations
\`\`\`bash
# Create migrations
make makemigrations

# Apply migrations
make migrate

# Backup database
make backup-db

# Restore database
make restore-db FILE=backup.sql

# Seed sample data
make seed
\`\`\`

## 🔧 Useful Commands

\`\`\`bash
# View logs
make logs

# Access Django shell
make shell

# Access container bash
make bash

# Restart services
make restart

# Check service status
make status

# Clean up
make clean
\`\`\`

## 📈 Monitoring and Logging

### Logs Location
- Application logs: `/app/logs/django.log`
- Access logs via: `make logs`

### Health Checks
- API Health: `GET /api/v1/employees/` (should return 200)
- Database: Check via admin panel

## 🔒 Security Considerations

1. **Authentication**: All endpoints require token authentication
2. **CORS**: Configure `CORS_ALLOWED_ORIGINS` for frontend domains
3. **File Uploads**: Images are validated and stored securely
4. **Database**: Use strong passwords and limit access
5. **SSL**: Enable HTTPS in production

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   \`\`\`bash
   # Check database status
   docker-compose ps db
   # Restart database
   docker-compose restart db
   \`\`\`

2. **Permission Denied**
   \`\`\`bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   \`\`\`

3. **Port Already in Use**
