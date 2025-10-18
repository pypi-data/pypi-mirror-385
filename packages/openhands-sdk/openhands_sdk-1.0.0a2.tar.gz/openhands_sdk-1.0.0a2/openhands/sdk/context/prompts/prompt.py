# prompt_utils.py
import os
import re
import sys
from functools import lru_cache

from jinja2 import Environment, FileSystemBytecodeCache, FileSystemLoader, Template


def refine(text: str) -> str:
    if sys.platform == "win32":
        text = re.sub(
            r"\bexecute_bash\b", "execute_powershell", text, flags=re.IGNORECASE
        )
        text = re.sub(
            r"(?<!execute_)(?<!_)\bbash\b", "powershell", text, flags=re.IGNORECASE
        )
    return text


@lru_cache(maxsize=64)
def _get_env(prompt_dir: str) -> Environment:
    if not prompt_dir:
        raise ValueError("prompt_dir is required")
    # BytecodeCache avoids reparsing templates across processes
    cache_folder = os.path.join(prompt_dir, ".jinja_cache")
    os.makedirs(cache_folder, exist_ok=True)
    bcc = FileSystemBytecodeCache(directory=cache_folder)
    env = Environment(
        loader=FileSystemLoader(prompt_dir),
        bytecode_cache=bcc,
        autoescape=False,
    )
    # Optional: expose refine as a filter so templates can use {{ text|refine }}
    env.filters["refine"] = refine
    return env


@lru_cache(maxsize=256)
def _get_template(prompt_dir: str, template_name: str) -> Template:
    env = _get_env(prompt_dir)
    try:
        return env.get_template(template_name)
    except Exception:
        raise FileNotFoundError(
            f"Prompt file {os.path.join(prompt_dir, template_name)} not found"
        )


def render_template(prompt_dir: str, template_name: str, **ctx) -> str:
    tpl = _get_template(prompt_dir, template_name)
    return refine(tpl.render(**ctx).strip())
