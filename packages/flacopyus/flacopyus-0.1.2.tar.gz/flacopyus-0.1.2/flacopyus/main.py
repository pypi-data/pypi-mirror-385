import time
import os
import shutil
import subprocess as sp
import io
import functools
from pathlib import Path
from dataclasses import dataclass
from enum import StrEnum
from contextlib import nullcontext
from threading import RLock
from concurrent.futures import ThreadPoolExecutor, Future
from .funs import filter_split
from .stdio import progress_bar, error_console
from .filesys import itreemap, itree


class BitrateMode(StrEnum):
    VBR = "--vbr"
    CBR = "--cbr"
    HardCBR = "--hard-cbr"


class LowBitrateTuning(StrEnum):
    Music = "--music"
    Speech = "--speech"


class Downmix(StrEnum):
    Mono = "--downmix-mono"
    Stereo = "--downmix-stereo"


@dataclass(kw_only=True, frozen=True)
class OpusOptions:
    bitrate: int = 128
    bitrate_mode: BitrateMode = BitrateMode.VBR
    low_bitrate_tuning: LowBitrateTuning | None = None
    downmix: Downmix | None = None


class Error:
    pass


def main(
    src: Path,
    dest: Path,
    *,
    force: bool = False,
    opus_options: OpusOptions = OpusOptions(),
    re_encode: bool = False,
    wav: bool,
    delete: bool = False,
    delete_excluded: bool = False,
    copy_exts: list[str] = [],
    fix_case: bool = False,
    encoding_concurrency: int | None = None,
    allow_parallel_io: bool = False,
    copying_concurrency: int = 1,
):
    encode = build_opusenc_func(
        options=opus_options,
        use_lock=(not allow_parallel_io),
    )
    delete = delete or delete_excluded

    copy_exts = [e.lower() for e in copy_exts]

    extmap = {"flac": "opus"}
    if wav:
        extmap |= {"wav": "opus"}

    for k in extmap:
        if k in copy_exts:
            raise ValueError()

    # TODO: Check SRC and DEST tree overlap for safety
    # TODO: Check some flacs are in SRC to avoid swapped SRC DEST disaster (unlimit with -f)
    if not force:
        pass

    ds: list[Path] = []
    if delete:
        if dest.exists(follow_symlinks=False):
            if delete_excluded:
                ds = list(itree(dest))
            else:
                ds = list(itree(dest, ext=["opus", *copy_exts]))
    will_del_dict: dict[Path, bool] = {p: True for p in ds}

    def fix_case_file(path: Path):
        physical = path.resolve(strict=True)
        if physical.name != path.name:
            physical.rename(path)

    def cp_main(s: Path, d: Path):
        stat_s = s.stat()
        s_ns = stat_s.st_mtime_ns
        # TODO: remove symlink
        if d.is_symlink():
            pass
        # TODO: handle case where destination is a folder and conflicts
        if re_encode or not d.exists(follow_symlinks=False) or s_ns != d.stat().st_mtime_ns:
            cp = encode(s, d)
            copy_mod(s_ns, d)
        if fix_case:
            fix_case_file(d)
        # TODO: Thread safe?
        will_del_dict[d] = False
        return True

    def cp_i(pool: ThreadPoolExecutor, pending: list[tuple[Path, Future[bool]]]):
        def f(s: Path, d: Path):
            future = pool.submit(cp_main, s, d)
            pending.append((s, future))

        return f

    poll = 0.1
    concurrency = max(1, 1 if (cpus := os.cpu_count()) is None else cpus - 1) if encoding_concurrency is None else encoding_concurrency
    pending: list[tuple[Path, Future[bool]]] = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        try:
            for _ in itreemap(cp_i(executor, pending), src, dest=dest, extmap=extmap, mkdir=True, mkdir_empty=False, fix_case=fix_case, progress=False):
                pass
            # Finish remaining tasks
            progress_display = progress_bar(error_console)
            task = progress_display.add_task("Processing", total=len(pending))
            with progress_display:
                while pending:
                    time.sleep(poll)
                    done, pending = filter_split(lambda x: x[1].done(), pending)
                    progress_display.update(task, advance=len(done), refresh=True)
        except KeyboardInterrupt:
            # Exit quickly when interrupted
            executor.shutdown(cancel_futures=True)
            raise

    def copyfile_fsync(s: Path, d: Path):
        with open(s, "rb") as s_fp:
            with open(d, "wb") as d_fp:
                shutil.copyfileobj(s_fp, d_fp)
                d_fp.flush()
                sync_disk(d_fp)

    def ff_(s: Path, d: Path):
        # TODO: remove symlink
        if d.is_symlink():
            pass
        # TODO: handle case where destination is a folder and conflicts
        if not d.exists():
            copyfile_fsync(s, d)
            copy_mod(s, d)
        if s.stat().st_mtime_ns != d.stat().st_mtime_ns or s.stat().st_size != d.stat().st_size:
            copyfile_fsync(s, d)
            copy_mod(s, d)
            if fix_case:
                fix_case_file(d)
        will_del_dict[d] = False
        return True

    def cp(pool, pending):
        def f(s, d):
            future = pool.submit(ff_, s, d)
            pending.append((s, future))

        return f

    pending_cp: list[tuple[Path, Future[bool]]] = []
    with ThreadPoolExecutor(max_workers=copying_concurrency) as executor_cp:
        try:
            for _ in itreemap(cp(executor_cp, pending_cp), src, dest=dest, extmap=copy_exts, mkdir=True, mkdir_empty=False, progress=False):
                pass
            progress_display = progress_bar(error_console)
            task = progress_display.add_task("Copying", total=len(pending_cp))
            with progress_display:
                while pending_cp:
                    time.sleep(poll)
                    done, pending_cp = filter_split(lambda x: x[1].done(), pending_cp)
                    for d, fu in done:
                        # Unwrap for collecting exceptions
                        fu.result()
                    progress_display.update(task, advance=len(done), refresh=True)
        except KeyboardInterrupt:
            # Exit quickly when interrupted
            executor.shutdown(cancel_futures=True)
            raise

    for p, is_deleted in will_del_dict.items():
        if is_deleted:
            p.unlink()

    # TODO: parameterize
    del_dir = True
    purge_dir = True

    try_del = set()

    if del_dir or purge_dir:
        found_emp = None
        while found_emp is not False:
            found_emp = False
            for d, s, is_empty in itreemap(lambda d, s: not any(d.iterdir()), dest, src, file=False, directory=True, mkdir=False):
                if is_empty:
                    # TODO: remove symlink
                    if purge_dir or not s.exists() or not s.is_dir():
                        if d not in try_del:
                            found_emp = True
                            try_del.add(d)
                            d.rmdir()
                            break
                        # TODO: 広いファイル名空間へのマッピング時にフォルダがのこる可能性あり
                        pass

    return 0


def which(cmd: str) -> str:
    match shutil.which(cmd):
        case None:
            raise RuntimeError(f"Command not found: {cmd}")
        case path:
            return path


@functools.cache
def fsync_func():
    try:
        # Available on Unix
        return os.fdatasync
    except AttributeError:
        return os.fsync


def sync_disk(f: io.BufferedIOBase | int):
    fd = f if isinstance(f, int) else f.fileno()
    fsync_func()(fd)


def build_opusenc_func(options: OpusOptions, *, use_lock: bool = True):
    opusenc_bin = which("opusenc")
    cmd_line = [opusenc_bin, "--bitrate", str(options.bitrate)]
    cmd_line.append(options.bitrate_mode.value)
    if options.low_bitrate_tuning is not None:
        cmd_line.append(options.low_bitrate_tuning.value)
    if options.downmix is not None:
        cmd_line.append(options.downmix.value)
    cmd_line.extend(["-", "-"])

    lock = RLock()

    def encode(src_file: Path, dest_opus_file: Path):
        buf = None
        with open(src_file, "rb") as src_fp:
            if use_lock:
                with lock:
                    buf = src_fp.read()
                in_stream = None
            else:
                in_stream = src_fp
            cp = sp.run(cmd_line, text=False, input=buf, stdin=in_stream, capture_output=True, check=True)
        with lock if use_lock else nullcontext():
            with open(dest_opus_file, "wb") as dest_fp:
                dest_fp.write(cp.stdout)
                dest_fp.flush()
                sync_disk(dest_fp)
        return cp

    return encode


def copy_mod(s: int | Path, d: Path):
    if isinstance(s, int):
        ns_s = s
    else:
        ns_s = s.stat().st_mtime_ns
    os.utime(d, ns=(time.time_ns(), ns_s))
