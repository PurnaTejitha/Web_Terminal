import os, shlex, subprocess, shutil

class CommandProcessor:
    def parse_and_execute(self, line):
        tokens = shlex.split(line)
        cmd = tokens[0]
        args = tokens[1:]

        if cmd == "pwd":
            return os.getcwd()
        elif cmd == "ls":
            return "\n".join(os.listdir(args[0] if args else "."))
        elif cmd == "mkdir":
            os.makedirs(args[0], exist_ok=True)
            return f"Created {args[0]}"
        elif cmd == "rm":
            os.remove(args[0])
            return f"Removed {args[0]}"
        else:
            # fallback to external command
            res = subprocess.run(tokens, capture_output=True, text=True)
            return res.stdout or res.stderr

def main():
    cp = CommandProcessor()
    while True:
        try:
            line = input("pyterm> ")
            if line.strip() in ["exit", "quit"]:
                break
            output = cp.parse_and_execute(line)
            print(output)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
