import os
import shlex
import subprocess
import psutil
import shutil
from base64 import b64decode

class CommandProcessor:
    def __init__(self):
        self.history = []

    def parse_and_execute(self, line):
        try:
            line = line.strip()
            if not line:
                return ""
            self.history.append(line)

            tokens = shlex.split(line)
            cmd = tokens[0]
            args = tokens[1:]

            # ------------------
            # BASIC FILE/DIR OPERATIONS
            # ------------------
            if cmd == "pwd":
                return os.getcwd()
            elif cmd == "ls":
                path = args[-1] if args else "."
                if not os.path.exists(path):
                    return f"ls: cannot access '{path}': No such file or directory"
                return "\n".join(sorted(os.listdir(path)))
            elif cmd == "cd":
                if not args:
                    return "cd: missing operand"
                try:
                    os.chdir(args[0])
                    return f"Changed directory to {os.getcwd()}"
                except Exception as e:
                    return f"cd: {str(e)}"
            elif cmd == "mkdir":
                if not args:
                    return "mkdir: missing operand"
                path = args[0]
                os.makedirs(path, exist_ok=True)
                return f"Created directory {path}"
            elif cmd == "rmdir":
                if not args:
                    return "rmdir: missing operand"
                try:
                    os.rmdir(args[0])
                    return f"Removed directory {args[0]}"
                except Exception as e:
                    return f"rmdir: {str(e)}"
            elif cmd == "touch":
                if not args:
                    return "touch: missing operand"
                open(args[0], "a").close()
                return f"Created file {args[0]}"
            elif cmd == "rm":
                if not args:
                    return "rm: missing operand"
                target = args[-1]
                try:
                    if os.path.isdir(target):
                        shutil.rmtree(target)
                    else:
                        os.remove(target)
                    return f"Removed {target}"
                except Exception as e:
                    return f"rm: {str(e)}"
            elif cmd == "cp":
                if len(args) < 2:
                    return "cp: missing operand"
                src, dest = args[0], args[1]
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dest)
                    return f"Copied {src} -> {dest}"
                except Exception as e:
                    return f"cp: {str(e)}"
            elif cmd == "mv":
                if len(args) < 2:
                    return "mv: missing operand"
                src, dest = args[0], args[1]
                try:
                    shutil.move(src, dest)
                    return f"Moved {src} -> {dest}"
                except Exception as e:
                    return f"mv: {str(e)}"
            elif cmd == "rename":
                if len(args) < 2:
                    return "rename: missing operand"
                try:
                    os.rename(args[0], args[1])
                    return f"Renamed {args[0]} -> {args[1]}"
                except Exception as e:
                    return f"rename: {str(e)}"

            # ------------------
            # FILE VIEWING / EDITING
            # ------------------
            elif cmd == "cat":
                if not args:
                    return "cat: missing operand"
                filename = args[0]
                try:
                    with open(filename, "r") as f:
                        return f.read()
                except FileNotFoundError:
                    return f"cat: {filename}: No such file"
                except Exception as e:
                    return f"cat: {str(e)}"

            elif cmd == "vim":
                if not args:
                    return "vim: missing file name"
                filename = args[0]
                if not os.path.exists(filename):
                    open(filename, "a").close()
                with open(filename, "r") as f:
                    content = f.read()
                return f"__OPEN_EDITOR__::{filename}::{content}"

            elif cmd == "__save__":
                if len(args) < 2:
                    return "Error: Invalid save command"
                filename = args[0]
                decoded_content = b64decode(" ".join(args[1:])).decode("utf-8")
                with open(filename, "w") as f:
                    f.write(decoded_content)
                return f"Saved file {filename}"

            elif cmd == "chmod":
                if len(args) < 2:
                    return "chmod: missing operand"
                try:
                    mode = int(args[0], 8)
                    os.chmod(args[1], mode)
                    return f"Changed permissions of {args[1]} to {args[0]}"
                except Exception as e:
                    return f"chmod: {str(e)}"

            # ------------------
            # SYSTEM MONITORING
            # ------------------
            elif cmd == "cpu":
                return f"CPU Usage: {psutil.cpu_percent(interval=1)}%"
            elif cmd == "mem":
                mem = psutil.virtual_memory()
                return f"Memory Usage: {mem.percent}% ({mem.used//(1024**2)}MB / {mem.total//(1024**2)}MB)"
            elif cmd == "ps":
                processes = []
                for p in psutil.process_iter(['pid', 'name']):
                    processes.append(f"{p.info['pid']:>6}  {p.info['name']}")
                return "\n".join(processes[:15])

            # ------------------
            # OTHER UTILITIES
            # ------------------
            elif cmd == "history":
                return "\n".join(self.history[-20:])
            elif cmd == "clear":
                return "__CLEAR_SCREEN__"

            # FALLBACK
            else:
                res = subprocess.run(tokens, capture_output=True, text=True)
                return res.stdout or res.stderr

        except Exception as e:
            return f"Error: {str(e)}"
