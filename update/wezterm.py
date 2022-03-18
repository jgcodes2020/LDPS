import tempfile, re, requests, sys
from pathlib import Path
import subprocess as subp
import ldps.utils as utils
from textwrap import dedent

import ldps.utils as utils

DEB_PATH = "/usr/local/debs/wezterm.deb"



print("Grabbing latest release info for wezterm...")

r = requests.get("https://api.github.com/repos/wez/wezterm/releases/latest",
    headers = {
        "Accept": "applications/vnd.github.v3+json"
    }
)

dl_asset = next(i for i in r.json()["assets"] if i["name"].endswith("Ubuntu20.04.deb"))
utils.download(dl_asset['browser_download_url'], DEB_PATH)

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
        append_to_field("Provides", "wezterm", ctl_lines)
        append_to_field("Conflicts", "wezterm", ctl_lines)
        append_to_field("Replaces", "wezterm", ctl_lines)
        ctl_file.truncate(0)
        ctl_file.seek(0)
        ctl_file.writelines(ctl_lines)
    
    # Patch postinst
    print(f"Patching postinst in {Path(DEB_PATH).name}")
    created_file = False
    with open(temp_path / "DEBIAN/postinst", "a") as pi_script:
        if pi_script.tell() == 0:
            created_file = True
            pi_script.write("#!/bin/sh\n")
        pi_script.write(dedent("""
        set -e
        if [ "$1" = "configure" ]; then
            update-alternatives --install /usr/bin/x-terminal-emulator \
            x-terminal-emulator /usr/bin/wezterm 40
        fi
        """))
    if created_file:
        utils.chmod_px(temp_path / "DEBIAN/postinst")
    
    # Patch prerm
    print(f"Patching prerm in {Path(DEB_PATH).name}")
    created_file = False
    with open(temp_path / "DEBIAN/prerm", "a") as pi_script:
        if pi_script.tell() == 0:
            created_file = True
            pi_script.write("#!/bin/sh\n")
        pi_script.write(dedent("""
        set -e
        if [ "$1" = "configure" ]; then
            update-alternatives --remove x-terminal-emulator /usr/bin/wezterm
        fi
        """))
    if created_file:
        utils.chmod_px(temp_path / "DEBIAN/prerm")
    
    # Repack deb
    print(f"Repacking {Path(DEB_PATH).name}")
    subp.run(["dpkg-deb", "-b", temp_str, DEB_PATH]).check_returncode()

print("Done!")
    
    
    
    
    
    