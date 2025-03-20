import shutil
from pathlib import Path
import os
from os import PathLike


class FileSession:
    def __init__(self):
        self.backups: dict[Path, bytes | None] = {}
        self.backups_dirs: dict[Path, bool] = {}
        self.objects: list[open] = []

    def __enter__(self):

        return FSession(
            self.backups,
            self.backups_dirs,
            self.objects,
        )

    def _restore_dirs(self):
        for k, v in self.backups_dirs.items():
            if v is False:
                try:
                    shutil.rmtree(k)
                except FileNotFoundError:
                    pass

        for k, v in self.backups_dirs.items():
            if v is True:
                k.mkdir(exist_ok=True, parents=True)

    def _restore_files(self):
        for k, v in self.backups.items():
            if v is None:
                if Path(k).exists():
                    os.remove(k)

        for k, v in self.backups.items():
            if v is not None:
                with open(k, mode="wb") as f:
                    f.write(v)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for obj in self.objects:
            obj.close()

        self._restore_dirs()
        self._restore_files()


class FSession:
    def __init__(
            self,
            backups: dict[Path, bytes | None],
            backups_dirs: dict[Path, bool],
            objects: list[open]
    ):

        self.backups: dict[Path, bytes | None] = backups
        self.backups_dirs: dict[Path, bool] = backups_dirs
        self.objects: list[open] = objects

    def open(
            self,
            file: Path | PathLike[str] | str,
            mode: str = "r",
            buffering: int = -1,
            encoding: str = None,
            *args,
            **kwargs
    ):

        if "r" not in mode or "+" in mode:

            file = Path(os.path.abspath(file))
            if file.exists() is False:
                self.backups[file] = None
            else:
                with open(file, mode="rb") as f:
                    if str(file) not in self.backups:
                        self.backups[file] = f.read()

        obj = open(file, mode, buffering, encoding, *args, **kwargs)
        self.objects.append(obj)
        return obj

    def makedirs(
            self,
            file: Path | PathLike[str] | str,
            exist_ok: bool = False,
            parents: bool = True,
    ):

        path = Path(os.path.abspath(file))
        x = path

        while not x.exists():
            if x.parent.exists():
                if x not in self.backups_dirs:
                    self.backups_dirs[x] = False
                break
            else:
                if x.parent == x:
                    raise IOError(f"Incorrect path: {path}")
            x = x.parent

        path.mkdir(exist_ok=exist_ok, parents=parents)

    def __rmfile(self, path: Path):
        self.__save(path)
        os.remove(path)

    def __rmtree(self, path: Path):
        self.__save(path)
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

    @staticmethod
    def __readtree(
            path: Path | PathLike[str] | str,
    ) -> tuple[set[Path], set[Path]]:
        path = Path(path).absolute()

        paths: list[Path] = [p for p in path.rglob("*")]

        dirs = {path}
        files = set()

        for p in paths:
            if p.is_file():
                files.add(p)
            elif p.is_dir():
                dirs.add(p)
            else:
                raise IOError(f"Incorrect path\\file: {p}")

        return dirs, files

    def __save(self, path: Path | PathLike[str] | str, reverse: bool = False):
        path = Path(path).absolute()

        if path.is_file():
            if path not in self.backups:
                with open(path, "rb") as f:
                    self.backups[path] = f.read()

        elif path.is_dir():

            dirs, files = self.__readtree(path)

            for file in files:
                if file not in self.backups:
                    if reverse is False:
                        with open(file, "rb") as f:
                            self.backups[file] = f.read()
                    else:
                        self.backups[file] = None

            for dir_ in dirs:
                if dir_ not in self.backups_dirs:
                    if reverse is False:
                        self.backups_dirs[dir_] = True
                    else:
                        self.backups_dirs[dir_] = False

        else:
            raise IOError(f"Incorrect path: {path}")

    def rm(self,
           path: Path | PathLike[str] | str
           ):

        path = Path(path).absolute()

        if path.is_file():
            self.__save(path)
            os.remove(path)

        elif path.is_dir():
            self.__save(path)
            shutil.rmtree(path)

        else:
            raise IOError(f"Incorrect path: {path}")

    def copyfile(
            self,
            path: Path | PathLike[str] | str,
            dest: Path | PathLike[str] | str,
            copy_meta: bool = False
    ):
        path = Path(path).absolute()
        dest = Path(dest).absolute()

        if not path.is_file():
            raise IOError(f"Only file may be copied with .copyfile: {path}")

        if not dest.is_dir() and not dest.parent.is_dir():
            raise IOError(f"Incorrect destanation: {dest}")

        if dest.is_dir():
            target_name = path.name
        else:
            target_name = dest.name
            dest = dest.parent

        full_path = dest / target_name
        self.backups[full_path] = None
        if copy_meta:
            shutil.copy2(path, full_path)
        else:
            shutil.copy(path, full_path)

    def copytree(
            self,
            path: Path | PathLike[str] | str,
            dest: Path | PathLike[str] | str,
    ):
        path = Path(path).absolute()
        dest = Path(dest).absolute()

        if not path.is_dir():
            raise IOError(f"Only dir may be copied with .copytree: {path}")

        if not dest.parent.is_dir():
            raise IOError(f"Incorrect destanation: {dest}")

        if dest.is_dir():
            raise IOError(f"Directory already exists: {dest}")

        shutil.copytree(path, dest)

        self.__save(dest, reverse=True)

    def move(
            self,
            path: Path | PathLike[str] | str,
            dest: Path | PathLike[str] | str,
    ):

        path = Path(path).absolute()
        dest = Path(dest).absolute()

        if dest.exists():
            raise IOError(f"Destination already exists: {dest}")

        if not dest.parent.is_dir():
            raise IOError(f"Incorrect destanation: {dest}")

        if path.is_file():
            if dest not in self.backups:
                self.backups[dest] = None
        elif path.is_dir():
            pass
        else:
            raise IOError(f"Incorrect path: {path}")

        self.__save(path)

        shutil.move(path, dest)

        if dest.is_dir():
            self.__save(dest, reverse=True)

    def commit(self):
        self.backups.clear()
        self.backups_dirs.clear()
