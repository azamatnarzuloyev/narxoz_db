from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import subprocess

app = FastAPI()

# CORS middleware qo'shildi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Barcha domenlarga ruxsat berish
    allow_credentials=True,
    allow_methods=["*"],  # Barcha metodlarga ruxsat berish (GET, POST, va hokazo)
    allow_headers=["*"],  # Barcha headerlarga ruxsat berish
)

def mjpeg_stream():
    """
    FFmpeg yordamida RTSP oqimini MJPEG formatiga aylantiruvchi va 
    to'liq JPEG kadrlarini ajratib olib, multipart formatda yuboruvchi generator.
    """
    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", "rtsp://admin:azamat1796@192.168.1.64/Streaming/Channels/101",
        "-f", "mjpeg",
        "-q:v", "5",
        "-r", "25",
        "-"
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    bytes_buffer = b""

    while True:
        chunk = process.stdout.read(1024)
        if not chunk:
            break
        bytes_buffer += chunk

        start = bytes_buffer.find(b'\xff\xd8')
        end = bytes_buffer.find(b'\xff\xd9')
        if start != -1 and end != -1 and end > start:
            frame = bytes_buffer[start:end+2]
            bytes_buffer = bytes_buffer[end+2:]
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/video")
def video_feed():
    """
    /video endpoint orqali MJPEG stream yuboramiz.
    """
    return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=frame")





# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# import subprocess

# app = FastAPI()

# def mjpeg_stream():
#     """
#     FFmpeg yordamida RTSP oqimini MJPEG formatiga aylantiruvchi va 
#     to'liq JPEG kadrlarini ajratib olib, multipart formatda yuboruvchi generator.
#     """
#     # RTSP URL va kerakli ffmpeg parametrlarini sozlaymiz.
#     command = [
#         "ffmpeg",
#         "-rtsp_transport", "tcp",  # TCP protokoli barqaror oqim uchun
#         "-i", "rtsp://admin:azamat1796@192.168.1.64/Streaming/Channels/101",
#         "-f", "mjpeg",
#         "-q:v", "5",      # Sifat parametri (1 eng yaxshi, 31 eng past)
#         "-r", "25",       # Kadrlar soni (25 FPS)
#         "-"
#     ]
#     process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
#     bytes_buffer = b""

#     while True:
#         # FFmpeg chiqishidan baytlarni o'qib bufferga qo'shamiz
#         chunk = process.stdout.read(1024)
#         if not chunk:
#             break
#         bytes_buffer += chunk

#         # JPEG kadrining boshlanish va tugash markerlarini aniqlaymiz
#         start = bytes_buffer.find(b'\xff\xd8')
#         end = bytes_buffer.find(b'\xff\xd9')
#         if start != -1 and end != -1 and end > start:
#             frame = bytes_buffer[start:end+2]
#             # Qolgan baytlarni bufferga saqlaymiz
#             bytes_buffer = bytes_buffer[end+2:]
#             # Multipart javob formatini shakllantiramiz
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.get("/video")
# def video_feed():
#     """
#     /video endpoint orqali MJPEG stream yuboramiz.
#     Brauzer <img> tegi yoki boshqa mijozlar bu URL orqali oqimni qabul qiladi.
#     """
#     return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=frame")