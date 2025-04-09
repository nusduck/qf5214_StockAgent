import builtins
import contextlib
import io
import sys
from typing import Any




def eval(code: str, _locals: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    # Store original keys before execution
    original_keys = set(_locals.keys())

    try:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            exec(code, builtins.__dict__, _locals)
        result = f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
    except SystemExit as e:
        # 特别处理SystemExit异常，避免程序终止
        result = f"警告: 代码尝试使用exit()或sys.exit()退出程序: {repr(e)}"
        print(result)  # 记录到控制台
    except Exception as e:
        result = f"Error during execution: {repr(e)}"

    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    return result, new_vars

