#!/usr/bin/env python3
"""Claude Code status line for the context-hygiene system.

Reads the status-line JSON on stdin and prints one line:
    [Model] ⎇ branch │ ctx NN% │ $C.CC │ <current task>
The context segment is color-coded (green < YELLOW ≤ yellow < RED ≤ red) and a
"⚠ /handoff" nudge is appended once it's red — the human's cue to checkpoint,
since the model itself cannot read its context level.

Input (Claude Code statusLine, stdin JSON): uses model.display_name,
workspace.{git_worktree,current_dir}, context_window.used_percentage,
cost.total_cost_usd, plus <cwd>/.claude/current-task.txt for the task label.

Must never error or hang — a failed status line just shows nothing useful, so
every field is defensively defaulted and any exception yields a minimal line.
"""
import json
import os
import sys

YELLOW = 50   # ctx % at/above which the meter turns yellow
RED = 75      # ctx % at/above which it turns red + nudges /handoff

C = {"green": "\033[32m", "yellow": "\033[33m", "red": "\033[31m",
     "dim": "\033[2m", "reset": "\033[0m"}


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("")            # never error the status line
        return

    def g(obj, *path, default=None):
        for k in path:
            if not isinstance(obj, dict):
                return default
            obj = obj.get(k)
        return obj if obj is not None else default

    model = g(data, "model", "display_name", default="Claude")
    ws = data.get("workspace", {}) if isinstance(data.get("workspace"), dict) else {}
    where = ws.get("git_worktree") or os.path.basename(
        ws.get("current_dir") or data.get("cwd") or "")
    pct = g(data, "context_window", "used_percentage", default=None)
    cost = g(data, "cost", "total_cost_usd", default=None)

    parts = [f"{C['dim']}[{model}]{C['reset']}"]
    if where:
        parts.append(f"⎇ {where}")

    if isinstance(pct, (int, float)):
        p = int(round(pct))
        col = C["red"] if p >= RED else C["yellow"] if p >= YELLOW else C["green"]
        seg = f"{col}ctx {p}%{C['reset']}"
        if p >= RED:
            seg += f"{C['red']} ⚠ /handoff{C['reset']}"
        parts.append(seg)

    if isinstance(cost, (int, float)) and cost > 0:
        parts.append(f"{C['dim']}${cost:.2f}{C['reset']}")

    cwd = ws.get("current_dir") or data.get("cwd") or "."
    task_file = os.path.join(cwd, ".claude", "current-task.txt")
    try:
        with open(task_file) as f:
            task = f.readline().strip()
        if task:
            parts.append(f"{C['dim']}· {task[:60]}{C['reset']}")
    except OSError:
        pass

    print(" │ ".join(parts))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("")            # last-resort: a status line must not crash the UI
