import stat
import requests, tempfile, re, sys
from pathlib import Path, PurePath
import subprocess as subp

def download(url: str, path: Path):
    r = requests.get(url)
    len = int(r.headers['Content-Length'])
    with open(path, "wb") as file:
        for count, chunk in enumerate(r.iter_content(chunk_size=1024)):
            file.write(chunk)
            print(f"\033[1G\033[2KDownloading from {url} ({((count * 1024) / len) * 100:.2f}%)...", end='')
            sys.stdout.flush()
    print()

def escape_shell(s: str):
    s = s.replace("'", "'\\''")
    return f"'{s}'"


def chmod_px(path: Path):
    "Performs the equivalent of chmod +x path"
    mode = path.stat().st_mode
    mode |= (mode & 0o444) >> 2
    path.chmod(mode)
