import tempfile
import requests, sys, re
from pathlib import Path
import ldps.utils as utils
import subprocess as subp
import contextlib

DEB_PATH = Path("/usr/local/debs/zoom.deb")

utils.download("https://zoom.us/client/latest/zoom_amd64.deb", DEB_PATH)

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

with tempfile.TemporaryDirectory() as tempdir:
    # Unpack deb
    print(f"Unpacking {DEB_PATH.name} for patching")
    temp_path = Path(tempdir)
    subp.run(["dpkg-deb", "-R", DEB_PATH, tempdir]).check_returncode()
    
    # Patch control file
    with open(temp_path / "DEBIAN/control", "r+") as ctl_file:
        ctl_lines = ctl_file.readlines()
        append_to_field("Provides", "zoom", ctl_lines)
        append_to_field("Conflicts", "zoom", ctl_lines)
        append_to_field("Replaces", "zoom", ctl_lines)
        ctl_file.truncate(0)
        ctl_file.seek(0)
        ctl_file.writelines(ctl_lines)
    
    # Repack deb
    print(f"Repacking {Path(DEB_PATH).name}")
    subp.run(["dpkg-deb", "-b", tempdir, DEB_PATH]).check_returncode()