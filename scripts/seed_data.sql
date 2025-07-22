-- Seed data for the attendance system

-- Insert regions
INSERT INTO attendance_region (name, label, employees_count, arrivals_count, departures_count, absentees_count, is_active, created_at, updated_at) VALUES
('narxoz', 'Narxoz University', 0, 0, 0, 0, true, NOW(), NOW()),
('fiskal', 'Fiskal Department', 0, 0, 0, 0, true, NOW(), NOW()),
('moliya', 'Moliya Department', 0, 0, 0, 0, true, NOW(), NOW());

-- Insert filials
INSERT INTO attendance_filial (name, value, address, is_active, created_at, updated_at) VALUES
('Main Office', 'main', 'Almaty, Kazakhstan', true, NOW(), NOW()),
('Branch Office 1', 'branch1', 'Nur-Sultan, Kazakhstan', true, NOW(), NOW()),
('Branch Office 2', 'branch2', 'Shymkent, Kazakhstan', true, NOW(), NOW());

-- Insert terminals
INSERT INTO attendance_terminal (ip_address, name, port, status, location, last_ping, created_at, updated_at, region_id, filial_id) VALUES
('192.168.1.100', 'Terminal 1', 80, 'active', 'Main Entrance', NOW(), NOW(), NOW(), 1, 1),
('192.168.1.101', 'Terminal 2', 80, 'active', 'Side Entrance', NOW(), NOW(), NOW(), 1, 1),
('192.168.1.102', 'Terminal 3', 80, 'active', 'Back Entrance', NOW(), NOW(), NOW(), 2, 2);

-- Insert cameras
INSERT INTO attendance_camera (name, ip_address, port, login, password, status, location, rtsp_url, last_ping, created_at, updated_at, region_id) VALUES
('Camera 1', '192.168.1.64', 554, 'admin', 'admin123', 'active', 'Main Entrance', 'rtsp://192.168.1.64:554/stream1', NOW(), NOW(), NOW(), 1),
('Camera 2', '192.168.1.65', 554, 'admin', 'admin123', 'active', 'Side Entrance', 'rtsp://192.168.1.65:554/stream1', NOW(), NOW(), NOW(), 1),
('Camera 3', '192.168.1.66', 554, 'admin', 'admin123', 'active', 'Back Entrance', 'rtsp://192.168.1.66:554/stream1', NOW(), NOW(), NOW(), 2);

-- Insert sample employees
INSERT INTO attendance_employee (first_name, last_name, middle_name, employee_id, position, phone_number, email, hire_date, status, is_active, created_at, updated_at, region_id, terminal_id) VALUES
('John', 'Doe', 'Michael', 'EMP0001', 'developer', '+7 777 123 4567', 'john.doe@example.com', '2023-01-15', 'active', true, NOW(), NOW(), 1, 1),
('Jane', 'Smith', 'Elizabeth', 'EMP0002', 'manager', '+7 777 234 5678', 'jane.smith@example.com', '2023-02-01', 'active', true, NOW(), NOW(), 1, 1),
('Bob', 'Johnson', 'Robert', 'EMP0003', 'designer', '+7 777 345 6789', 'bob.johnson@example.com', '2023-03-10', 'active', true, NOW(), NOW(), 2, 2),
('Alice', 'Brown', 'Marie', 'EMP0004', 'accountant', '+7 777 456 7890', 'alice.brown@example.com', '2023-04-05', 'active', true, NOW(), NOW(), 2, 2),
('Charlie', 'Wilson', 'James', 'EMP0005', 'hr', '+7 777 567 8901', 'charlie.wilson@example.com', '2023-05-20', 'active', true, NOW(), NOW(), 3, 3);

-- Insert sample admins
INSERT INTO attendance_admin (name, login, password, status, last_login, created_at, updated_at, region_id, filial_id) VALUES
('System Admin', 'sysadmin', 'pbkdf2_sha256$600000$randomsalt$hashedpassword', 'active', NULL, NOW(), NOW(), 1, 1),
('Regional Admin', 'regadmin', 'pbkdf2_sha256$600000$randomsalt$hashedpassword', 'active', NULL, NOW(), NOW(), 2, 2);

-- Insert sample attendance records for today
INSERT INTO attendance_attendancerecord (check_in, check_out, date, status, distance, notes, recorded_at, created_at, updated_at, employee_id, camera_id, region_id) VALUES
('09:00:00', '18:00:00', CURRENT_DATE, 'come', 0.85, 'On time', NOW(), NOW(), NOW(), 1, 1, 1),
('09:15:00', '18:30:00', CURRENT_DATE, 'latecomers', 0.78, '15 minutes late', NOW(), NOW(), NOW(), 2, 1, 1),
('08:45:00', '17:45:00', CURRENT_DATE, 'come', 0.92, 'Early arrival', NOW(), NOW(), NOW(), 3, 2, 2),
('09:30:00', NULL, CURRENT_DATE, 'latecomers', 0.88, '30 minutes late, no checkout yet', NOW(), NOW(), NOW(), 4, 2, 2);

-- Insert sample attendance records for yesterday
INSERT INTO attendance_attendancerecord (check_in, check_out, date, status, distance, notes, recorded_at, created_at, updated_at, employee_id, camera_id, region_id) VALUES
('09:00:00', '18:00:00', CURRENT_DATE - INTERVAL '1 day', 'come', 0.89, 'Regular day', NOW() - INTERVAL '1 day', NOW(), NOW(), 1, 1, 1),
('09:05:00', '18:15:00', CURRENT_DATE - INTERVAL '1 day', 'come', 0.82, 'Slightly late', NOW() - INTERVAL '1 day', NOW(), NOW(), 2, 1, 1),
(NULL, NULL, CURRENT_DATE - INTERVAL '1 day', 'not_come', NULL, 'Absent', NOW() - INTERVAL '1 day', NOW(), NOW(), 3, NULL, 2),
('09:20:00', '17:50:00', CURRENT_DATE - INTERVAL '1 day', 'latecomers', 0.75, '20 minutes late', NOW() - INTERVAL '1 day', NOW(), NOW(), 4, 2, 2),
('08:55:00', '18:05:00', CURRENT_DATE - INTERVAL '1 day', 'come', 0.91, 'Good attendance', NOW() - INTERVAL '1 day', NOW(), NOW(), 5, 3, 3);

-- Update region counts
UPDATE attendance_region SET 
    employees_count = (SELECT COUNT(*) FROM attendance_employee WHERE region_id = attendance_region.id AND is_active = true),
    arrivals_count = (SELECT COUNT(*) FROM attendance_attendancerecord WHERE region_id = attendance_region.id AND date = CURRENT_DATE AND status = 'come'),
    absentees_count = (SELECT COUNT(*) FROM attendance_attendancerecord WHERE region_id = attendance_region.id AND date = CURRENT_DATE AND status = 'not_come');

COMMIT;
