import argparse
import hashlib
import logging
import os
from pathlib import Path

from hash_directory.terminal_formatting import parse_color, print_temp, hide_temp
from hash_directory.version import program_version

log = logging.getLogger("hash-directory")
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.DEBUG)
console.setFormatter(
    logging.Formatter(parse_color("{asctime} [ℂ3.{levelname:>5}ℂ.] ℂ4.{name}ℂ.: {message}"),
                      style="{", datefmt="%W %a %I:%M"))

PROGRAM_NAME = "hash-directory"


def hash_directory(path: Path, hash_function=hashlib.sha256):
    hasher = DirectoryHasher(hash_function=hash_function)
    return hasher.hash(path)


def compare_directories(a: Path, b: Path, hash_function=hashlib.sha256):
    log.debug(f"Comparing {a} to {b}")

    hasher = DirectoryHasher(hash_function=hash_function)

    def filenames(sub_path: Path):
        files = set()

        for path in [a, b]:
            if (path / sub_path).is_dir():
                for file in (path / sub_path).iterdir():
                    files.add(file.name)

        files = list(files)
        files.sort()

        return files

    def compare_at(sub_path: Path):
        log.debug(f"Comparing at {sub_path}")

        if not (a / sub_path).exists() or not (b / sub_path).exists():
            missing = [str(p) for p in [a, b] if not (p / sub_path).exists()]
            print(parse_color(
                f"File missing in ℂ1.{", ".join(missing)}ℂ.: ℂ4.{sub_path}ℂ."))
        else:
            hash_a = hasher.hash(a / sub_path)
            hash_b = hasher.hash(b / sub_path)

            if hash_a != hash_b:
                print(f"Files differ at {sub_path}")

        for filename in filenames(sub_path):
            compare_at(sub_path / filename)

    compare_at(Path(os.curdir))


class DirectoryHasher:
    def __init__(self, hash_function=hashlib.sha256):
        self._hash_function = hash_function
        self._hashes = {}

    def _hash_file(self, path: Path):
        with open(path, "rb") as fp:
            return hashlib.file_digest(fp, self._hash_function).hexdigest()

    def _hash_dir(self, path: Path):
        the_hash = self._hash_function()

        for file in sorted(path.iterdir(), key=lambda p: p.name):
            the_hash.update(file.name.encode("utf-8"))
            the_hash.update(self.hash(file).encode("utf-8"))

        return the_hash.hexdigest()

    def hash(self, path: Path):
        print_temp(f"Hashing {path}")
        path = Path(path)
        path = path.resolve(strict=True)

        if path.is_file():
            the_hash = self._hash_file(path)
        else:
            the_hash = self._hash_dir(path)

        self._hashes[str(path)] = the_hash
        hide_temp()
        return the_hash

    def hash_overview(self, path: Path, _relative_to=None, _recursion_depth=0):
        path = Path(path)

        if _relative_to is None:
            _relative_to = path

        if path.is_file():
            return f"{path.relative_to(_relative_to)} \t{self.hash(path)}\n"
        else:
            output = ""
            for file in sorted(path.iterdir(), key=lambda p: p.name):
                output += self.hash_overview(file, _relative_to=_relative_to,
                                             _recursion_depth=_recursion_depth + 1)
            return output


def command_entry_point():
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Program was interrupted by user")


def main():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description="",
                                     allow_abbrev=True, add_help=True, exit_on_error=True)

    parser.add_argument('-v', '--verbose', action='store_true', help="Show more output")
    parser.add_argument("--version", action="store_true", help="Show the current version of the program")

    parser.add_argument("-o", "--overview", action="store_true", help="Show an overview of all hashes in directory")
    parser.add_argument("-c", "--compare", help="Compare the hashes of PATH and its subdirectories with COMPARE")
    parser.add_argument("PATH", help="The directory to hash")

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    if args.version:
        log.info(f"{PROGRAM_NAME} version {program_version}")
        return

    if args.compare is not None:
        compare_directories(args.PATH, args.compare)
    elif args.overview:
        print(DirectoryHasher().hash_overview(args.PATH))
    else:
        print(hash_directory(args.PATH))
