"""
Structured terminal logger for pymiro dev mode.
"""

import sys


class DevLogger:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def _log(self, action: str, color_code: str, msg: str) -> None:
        if not self.enabled:
            return

        # Color codes:
        # cyan=36, yellow=33, blue=34, green=32, magenta=35, red=31
        # action is padded to 10 characters before coloring, wait.
        # Format: [pymiro] {action:10} {msg}
        padded_action = f"{action:<10}"
        colored_action = f"\033[{color_code}m{padded_action}\033[0m"
        print(f"  [pymiro] {colored_action} {msg}")
        sys.stdout.flush()

    def mount(self, component_name: str) -> None:
        self._log("mount", "36", component_name)

    def signal(self, name: str, old: object, new: object) -> None:
        self._log("signal", "33", f"{name}: {old} → {new}")

    def reconcile(self, patch_count: int) -> None:
        # e.g., "3 patches" or "1 patch"
        suffix = "patches" if patch_count != 1 else "patch"
        self._log("reconcile", "34", f"{patch_count} {suffix}")

    def commit(self, patch: object) -> None:
        # extract patch type name and affected node if possible
        # We can just use the class name
        name = patch.__class__.__name__
        # Assuming patch has node_id or parent_id, but the prompt just says "UpdateProps node_3"
        # We'll try to extract node_id or parent_id
        target = getattr(
            patch,
            "node_id",
            getattr(patch, "parent_id", getattr(patch, "new_parent_id", "")),
        )
        self._log("commit", "32", f"{name} {target}".strip())

    def reload(self, filename: str) -> None:
        self._log("reload", "35", filename)

    def error(self, msg: str) -> None:
        self._log("error", "31", msg)

    def warning(self, msg: str) -> None:
        self._log("warning", "33", msg)


__all__ = ["DevLogger"]
