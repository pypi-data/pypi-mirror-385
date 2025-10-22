import json
import os
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional
import shutil
import hashlib
import atexit
from collections import OrderedDict
import functools
import datetime

def default_cache_dir():
    return os.path.join(Path.home(), ".ppl", "cache/python")

def default_cache_root():
    return os.path.join(Path.home(), ".ppl", "cache")

def get_folder_size(folder):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

class CacheManager(ABC):
    def __init__(self, key):
        pass

    @abstractmethod
    def get_file(self, filename) -> Optional[str]:
        pass

    @abstractmethod
    def has_file(self, filename) -> bool:
        pass

    @abstractmethod
    def put(self, data, filename, binary=True) -> str:
        pass

    @abstractmethod
    def get_group(self, filename: str) -> Optional[Dict[str, str]]:
        pass

    @abstractmethod
    def put_group(self, filename: str, group: Dict[str, str]):
        pass


class FileCacheManager(CacheManager):
    def __init__(self, key):
        self.key = key
        self.lock_path = None
        # create cache directory if it doesn't exist
        self.cache_dir = os.environ.get('PPL_CACHE_PATH', default_cache_dir())
        if self.cache_dir:
            self.cache_dir = os.path.join(self.cache_dir, self.key)
            self.lock_path = os.path.join(self.cache_dir, "lock")
            os.makedirs(self.cache_dir, exist_ok=True)

    def get_cache_dir(self) -> str:
        return self.cache_dir

    def _make_path(self, filename) -> str:
        return os.path.join(self.cache_dir, filename)

    def has_file(self, filename):
        if not self.cache_dir:
            return False
        return os.path.exists(self._make_path(filename))

    def get_file(self, filename) -> Optional[str]:
        if self.has_file(filename):
            return self._make_path(filename)
        else:
            return None

    def get_group(self, filename: str) -> Optional[Dict[str, str]]:
        grp_filename = f"__grp__{filename}"
        if not self.has_file(grp_filename):
            return None
        grp_filepath = self._make_path(grp_filename)
        with open(grp_filepath) as f:
            grp_data = json.load(f)
        child_paths = grp_data.get("child_paths", None)
        # Invalid group data.
        if child_paths is None:
            return None
        result = {}
        for c in child_paths:
            p = self._make_path(c)
            if not os.path.exists(p):
                raise Exception(f"Group file {p} does not exist from group {grp_filename} ")
            result[c] = p
        return result

    # Note a group of pushed files as being part of a group
    def put_group(self, filename: str, group: Dict[str, str]):
        if not self.cache_dir:
            return
        grp_contents = json.dumps({"child_paths": sorted(list(group.keys()))})
        grp_filename = f"__grp__{filename}"
        return self.put(grp_contents, grp_filename, binary=False)

    def put(self, data, filename, binary=True) -> str:
        if not self.cache_dir:
            return
        binary = isinstance(data, bytes)
        if not binary:
            data = str(data)
        assert self.lock_path is not None
        filepath = self._make_path(filename)
        # Random ID to avoid any collisions
        rnd_id = random.randint(0, 1000000)
        # we use the PID incase a bunch of these around so we can see what PID made it
        pid = os.getpid()
        # use tempfile to be robust against program interruptions
        temp_path = f"{filepath}.tmp.pid_{pid}_{rnd_id}"
        mode = "wb" if binary else "w"
        with open(temp_path, mode) as f:
            f.write(data)
        # Replace is guaranteed to be atomic on POSIX systems if it succeeds
        # so filepath cannot see a partial write
        os.replace(temp_path, filepath)
        return filepath

    def handle(self, target_path, data_path, only_emit_kernel):
        if not os.path.exists(data_path):
            return
        if os.path.exists(os.path.join(target_path, "data")):
            shutil.rmtree(os.path.join(target_path, "data"))
        if not only_emit_kernel:
            os.makedirs(os.path.join(target_path, "data"))
        if not os.path.exists(data_path):
            assert 0, "fatal error"

        for item in os.listdir(data_path):
            src_item = os.path.join(data_path, item)
            dest_item = os.path.join(os.path.join(target_path, "data"), item)
            shutil.copy(src_item, dest_item)
        shutil.rmtree(data_path)

    def store(self, target_path):
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        os.makedirs(target_path, exist_ok=True)
        cmd_str = "cp -rf %s/* %s/" % (self.cache_dir, target_path)
        os.system(cmd_str)
        cmd_str = "rm -rf %s/*.json" % (target_path)
        os.system(cmd_str)
        cmd_str = "rm -rf %s/build/*" % (target_path)
        os.system(cmd_str)

__cache_cls = FileCacheManager
__cache_cls_nme = "DEFAULT"


def get_cache_manager(key) -> CacheManager:
    import os

    user_cache_manager = os.environ.get("PPL_CACHE_MANAGER", None)
    global __cache_cls
    global __cache_cls_nme

    if user_cache_manager is not None and user_cache_manager != __cache_cls_nme:
        import importlib
        module_path, clz_nme = user_cache_manager.split(":")
        module = importlib.import_module(module_path)
        __cache_cls = getattr(module, clz_nme)
        __cache_cls_nme = user_cache_manager

    return __cache_cls(key)

class Cache:
    def __init__(self):
        self.cache = OrderedDict()

    def put(self, key, value):
        self.cache[key] = value

def get_folder_access_time(folder_path):
    try:
        return os.path.getatime(folder_path)
    except OSError:
        return None

def cachemanager(kernel):
    cache_dir = os.environ.get('PPL_CACHE_PATH', default_cache_dir())
    max_cache_item = os.environ.get('PPL_MAX_CACHE_ITEM', 1500)
    folders = [f for f in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, f))]
    folder_count = len(folders)
    folders_to_delete = []
    if folder_count > max_cache_item:
        cache = Cache()
        for folder_name in os.listdir(cache_dir):
            folder_path = os.path.join(cache_dir, folder_name)
            if os.path.isdir(folder_path):
                access_time = get_folder_access_time(folder_path)
                if access_time is not None:
                    cache.put(folder_path, access_time)

        def custom_sort(item):
            folder_name, access_time = item
            if folder_name == kernel.path:
                return (1, access_time)
            else:
                return (0, access_time)

        sorted_cache = sorted(cache.cache.items(), key=custom_sort)
        folders_to_delete = [folder for folder, _ in sorted_cache[:-max_cache_item]]
        for folder in folders_to_delete:
            shutil.rmtree(folder)
    return folders_to_delete

# class CppLRUCacheManager:
#   def __init__(self, capacity):
#       self.capacity = capacity
#       self.queue = collections.OrderedDict()
#   def get(self, key):
#       if key not in self.queue:
#           return -1
#       value = self.queue.pop(key)
#       self.queue[key] = value
#       return self.queue[key]

#   def put(self, key, value):
#       if key in self.queue:
#           self.queue.pop(key)
#       elif len(self.queue.items()) == self.capacity:
#           self.queue.popitem(last=False)
#       self.queue[key] = value

class Heap:
    def __init__(self, max_num, max_fsize=0):
        self.max_num = max_num
        self.max_fsize = max_fsize
        self.record_size = 0
        self.store = OrderedDict()

    def get(self, key, to_top=True):
        if key in self.store:
            if to_top:
                self.store.move_to_end(key)
            return self.store[key]
        return None

    def add(self, key, value, size=0):
        removed = []
        if key in self.store:
            self.store[key] = value
            self.store.move_to_end(key)
        else:
            self.record_size += size
            if len(self.store) >= self.max_num:
                k, v = self.store.popitem(last=False)
                removed.append(k)
                if self.max_fsize:
                    self.record_size -= v[-1]
            while self.record_size > self.max_fsize:
                assert len(self.store), f"max_fsize ({self.max_fsize}) is too small."
                k, v = self.store.popitem(last=False)
                removed.append(k)
                self.record_size -= v[-1]
            self.store[key] = value
        return removed

    def save(self, filename):
        with open(filename, 'w') as file:
            json.dump([[key] + value for key, value in self.store.items()], file)

    def load(self, filename):
        with open(filename, 'r') as file:
            items = json.load(file)
            for item in items:
                self.store[item[0]] = item[1:]
                self.record_size += item[-1]
            while len(self.store) > self.max_num:
                self.store.popitem(last=False)

    def update_fsize(self, key, size):
        self.record_size -= self.store[key][-1]
        self.store[key][-1] = size
        self.record_size += size

    def __repr__(self):
        return repr(self.store)

class LRUCache:
    def __init__(self, max_num=1000, max_size=1024, cache_folde=None):
        self.cache_root = os.environ.get('PPL_CACHE_PATH', default_cache_root())
        if cache_folde:
           self.cache_root = os.path.join(self.cache_root, cache_folde)
        if not os.path.exists(self.cache_root):
            os.makedirs(self.cache_root, exist_ok=True)
        self.func_cache = Heap(max_num)
        self.file_cache = Heap(max_num, max_size)
        self.hash = ''
        self.cache_file_flag= False
        cache_file = os.path.join(self.cache_root, ".cache")
        if os.path.exists(cache_file):
            self.file_cache.load(cache_file)
        atexit.register(self._save_cache)

    def get_cached_file(self, file):
        if not self.cache_file_flag:
            assert 0, f"pass cache_fn to register first"
        file_path = os.path.join(self.cache_root, self.hash, file)
        if os.path.exists(file_path):
            v = self.file_cache.get(self.hash, False)
            if v:
                files = v[0]
                if file not in files:
                    files.append(file)
                return file_path
        assert 0, f"{file_path} not exists check registed cache_fn manner"
        return None

    def check_cached_file(self, time_stamp):
        info = self.file_cache.get(self.hash)
        if info:
            files, time, _ = info
            if time_stamp != time or len(files) == 0:
                return False
            for f in files:
                if not os.path.exists(os.path.join(self.cache_root, self.hash, f)):
                    return False
            return True
        return False

    def register(self, idx=1, cache_fn=None):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.cache_file_flag = True if cache_fn else False
                has_fcache = True
                if self.cache_file_flag:
                    file_path = args[idx]
                    file_cache_key = f"{str(args)}-{str(kwargs)}"
                    self.hash = hashlib.md5(file_cache_key.encode("utf-8")).hexdigest()
                    time_stamp = []
                    for src in file_path:
                        time_stamp.append(os.path.getmtime(src))
                # Update the file_cache even if the func_cache exists
                has_fcache = self.check_cached_file(time_stamp)
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                result = self.func_cache.get(cache_key)
                if result:
                    return result
                added_file_key = None
                build_debug = False
                extra_cflags = args[3] if len(args) > 3 else kwargs.get('extra_cflags', [])
                extra_plflags = args[4] if len(args) > 4 else kwargs.get('extra_plflags', [])
                if '-g' in extra_cflags or '-g' in extra_plflags:
                    build_debug = True
                if not has_fcache:
                    work_path = os.path.join(self.cache_root, self.hash)
                    cache_fn(work_path, build_debug, *args, **kwargs)
                    fsize_mb = get_folder_size(work_path) / (1024 * 1024)
                    # Remove infrequently used folders when the limit is exceeded
                    removed = self.file_cache.add(self.hash, [[], time_stamp, fsize_mb], fsize_mb)
                    for folder in removed:
                        folder = os.path.join(self.cache_root, folder)
                        if os.path.exists(folder):
                            shutil.rmtree(folder)
                    added_file_key = self.hash
                result = func(*args, **kwargs)
                self.func_cache.add(cache_key, result)
                # remove unrecored files
                if added_file_key and not build_debug:
                    self._clean_workdir(added_file_key)
                return result
            return wrapper
        return decorator

    def get_work_path(self):
        return os.path.join(self.cache_root, self.hash)

    def _clean_workdir(self, folder):
        path = os.path.join(self.cache_root, folder)
        keep_files = [os.path.join(path, f) for f in self.file_cache.get(folder, False)[0]]
        for root, dirs, files in os.walk(path, topdown=True):
            if root in keep_files:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in keep_files:
                    os.remove(file_path)
        self.file_cache.update_fsize(folder, get_folder_size(path) / (1024 * 1024))

    def _save_cache(self):
        if self.cache_file_flag:
            self.file_cache.save(os.path.join(self.cache_root, ".cache"))

    def __repr__(self):
        output = ""
        output = "\033[32m===============LRUCache status===============\033[0m\n"
        output += f"cache root: {self.cache_root}\n"
        output += "cache:\n"
        for idx, (key, value) in enumerate(reversed(self.file_cache.store.items())):
            files, timestamp, size_mb = value
            date_time = datetime.datetime.fromtimestamp(timestamp)
            output += f"{idx}\n"
            output += f"- folder: {key}\n"
            output += f"  cached files: {', '.join(files)}\n"
            output += f"  creation time: {date_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"  size: {size_mb:.2f} MB\n"
        return output
