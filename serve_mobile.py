import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
DIRECTORY = Path("C:/Users/admin/.gemini/antigravity/scratch/petro_phd_radar_bot")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/dashboard.html"
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(str(DIRECTORY))
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"خادم لوحة التحكم يعمل الآن!")
        print(f"من الكمبيوتر: http://localhost:{PORT}")
        print(f"من هاتفك (المتصل بنفس الواي فاي): http://192.168.1.40:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nتم إيقاف الخادم.")
