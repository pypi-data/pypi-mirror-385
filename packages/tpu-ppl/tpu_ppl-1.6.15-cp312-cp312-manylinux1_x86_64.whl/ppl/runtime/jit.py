from __future__ import annotations, division

import ast
import functools
import hashlib
import inspect
import os
import subprocess
import textwrap
import numpy as np
import torch
from collections import defaultdict, namedtuple
from functools import cached_property, wraps
from typing import (Callable, Generic, Iterable, List, Optional, TypeVar, Union, cast,
                    overload)
from .cache import get_cache_manager

from pathlib import Path
import shutil
PPL_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PPL_VERSION = "2.1.0"

T = TypeVar('T')

# -----------------------------------------------------------------------------
# Dependencies Finder
# -----------------------------------------------------------------------------


class DependenciesFinder(ast.NodeVisitor):
    """
    This AST visitor is used to find dependencies of a JITFunction. This can
    be used to invalidate a JITFunction's hash when its source code -- or
    that of its dependencies -- changes.
    """

    def __init__(self, globals, src) -> None:
        super().__init__()
        self.ret = hashlib.md5(src.encode("utf-8")).hexdigest()
        self.globals = globals

    def visit_Name(self, node):
        return self.globals.get(node.id, None)

    def visit_Attribute(self, node):
        lhs = self.visit(node.value)
        while isinstance(lhs, ast.Attribute):
            lhs = self.visit(lhs.value)
        if lhs is None or (getattr(lhs, "__name__", "") == "ppl" or getattr(lhs, "__name__", "").endswith(".ppl")):
            return None
        return getattr(lhs, node.attr)

    def visit_Call(self, node):
        func = self.visit(node.func)
        if func is None:
            return
        if inspect.isbuiltin(func):
            return
        if func.__module__ and (func.__module__.startswith('ppl.') or '.ppl.' in func.__module__):
            return
        assert isinstance(func, JITFunction), f"Function \"{func.__name__}\" is being called from a Ppl function but is not a Ppl function itself. Decorate it with @ppl.jit to fix this"
        if func.hash is None:
            tree = ast.parse(func.src)
            finder = DependenciesFinder(func.__globals__, func.src)
            finder.visit(tree)
            func.hash = finder.ret
        noinline = str(getattr(func, 'noinline', False))
        self.ret = (self.ret + func.hash + noinline).encode("utf-8")
        self.ret = hashlib.md5(self.ret).hexdigest()

# -----------------------------------------------------------------------------
# JITFunction
# -----------------------------------------------------------------------------


@functools.lru_cache()
def version_key():
    import pkgutil
    contents = []
    # frontend
    with open(__file__, "rb") as f:
        contents += [hashlib.md5(f.read()).hexdigest()]
    # compiler
    compiler_path = os.path.join(PPL_PATH, 'compiler')
    for lib in pkgutil.iter_modules([compiler_path]):
        with open(lib.module_finder.find_spec(lib.name).origin, "rb") as f:
            contents += [hashlib.md5(f.read()).hexdigest()]
    # backend
    with open(os.path.join(PPL_PATH, "_C/libppl.so"), "rb") as f:
        contents += [hashlib.md5(f.read()).hexdigest()]
    # language
    language_path = os.path.join(PPL_PATH, 'language')
    for lib in pkgutil.iter_modules([language_path]):
        with open(lib.module_finder.find_spec(lib.name).origin, "rb") as f:
            contents += [hashlib.md5(f.read()).hexdigest()]
    # ppl version
    return '-'.join(PPL_VERSION) + '-' + '-'.join(contents)


def _normalize_ty(ty) -> str:
    if isinstance(ty, type):
        return ty.__name__
    elif isinstance(ty, str):
        return ty
    return repr(ty)

class KernelParam:
    """Represents a parameter to a @jit'ed function.

    A parameter is just the name plus metadata; a parameter plus a value is a
    KernelArg.
    """

    def __init__(self, num: int, param: inspect.Parameter, do_not_specialize: bool):
        self.num = num
        self._param = param
        self.do_not_specialize = do_not_specialize

    @cached_property
    def name(self):
        return self._param.name

    @cached_property
    def annotation(self):
        if not self._param.annotation or self._param.annotation == inspect.Parameter.empty:
            return ""
        return _normalize_ty(self._param.annotation)

    @cached_property
    def is_constexpr(self):
        return "constexpr" in self.annotation

    @property
    def default(self):
        return self._param.default

    @property
    def has_default(self):
        return self._param.default != inspect.Parameter.empty


class KernelArg:
    """Represents an argument to a @jit'ed function.

    An argument is a parameter plus a value.
    """

    def __init__(self, value, param):
        self.value = value
        self.param = param

    @property
    def name(self):
        return self.param.name

    def signature_key(self):
        annotation = self.param.annotation
        if "Tensor" in annotation:
            return self.value.dtype
        elif annotation == "bool":
            return "i1"
        elif annotation == "float":
            return "fp32"
        else:
            return JITFunction._key_of(self.value)

    def specialization_key(self):
        assert not self.param.do_not_specialize

        try:
            return (self.value.data_ptr() % JITFunction.divisibility == 0, )
        except AttributeError:
            pass

        if isinstance(self.value, int):
            # bool is a subclass of int, so we don't check explicitly above.
            return (
                self.value % JITFunction.divisibility == 0,
                self.value % JITFunction.divisibility_8 == 0,
                self.value == 1,
            )

        return (False, )

class KernelInterface(Generic[T]):
    run: T

    def __getitem__(self, grid) -> T:
        """
        A JIT function is launched with: fn[grid](*args, **kwargs).
        Hence JITFunction.__getitem__ returns a callable proxy that
        memorizes the grid.
        """
        return cast(T, functools.partial(cast(Callable, self.run), grid=grid))


class JITFunction(KernelInterface[T]):

    # Hook for inspecting compiled functions and modules
    cache_hook = None
    divisibility = 16
    divisibility_8 = 8
    @staticmethod
    def _key_of(arg):
        def _all_elements_same_type(arr):
            if not arr:
                return True
            first_type = type(arr[0])
            return all(isinstance(x, first_type) for x in arr)
        if hasattr(arg, "dtype"):
            return arg.dtype
        elif isinstance(arg, bool):
            return "i1"
        elif isinstance(arg, int):
            if -2**31 <= arg and arg <= 2**31 - 1:
                return "i32"
            elif 2**63 <= arg and arg <= 2**64 - 1:
                return "u64"
            else:
                return "i64"
        elif isinstance(arg, float):
            return 'fp32'
        elif arg is None:
            return None
        elif isinstance(arg, tuple):
            if _all_elements_same_type(arg):
                if len(arg) == 0:
                    raise TypeError(f'Empty tuple is not supported')
                return 'tuple_' + JITFunction._key_of(arg[0]) + '_' + str(len(arg))
            else:
                raise TypeError(f'All elements of input {type(arg)}: {arg} should keep in same type')
        else:
            raise TypeError(f'Unsupported type {type(arg)} for {arg}')

    def _get_config(self, non_const_index, *args):
        def is_divisible_by_16(x):
            if hasattr(x, "data_ptr"):
                return x.data_ptr() % JITFunction.divisibility == 0
            elif isinstance(x, int):
                return x % JITFunction.divisibility == 0
            if x is None:
                return True
            return False
        divisible_by_16 = {i for i, arg in enumerate(args) if is_divisible_by_16(arg) and i not in self.do_not_specialize}
        equal_to_1 = {i for i, arg in enumerate(args) if not isinstance(arg, bool) and isinstance(arg, int) and arg == 1 and i not in non_const_index and i not in self.do_not_specialize}
        return namedtuple("instance_descriptor", ["divisible_by_16", "equal_to_1"])(tuple(divisible_by_16), tuple(equal_to_1))
        # return _ppl.code_gen.instance_descriptor(divisible_by_16, equal_to_1)

    @staticmethod
    def _type_of(key):
        # None are nullptr -- implicitly converted to *i8
        if key is None:
            return '*i8'
        dtype_str = str(key).split(".")[-1]
        tys = {
            "bool": "i1",
            "float8e4": "fp8e4",
            "float8e5": "fp8e5",
            "float8e4b15": "fp8e4b15",
            "float16": "fp16",
            "bfloat16": "bf16",
            "float32": "fp32",
            "float64": "fp64",
            "int8": "i8",
            "int16": "i16",
            "int32": "i32",
            "int64": "i64",
            "uint8": "u8",
            "uint16": "u16",
            "uint32": "u32",
            "uint64": "u64",
        }
        # reinterpret can create ppl type
        for v in list(tys.values()):
            tys[v] = v
        return key if isinstance(key, str) else f"*{tys[dtype_str]}"

    def _make_signature(self, sig_key):
        signature = ",".join([self._type_of(k) for i, k in enumerate(sig_key)])
        return signature

    def _make_constants(self, constexpr_key):
        constants = dict(zip(self.constexprs, constexpr_key))
        return constants

    def _call_hook(self, key, signature, device, constants, num_warps, num_stages, extern_libs, configs):
        if JITFunction.cache_hook is None:
            return False
        name = self.fn.__name__
        module = self.fn.__module__
        arg_reprs = ', '.join([f'{name}: {ty}' for name, ty in zip(self.arg_names, key[1])])
        repr = f"{name}[num_warps={num_warps}, num_stages={num_stages}]({arg_reprs})"
        key = str(key)

        class LegacyCompiler:
            def __init__(self, module, name):
                self.module = module
                self.name = name
                pass

        kwargs = dict(signature=signature, device=device, constants=constants,
                      num_warps=num_warps, num_stages=num_stages, extern_libs=extern_libs,
                      configs=configs)

        return JITFunction.cache_hook(key=key, repr=repr, fn=LegacyCompiler(module, name), compile={"key": key, **kwargs}, is_manual_warmup=False, already_compiled=False)

    @functools.lru_cache()
    def run(self, *args_, **kwargs):
        # Get a compiler-flags arg like `num_warps` and remove it from kwargs.
        def get_special_arg(name: str, default=None):
            if name not in kwargs:
                return default
            ret = kwargs[name]
            del kwargs[name]
            return ret

        grid = get_special_arg("grid")
        device = "tpu"
        # Bind the remaining arguments to `fn`.
        only_emit_kernel = any(isinstance(value, torch.Tensor) and not value.is_cpu for value in args_)
        bound_args = self.signature.bind(*args_, **kwargs)
        bound_args.apply_defaults()

        assert len(bound_args.arguments) == len(self.params)
        args = [KernelArg(arg_value, param) for (_, arg_value), param in zip(bound_args.arguments.items(), self.params)]

        sig_key = tuple(arg.signature_key() for arg in args if not arg.param.is_constexpr)
        #spec_key = tuple(arg.specialization_key() for arg in args if not arg.param.do_not_specialize)
        constexpr_key_list = [arg.value for arg in args if arg.param.is_constexpr]

        constexpr_key = tuple(constexpr_key_list)
        assert grid is not None
        if callable(grid):
            # Arguments are passed as a dict to `grid`, by contract.
            # TODO(jlebar): In the new launch API, pass the compiler flags as a
            # second parameter to `grid`.
            grid = grid(dict(bound_args.arguments))
        grid_size = len(grid)
        grid_0 = grid[0]
        grid_1 = grid[1] if grid_size > 1 else 1
        grid_2 = grid[2] if grid_size > 2 else 1

        key = (
            self.fn.__name__,
            sig_key,
            constexpr_key,
            #spec_key,
            self.debug,
            self.mode,
            grid_size,
            grid_0,
            grid_1,
            grid_2
        )

        kernel = self.cache.get(key, None)
        hash = None
        signature = None
        constants = None
        # for test mode
        if kernel is None or not only_emit_kernel:
            # Build kernel signature -- doesn't include constexpr arguments.
            signature = {
                arg.param.num: self._type_of(self._key_of(arg.value))
                for arg in args
                if not arg.param.is_constexpr
            }
            # TODO: It's not clear under what circumstances signature will be str.
            # Maybe it's not needed here
            if isinstance(signature, str):
                signature = {
                    k: v.strip()
                    for k, v in enumerate(signature.split(","))
                }
            constants = {
                arg.param.num: arg.value
                for arg in args
                if arg.param.is_constexpr
            }
            for i, arg in constants.items():
                if callable(arg):
                    raise TypeError(f"Callable constexpr at index {i} is not supported")
            arch = os.getenv("CHIP", default="bm1684x")
            hash_content = f"{self.fn.__name__}-{self.src}-{''.join(signature.values())}-{constants}-{self.debug}-{self.mode}-{arch}-{grid_size}-{grid_0}-{grid_1}-{grid_2}"
            hash = hashlib.md5(hash_content.encode("utf-8")).hexdigest()

        if not only_emit_kernel:
            fn_cache_manager = get_cache_manager(hash)
            cache_dir = fn_cache_manager.get_cache_dir()
            print(f"{self.fn.__name__} cache dir is {cache_dir}")
            data_dir = os.path.join(cache_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            rst_file = open(os.path.join(data_dir, "param.txt"), 'w')
            non_constexpr_arg_values = [arg.value for arg in args if not arg.param.is_constexpr]
            non_constexpr_arg_names = [arg.name for arg in args if not arg.param.is_constexpr]
            for index, (tensor, name) in enumerate(zip(non_constexpr_arg_values, non_constexpr_arg_names)):
                if isinstance(tensor, torch.Tensor):
                    assert tensor.is_cpu
                    dic = {}
                    #numpy don't support bf16
                    npz_name = name + ".npz"
                    if tensor.dtype == torch.bfloat16:
                        dic["0"] = tensor.float().numpy()
                    else:
                        dic["0"] = tensor.numpy()
                    rst_file.write(npz_name+"\n")
                    np.savez(os.path.join(data_dir, npz_name), **dic)
                else:
                    if tensor is None:
                        npz_name = name + ".npz"
                        dic = {}
                        dic["0"] = 0
                        np.savez(os.path.join(data_dir, npz_name), **dic)
                        rst_file.write(npz_name+"\n")
                    elif isinstance(tensor, bool):
                        rst_file.write(f"{int(tensor)}\n")
                    elif isinstance(tensor, tuple):
                        rst_file.write(",".join([str(x) for x in tensor])+"\n")
                    else:
                        rst_file.write(f"{tensor}\n")
            rst_file.close()

        # Kernel is not cached; we have to compile.
        if kernel is None:
            from ..compiler import compile
            constexpr_index = [index for index, arg in enumerate(args) if arg.param.is_constexpr]
            non_const_index = {
                arg.param.num
                for arg in args
                if not arg.param.is_constexpr
            }
            configs = (self._get_config(non_const_index, *[arg.value for arg in args]), )

            kernel = compile(
                self,
                signature=signature,
                sig_key=sig_key,
                constants=constants,
                configs=configs,
                debug=self.debug,
                mode=self.mode,
                save_dir=self.save_dir,
                only_emit_kernel=only_emit_kernel,
                constexpr_index=constexpr_index,
                grid_size = grid_size,
                grid_0 = grid_0,
                grid_1 = grid_1,
                grid_2 = grid_2,
                hash = hash
                )
            self.cache[key] = kernel
            self.kernel = kernel
            from .cache import cachemanager
            folders_to_delete = cachemanager(kernel)
            for folder in folders_to_delete:
                to_delete = [key for key, value in self.cache[device].items() if value.path == folder]
                for key in to_delete:
                    del self.cache[device][key]

        if not only_emit_kernel:
            if kernel.errorCode:
                print("[ERROR] generator kernel failed")
            else:
                kernel.run(kernel.path, kernel.arch, kernel.function_name, kernel.mode, kernel.only_emit_kernel, self.debug, kernel.desc)
                new_data = np.load(os.environ["PPL_DATA_PATH"]+"/" + self.fn.__name__+"_tar.npz")
                tensor_idx = -1
                #copy result data to output
                for index, arg in enumerate(args_):
                    if isinstance(arg, torch.Tensor) or arg is None:
                        tensor_idx += 1
                        if isinstance(arg, torch.Tensor) and arg.is_cpu:
                            args_[index].data = torch.from_numpy(new_data[str(tensor_idx)]).to(arg.dtype).data.view(args_[index].data.shape)
        return kernel

    def __init__(self, fn, version=None, do_not_specialize=None, debug=None, noinline=None):
        self.fn = fn
        self.module = fn.__module__
        self.version = version
        self.do_not_specialize = do_not_specialize
        self.starting_line_number = inspect.getsourcelines(fn)[1]
        self.signature = inspect.signature(fn)
        self.params = []
        for i, param in enumerate(self.signature.parameters.values()):
            dns = do_not_specialize and (i in do_not_specialize or param.name in do_not_specialize)
            self.params.append(KernelParam(i, param, dns))
        # function signature information
        self.arg_names = [v.name for v in self.signature.parameters.values()]
        self.arg_defaults = [v.default for v in self.signature.parameters.values()]
        self.has_defaults = any(v != inspect._empty for v in self.arg_defaults)
        # specialization hints
        self.do_not_specialize = [] if do_not_specialize is None else do_not_specialize
        self.do_not_specialize = {self.arg_names.index(arg) if isinstance(arg, str) else arg for arg in self.do_not_specialize}
        # function source code (without decorators)
        self.src = textwrap.dedent(inspect.getsource(fn))
        self.src = self.src[self.src.find("def"):]
        # cache of just-in-time compiled kernels
        self.cache = {}
        self.hash = None
        # JITFunction can be instantiated as kernel
        # when called with a grid using __getitem__
        self.kernel_decorators = []
        self.kernel = None
        self.debug = True if debug is not None and(debug == 1 or debug == True) else False
        self.mode = os.environ.get("MODE", "cmodel")
        self.save_dir = os.environ.get("SAVE_DIR", None)
        self.noinline = noinline
        # annotations
        self.__annotations__ = {name: _normalize_ty(ty) for name, ty in fn.__annotations__.items()}
        # index of constexprs
        self.constexprs = [self.arg_names.index(name) for name, ty in self.__annotations__.items() if 'constexpr' in ty]

        # re-use docs of wrapped function
        self.__doc__ = fn.__doc__
        self.__name__ = fn.__name__
        self.__globals__ = fn.__globals__
        self.__module__ = fn.__module__

    @property
    def cache_key(self):
        # TODO : hash should be attribute of `self`
        if self.hash is None:
            dependencies_finder = DependenciesFinder(globals=self.__globals__, src=self.src)
            dependencies_finder.visit(self.parse())
            self.hash = dependencies_finder.ret + version_key()
        return self.hash

    def warmup(self, *args, **kwargs):
        return self.run(*map(MockTensor.wrap_dtype, args), **kwargs, warmup=True)

    # we do not parse `src` in the constructor because
    # the user might want to monkey-patch self.src dynamically.
    # Our unit tests do this, for example.
    def parse(self):
        tree = ast.parse(self.src)
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.FunctionDef)
        return tree

    def __call__(self, *args, **kwargs):
        raise RuntimeError("Cannot call @ppl.jit'd outside of the scope of a kernel")

    def __setattr__(self, name, value):
        # - when kernel decorators change, cached kernel
        #   needs to be cleared
        if name == 'kernel_decorators':
            self.kernel = None
        super(JITFunction, self).__setattr__(name, value)
        # - when `.src` attribute is set, cache path needs
        #   to be reinitialized
        if name == 'src':
            self.hash = None

    def __repr__(self):
        return f"JITFunction({self.module}:{self.fn.__name__})"


# -----------------------------------------------------------------------------
# `jit` decorator
# -----------------------------------------------------------------------------


class TilingWrap(KernelInterface):
    def __init__(self, tiling_func, fn):
        self.fn = fn
        self.tiling_func = tiling_func
        self.hash = {}

    def run(self, *args, **kwargs):
        def get_special_arg(name: str, default=None):
            if name not in kwargs:
                return default
            return kwargs[name]

        grid = get_special_arg("grid")
        const_val = tuple(args[i] for i in range(len(args)) if i in self.fn.constexprs)
        key = (
            self.fn.__name__,
            self.fn.mode,
            self.fn.debug,
            grid,
            const_val
        )
        if key in self.hash:
            return self.hash[key]
        fn_wrap = lambda *x : self.fn.run(*x, **kwargs)
        ret = self.tiling_func(fn_wrap, *args)
        self.hash[key] = ret
        return ret

@overload
def jit(fn: T) -> JITFunction[T]:
    ...


@overload
def jit(
    *,
    version=None,
    do_not_specialize: Optional[Iterable[int]] = None,
    debug: Optional[bool] = None,
    noinline: Optional[bool] = None,
) -> Callable[[T], JITFunction[T]]:
    ...


def jit(
    fn: Optional[T] = None,
    *,
    version=None,
    do_not_specialize: Optional[Iterable[int]] = None,
    tiling: Optional[Callable] = None,
    debug: Optional[bool] = None,
    noinline: Optional[bool] = None,
    interpret: Optional[bool] = None,
) -> Union[JITFunction[T], Callable[[T], JITFunction[T]]]:
    """
    Decorator for JIT-compiling a function using the Ppl compiler.

    :note: When a jit'd function is called, arguments are
        implicitly converted to pointers if they have a :code:`.data_ptr()` method
        and a `.dtype` attribute.

    :note: This function will be compiled and run on the GPU. It will only have access to:

           * python primitives,
           * builtins within the ppl package,
           * arguments to this function,
           * other jit'd functions

    :param fn: the function to be jit-compiled
    :type fn: Callable
    """

    def decorator(fn: T) -> JITFunction[T]:
        assert callable(fn)
        if interpret:
            from ..interpreter.interpreter import GridSelector
            return GridSelector(fn)
        else:
            jitFunc = JITFunction(
                fn,
                version=version,
                do_not_specialize=do_not_specialize,
                debug=debug,
                noinline=noinline,
            )
            if tiling is not None:
                return TilingWrap(tiling, jitFunc)
            else:
                return jitFunc
    if fn is not None:
        ret = decorator(fn)
        return ret

    else:
        return decorator

# -----------------------------------------------------------------------------
# Utilities for mocking tensors
# -----------------------------------------------------------------------------


class MockTensor:
    """
    Can be used in place of real tensors when calling:
        kernel.warmup(MockTensor(torch.float32), ...)
    """
    @staticmethod
    def wrap_dtype(arg):
        if arg.__class__.__name__ == "dtype" and\
           arg.__module__ == "torch":
            return MockTensor(arg)
        return arg

    def __init__(self, dtype):
        self.dtype = dtype

    @staticmethod
    def data_ptr():
        return 0  # optimistically assumes multiple of 16

class AutoTiling(KernelInterface):
    def __init__(self, fn, arg_names,values):
        self.fn = fn
        self.arg_names = arg_names
        self.values = values
        self.hash = {}

    def run(self, *args, **kwargs):
        def get_special_arg(name: str, default=None):
            if name not in kwargs:
                return default
            return kwargs[name]

        grid = get_special_arg("grid")
        const_val = tuple(args[i] for i in range(len(args)) if i in self.fn.constexprs)
        key = (
            self.fn.__name__,
            self.fn.mode,
            self.fn.debug,
            grid,
            const_val
        )
        if key in self.hash:
            return self.hash[key]
        else:
            while True:
                ret = self.fn.run(*args, **kwargs)
                if not ret is None and ret.errorCode == 0:
                    self.hash[key] = ret
                    return ret
                else:
                    nargs = dict(zip(self.arg_names, args))
                    for v, heur in self.values.items():
                        if v in nargs:
                            nargs[v] = heur({**dict(zip(self.arg_names, args)), **kwargs})
                    args = tuple(nargs.values())

def autotiling(values):
    def decorator(fn):
        return AutoTiling(fn, fn.arg_names, values)
    return decorator
