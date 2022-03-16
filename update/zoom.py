import requests, sys
from pathlib import Path

DEB_PATH = "/usr/local/debs/zoom.deb"

def download(url: str, path: Path):
    r = requests.get(url)
    len = int(r.headers['Content-Length'])
    with open(path, "wb") as file:
        for count, chunk in enumerate(r.iter_content(chunk_size=1024)):
            file.write(chunk)
            sys.stdout.write(f"\033[1G\033[2KDownloading from {url} ({((count * 1024) / len) * 100:.2f}%)...")
            sys.stdout.flush()
    print()

download("https://zoom.us/client/latest/zoom_amd64.deb", DEB_PATH)