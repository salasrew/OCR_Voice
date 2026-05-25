from __future__ import annotations

import os
import subprocess
from typing import Any


def run_hidden(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
    if os.name == "nt" and "creationflags" not in kwargs:
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.run(command, **kwargs)
