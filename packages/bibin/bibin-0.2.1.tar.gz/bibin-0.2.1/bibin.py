#!/usr/bin/env python3
# SPDX-License-Identifier: WTFPL

import argparse
from collections.abc import Iterable
from configparser import ConfigParser, Error as ConfigError
from dataclasses import dataclass
import datetime
import errno
import json
import locale
import os
from pathlib import Path
import stat as stat_module
import sys
from textwrap import dedent
from urllib.parse import quote, unquote
import uuid


__version__ = "0.2.1"


DELETION_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_home_trash():
    xdg_data_home = Path(
        os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share"
    )
    return xdg_data_home / "Trash"


@dataclass
class TrashedFile:
    info: Path
    file: Path
    original_path: Path
    deletion_date: datetime.datetime


def _rmrec(path: Path, rootstat):
    stat = path.lstat()
    if rootstat.st_dev != stat.st_dev:
        raise Exception()

    if stat_module.S_ISDIR(stat.st_mode):
        # if we don't have write access, we won't be able to delete anything
        path.chmod(stat.st_mode | stat_module.S_IWUSR)

        for sub in path.iterdir():
            yield from _rmrec(sub, rootstat)

        yield path
        try:
            path.rmdir()
        except FileNotFoundError:
            pass

    else:
        yield path
        path.unlink(missing_ok=True)


def rmtree(path):
    return _rmrec(path, path.lstat())


def resolve_parents(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    return path.parent.resolve() / path.name


class TrashDirectory:
    def __init__(self, root: Path, relroot: Path):
        self.rootdir = root
        self.infodir = root / "info"
        self.filesdir = root / "files"
        self.stat = self.rootdir.stat()
        self.relroot = relroot

    def __repr__(self) -> str:
        return f"<{type(self).__name__} root={self.rootdir!r}>"

    def _get_file_from_info(self, infopath: Path) -> Path:
        return self.filesdir / infopath.stem

    def _get_info_from_file(self, filepath: Path) -> Path:
        return self.infodir / f"{filepath.name}.trashinfo"

    def iter_trashed(self) -> Iterable[TrashedFile]:
        for info in self._iter_info():
            file = self._parse_info(info)
            if not file:
                continue

            try:
                file.file.lstat()
            except FileNotFoundError:
                continue

            yield file

    def _iter_info(self) -> Iterable[Path]:
        return self.infodir.glob("*.trashinfo")

    def get_info(self, infopath: Path) -> TrashedFile | None:
        file = self._parse_info(infopath)
        if not file:
            return None

        try:
            file.file.lstat()
        except FileNotFoundError:
            return None
        return file

    def _parse_info(self, infopath: Path) -> TrashedFile | None:
        parser = ConfigParser(interpolation=None)
        try:
            with infopath.open() as fp:
                parser.read_file(fp)
        except IOError:
            # TODO catch more exceptions
            # TODO raise specific exception
            return None
        except UnicodeError:
            return None

        original_path = self.relroot / Path(unquote(parser["Trash Info"]["Path"]))
        try:
            deletion_date = datetime.datetime.strptime(
                parser["Trash Info"]["DeletionDate"], DELETION_DATE_FORMAT,
            )
        except (KeyError, ValueError):
            deletion_date = None

        return TrashedFile(
            info=infopath,
            file=self._get_file_from_info(infopath),
            original_path=original_path,
            deletion_date=deletion_date,
        )

    def erase(self, trashed: TrashedFile) -> None:
        stat = trashed.file.lstat()
        if stat_module.S_ISDIR(stat.st_mode):
            for _ in rmtree(trashed.file):
                pass
        else:
            trashed.file.unlink(missing_ok=True)
        trashed.info.unlink(missing_ok=True)

    def restore(self, trashed: TrashedFile) -> None:
        trashed.file.rename(trashed.original_path)
        trashed.info.unlink(missing_ok=True)

    def iter_orphans(self) -> Iterable[Path]:
        """Iter files without info"""
        for file in self.filesdir.iterdir():
            info = self._get_info_from_file(file)
            try:
                info.lstat()
            except FileNotFoundError:
                yield file

    def clean_spurious(self) -> Iterable[None]:
        """Removes info files without data file, or unusable info"""
        for info in self._iter_info():
            file = self._get_file_from_info(info)
            try:
                file.lstat()
            except FileNotFoundError:
                print(f"removing {info}")
                info.unlink()
                yield
                continue

            # if only original_path is missing or invalid, the file will be "orphan"
            try:
                self._parse_info(info)
            except ConfigError:
                print(f"removing {info}")
                info.unlink()
                yield
                continue

    def _name_or_none(self, fn: str) -> str | None:
        try:
            return (self.infodir / f"{fn}.trashinfo").open("x")
        except FileExistsError:
            return None

    def _create_info(self, original_name: str, deletion_date: datetime.datetime):
        original_name = original_name.replace("\n", "-")
        return (
            self._name_or_none(original_name)
            or self._name_or_none(f"{deletion_date:%Y%m%d-%H%M%S}-{original_name}")
            or self._name_or_none(str(uuid.uuid4()))
        )

    def is_eligible(self, original: Path) -> bool:
        original_stat = original.lstat()
        if original_stat.st_dev != self.stat.st_dev:
            return False

        return True

    def trash_file(self, original: Path) -> TrashedFile:
        original = resolve_parents(original)

        if not self.is_eligible(original):
            raise IOError(errno.EXDEV)

        try:
            rel_or_abs = original.relative_to(self.relroot)
        except ValueError:
            rel_or_abs = original
        deletion_date = datetime.datetime.now()
        deletion_date_str = deletion_date.strftime(DELETION_DATE_FORMAT)
        infodata = dedent(f"""
            [Trash Info]
            Path={quote(str(rel_or_abs))}
            DeletionDate={deletion_date_str}
        """).lstrip()

        with self._create_info(original.name, deletion_date) as fp:
            info_path = Path(fp.name)
            fp.write(infodata)

        target_file = self._get_file_from_info(info_path)
        try:
            original.rename(target_file)
        except FileNotFoundError:
            info_path.unlink(missing_ok=True)
            raise

        return self.get_info(info_path)


class TrashDetector:
    @classmethod
    def _iter_top_dirs(cls) -> Iterable[Path]:
        for line in Path("/proc/mounts").read_text().strip().split("\n"):
            yield Path(line.split()[1])

    @classmethod
    def iter_trashes(cls) -> Iterable[TrashDirectory]:
        home_trash = get_home_trash()
        if home_trash.is_dir():
            yield TrashDirectory(home_trash, home_trash.parent)

        uid = os.getuid()
        for top_dir in cls._iter_top_dirs():
            trash = top_dir / ".Trash"
            try:
                stat = trash.lstat()
            except OSError:
                pass
            else:
                if (
                    stat_module.S_ISDIR(stat.st_mode)
                    and stat.st_mode & stat_module.S_ISVTX
                ):
                    trash = trash / str(uid)
                    if trash.is_dir():
                        yield TrashDirectory(trash, top_dir)
                        continue

            trash = top_dir / f".Trash-{uid}"
            try:
                trash.lstat()
            except OSError:
                pass
            else:
                if trash.is_dir():
                    yield TrashDirectory(trash, top_dir)
                    continue

    @classmethod
    def create_home_trash(cls) -> TrashDirectory:
        path = get_home_trash()
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)
        cls._sub_mkdir(path)
        # check W_OK?
        return TrashDirectory(path, path.parent)

    @classmethod
    def create_top_trash_at(cls, top_dir: Path) -> TrashDirectory | None:
        uid = os.getuid()
        trash = top_dir / ".Trash"
        if trash.is_dir() and not trash.is_symlink():
            stat = trash.lstat()
            if stat.st_mode & stat_module.S_ISVTX:
                trash = trash / str(uid)
                try:
                    trash.mkdir(exist_ok=True)
                    trash.chmod(0o700)
                    cls._sub_mkdir(trash)
                except OSError:
                    pass
                else:
                    if os.access(trash, os.W_OK):
                        return TrashDirectory(trash, top_dir)

        trash = top_dir / f".Trash-{uid}"
        try:
            trash.mkdir(exist_ok=True)
            trash.chmod(0o700)
            cls._sub_mkdir(trash)
        except OSError:
            pass
        else:
            if os.access(trash, os.W_OK):
                return TrashDirectory(trash, top_dir)

    @classmethod
    def _sub_mkdir(cls, trash: Path) -> None:
        (trash / "files").mkdir(exist_ok=True)
        (trash / "info").mkdir(exist_ok=True)

    @classmethod
    def find_top_dir(cls, path: Path) -> Path:
        # don't resolve path, caller may want to delete a symlink
        # and Path.absolute doesn't normalize path, which is a problem for .parent
        path = Path(os.path.abspath(path))
        while not path.is_mount():
            path = path.parent
        return path

    @classmethod
    def get_trash_of(cls, info_path: Path) -> TrashDirectory | None:
        trash_root = info_path.parent.parent

        home_trash = get_home_trash()
        if trash_root == home_trash:
            return TrashDirectory(home_trash, home_trash.parent)

        top = cls.find_top_dir(info_path)
        if trash_root.parent == top:
            return TrashDirectory(trash_root, top)

    @classmethod
    def create_trash_for(cls, to_delete: Path) -> TrashDirectory | None:
        to_delete = resolve_parents(to_delete)

        home_trash = get_home_trash()
        home_top = cls.find_top_dir(home_trash)
        if to_delete.lstat().st_dev == home_top.lstat().st_dev:
            cls.create_home_trash()
            return TrashDirectory(home_trash, home_trash.parent)

        top_dir = cls.find_top_dir(to_delete)
        return cls.create_top_trash_at(top_dir)


MODE_TYPES = {
    stat_module.S_ISREG: "-",
    stat_module.S_ISDIR: "d",
    stat_module.S_ISLNK: "l",
    stat_module.S_ISBLK: "b",
    stat_module.S_ISCHR: "c",
    stat_module.S_ISSOCK: "s",
    stat_module.S_ISFIFO: "p",
}


def mode_to_string(mode):
    result = list("?---------")
    perms = stat_module.S_IMODE(mode)
    for func in MODE_TYPES:
        if func(mode):
            result[0] = MODE_TYPES[func]
            break

    if perms & 0o400:
        result[1] = "r"
    if perms & 0o200:
        result[2] = "w"
    if perms & 0o4000:
        if perms & 0o100:
            result[3] = "s"
        else:
            result[3] = "S"
    elif perms & 0o100:
        result[3] = "x"

    if perms & 0o40:
        result[4] = "r"
    if perms & 0o20:
        result[5] = "w"
    if perms & 0o2000:
        if perms & 0o10:
            result[6] = "s"
        else:
            result[6] = "S"
    elif perms & 0o10:
        result[6] = "x"

    if perms & 0o4:
        result[7] = "r"
    if perms & 0o2:
        result[8] = "w"
    if perms & 0o1000:
        if perms & 0o1:
            result[9] = "t"
        else:
            result[9] = "T"
    elif perms & 0o1:
        result[9] = "x"

    return "".join(result)


def trashed_to_json_entry(trashed):
    # roughly the same columns as nushell's ls
    stat = trashed.file.lstat()
    result = {
        "name": trashed.original_path.name,
        "type": "dir" if stat_module.S_ISDIR(stat.st_mode) else "file", # FIXME
        "size": stat.st_size,
        "accessed": datetime.datetime.fromtimestamp(stat.st_atime).astimezone(),
        "modified": datetime.datetime.fromtimestamp(stat.st_mtime).astimezone(),
        "inode": stat.st_ino,
        "mode": mode_to_string(stat.st_mode),
        "readonly": stat.st_mode & stat_module.S_IWUSR,
        "target": None,
        "deleted_at": trashed.deletion_date.astimezone(),
        "original_path": str(trashed.original_path),
        "trashed_path": str(trashed.file),
        "info_path": str(trashed.info),
    }
    try:
        result["user"] = trashed.file.owner()
        result["group"] = trashed.file.group()
    except (KeyError, FileNotFoundError):
        # FIXME use lstat
        pass

    return result


def trashdir_to_json(trashdir):
    return {"path": trashdir.rootdir}


def json_convert(value):
    if isinstance(value, Path):
        return str(value)
    elif isinstance(value, datetime.datetime):
        return value.strftime("%F %T %z")
    raise TypeError(f"{type(value)} object can't be serialized")


def main():
    locale.setlocale(locale.LC_ALL, "")

    parser = argparse.ArgumentParser()

    subs = parser.add_subparsers(
        required=True, dest="cmd",
        help="Sub-command",
    )
    subs.add_parser(
        "list",
        help="List files/folders in the trash directory",
    )

    sub = subs.add_parser(
        "put",
        help="Put PATH in the appropriate trash dir (can be undone by restoring)",
    )
    sub.add_argument(
        "paths", nargs="+", type=Path, metavar="PATH",
    )

    sub = subs.add_parser(
        "erase",
        help="Remove PATH from trash (can't be undone)",
    )
    sub.add_argument(
        "paths", nargs="+", type=Path, metavar="PATH",
    )

    sub = subs.add_parser(
        "restore",
        help="Restore PATH from trash",
    )
    sub.add_argument(
        "paths", nargs="+", type=Path, metavar="PATH",
    )

    subs.add_parser(
        "list-trashes",
        help="List trash directories",
    )
    subs.add_parser(
        "clean-spurious",
    )
    subs.add_parser(
        "list-orphans",
    )

    parser.add_argument(
        "--json", action="store_true",
        help="Output results in JSON",
    )
    parser.add_argument(
        "--trash-dir", type=Path,
        help="When listing, use TRASH_DIR instead of home trash dir",
    )

    args = parser.parse_args()
    result = 0

    if args.trash_dir:
        trash = TrashDirectory(
            args.trash_dir, TrashDetector.find_top_dir(args.trash_dir)
        )
    else:
        home = get_home_trash()
        trash = TrashDirectory(home, home.parent)

    if args.cmd == "list":
        items = list(trash.iter_trashed())
        if args.json:
            items = [
                trashed_to_json_entry(item) for item in items
            ]
            print(json.dumps(items, default=json_convert))
        else:
            for trashed in items:
                print(trashed.original_path)
    elif args.cmd == "list-orphans":
        print(list(trash.iter_orphans()))
    elif args.cmd == "list-trashes":
        trashes = list(TrashDetector.iter_trashes())
        if args.json:
            items = [
                trashdir_to_json(item) for item in trashes
            ]
            print(json.dumps(items, default=json_convert))
        else:
            for trashdir in trashes:
                print(trashdir.rootdir)
    elif args.cmd == "clean_spurious":
        for _ in trash.clean_spurious():
            pass
    elif args.cmd == "put":
        for path in args.paths:
            to_delete = resolve_parents(path)
            trash = TrashDetector.create_trash_for(to_delete)
            trash.trash_file(to_delete)
    elif args.cmd == "erase":
        for path in args.paths:
            trash = TrashDetector.get_trash_of(path)
            info = trash.get_info(path)
            if info:
                trash.erase(info)
            else:
                print(f"error: no trashed file at {path}", file=sys.stderr)
                result = os.EX_NOINPUT
    elif args.cmd == "restore":
        for path in args.paths:
            trash = TrashDetector.get_trash_of(path)
            info = trash.get_info(path)
            if not info:
                raise FileNotFoundError(f"no trashed file at {path}")
            trash.restore(info)
    else:
        raise NotImplementedError()

    return result


if __name__ == "__main__":
    sys.exit(main())
