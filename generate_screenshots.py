from pathlib import Path
import subprocess, time, os, signal

ROOT = Path(__file__).resolve().parent
SCREEN_DIR = ROOT / 'docs' / 'screenshots'
SCREEN_DIR.mkdir(parents=True, exist_ok=True)

server = subprocess.Popen(['python', 'run.py'], cwd=ROOT)
try:
    time.sleep(4)
    pages = {
        'landing-page.png': 'http://127.0.0.1:5000/',
        'dashboard.png': 'http://127.0.0.1:5000/dashboard',
        'report.png': 'http://127.0.0.1:5000/report/9',
    }
    for name, url in pages.items():
        subprocess.run([
            'chromium', '--headless', '--disable-gpu', f'--screenshot={SCREEN_DIR / name}', '--window-size=1440,1200', url
        ], check=True)
finally:
    server.terminate()
