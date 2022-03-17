import requests, tempfile, re, sys
from pathlib import Path, PurePath
import subprocess as subp

DEB_PATH = "/usr/local/debs/wezterm-nightly.deb"

def download(url: str, path: Path):
    r = requests.get(url)
    len = int(r.headers['Content-Length'])
    with open(path, "wb") as file:
        for count, chunk in enumerate(r.iter_content(chunk_size=1024)):
            file.write(chunk)
            print(f"\033[1F\033[1E\033[2KDownloading from {url} ({((count * 1024) / len) * 100:.2f}%)...", end='')
    print()
            


print("Finding latest wezterm release...")

r = requests.get("https://api.github.com/repos/wez/wezterm/releases/tags/nightly",
    headers = {
        "Accept": "applications/vnd.github.v3+json"
    }
)

dl_asset = next(i for i in r.json()["assets"] if i["name"].endswith("Ubuntu20.04.deb"))
download(dl_asset['browser_download_url'], DEB_PATH)

# PATCHING
# ============

def append_to_field(field: str, value: str, lines: list[str]):
    index = next((i for (i, x) in enumerate(lines) if x.startswith(f"{field}:")), None)
    if index is None:
        lines.append(f"{field}: {value}\n")
    else:
        lines[index] = re.sub(r"\n$", f", {value}\n", lines[index])

def replace_field(field: str, value: str, lines: list[str]):
    index = next((i for (i, x) in enumerate(lines) if x.startswith(f"{field}:")), None)
    if index is None:
        lines.append(f"{field}: {value}\n")
    else:
        lines[index] = f"{field}: {value}\n"
        

with tempfile.TemporaryDirectory() as temp_str:
    # Unpack deb
    print(f"Unpacking {Path(DEB_PATH).name} for patching")
    temp_path = Path(temp_str)
    subp.run(["dpkg-deb", "-R", DEB_PATH, temp_str]).check_returncode()
    
    # Patch control file
    print(f"Patching {Path(DEB_PATH).name}")
    ctl_lines = None
    with open(temp_path / "DEBIAN/control", "r+") as ctl_file:
        ctl_lines = ctl_file.readlines()
        replace_field("Package", "wezterm-nightly", ctl_lines)
        append_to_field("Provides", "wezterm", ctl_lines)
        append_to_field("Conflicts", "wezterm", ctl_lines)
        append_to_field("Replaces", "wezterm", ctl_lines)
        ctl_file.truncate(0)
        ctl_file.seek(0)
        ctl_file.writelines(ctl_lines)
    # Repack deb
    print(f"Repacking {Path(DEB_PATH).name}")
    subp.run(["dpkg-deb", "-b", temp_str, DEB_PATH]).check_returncode()

print("Done!")