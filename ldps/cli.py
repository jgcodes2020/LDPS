#!/usr/bin/python3

from argparse import ArgumentParser
import io
import os
import shlex
import subprocess as subp
import gzip
from pathlib import Path, PurePath
import sys
import typing
from threading import Thread

parser = ArgumentParser(description="The Local Debian Package System (LDPS) manages packages on your local filesystem.")
subparsers = parser.add_subparsers(dest="subcommand", metavar="<subcommand>", help="Subcommand to execute")

# PROGRAM FUNCTIONS
# =======================

def stream_piper(input: io.FileIO, output: io.FileIO, binary=False):
    if binary:
        def read_bin():
            return input.read(1024)
        for chunk in iter(read_bin, b''):
            output.write(chunk)
    else:
        for line in iter(input.readline, b''):
            output.write(line)

def subcommand(help="", args=[], parent=subparsers):
    def decorator(callback):
        parser = None
        if help is None:
            parser = parent.add_parser(callback.__name__)
        else:
            parser = parent.add_parser(callback.__name__, help=help, description=help)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(callback=callback)
    return decorator

# SUBCOMMANDS
# =======================

@subcommand("Update the local package registry so that APT recognizes it.")
def update(args):
    if os.geteuid() != 0:
        print("LDPS needs root privileges to update the local repository.")
        print(f"Try: sudo {shlex.join(sys.argv)}")
        sys.exit(1)
    
    for i in Path("/etc/ldps/autoupdate.d").glob("*.py"):
        print(f"Running updater script [{i.name}]")
        subp.run([sys.executable, str(i)]).check_returncode()
        print()
    
    with gzip.open("/usr/local/debs/Packages.gz", "wb") as file:
        proc = subp.Popen(["dpkg-scanpackages", ".", "/usr/local/debs/deb-override.txt"], stdout=subp.PIPE, cwd="/usr/local/debs")
        piper = Thread(target=stream_piper, args=(proc.stdout, file, True))
        piper.start()
        piper.join()

def main():
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        try:
            args.callback(args)
        except subp.CalledProcessError as e:
            print(f"Error in process {e.cmd}: return code {e.returncode}")
            sys.exit(e.returncode)

if __name__ == "__main__":
    main()
else:
    raise ImportError(
        f"{'ldps.cli' if __name__ == 'ldps.cli' else f'ldps.cli (aliased to {__name__})'} should never be imported", 
        __name__, __file__
    )