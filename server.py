import os
import json
from flask import Flask, request, jsonify, render_template
from command_processor import CommandProcessor

# -----------------------------
# Load datasets
# -----------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT_DIR, "nl_to_command.json")) as f:
    nl_commands = json.load(f)

with open(os.path.join(ROOT_DIR, "command_suggestions.json")) as f:
    command_suggestions = json.load(f)

with open(os.path.join(ROOT_DIR, "command_manual.json")) as f:
    command_manual = json.load(f)

# -----------------------------
# Flask setup
# -----------------------------
template_path = os.path.join(ROOT_DIR, "web_ui", "templates")
app = Flask(__name__, template_folder=template_path)

cp = CommandProcessor()

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_command():
    data = request.json
    user_input = data.get("command", "").strip()

    if not user_input:
        return jsonify({"output": "No command provided", "cwd": os.getcwd()})

    # -----------------------------
    # Handle man command
    # -----------------------------
    if user_input.startswith("man"):
        parts = user_input.split()
        if len(parts) == 1:
            output_lines = []
            for cmd, info in command_manual.items():
                output_lines.append(f"{cmd}:\n  {info['description']}\n  Usage: {info['usage']}\n")
            return jsonify({"output": "\n".join(output_lines), "cwd": os.getcwd()})
        else:
            cmd = parts[1].strip()
            if cmd in command_manual:
                desc = command_manual[cmd]["description"]
                usage = command_manual[cmd]["usage"]
                return jsonify({"output": f"{cmd}:\n{desc}\nUsage:\n{usage}", "cwd": os.getcwd()})
            else:
                return jsonify({"output": f"No manual entry for '{cmd}'", "cwd": os.getcwd()})

    # -----------------------------
    # NL → command mapping
    # -----------------------------
    for phrase, cmd in nl_commands.items():
        if phrase.lower() in user_input.lower():
            user_input = cmd
            break

    # -----------------------------
    # Execute command
    # -----------------------------
    output = cp.parse_and_execute(user_input)

    # Return output + current working directory
    return jsonify({"output": output, "cwd": os.getcwd()})


@app.route("/suggest", methods=["POST"])
def suggest_command():
    data = request.json
    typed = data.get("typed", "").strip().lower()
    suggestions = []

    if typed:
        for key, cmds in command_suggestions.items():
            for cmd in cmds:
                if cmd.startswith(typed):
                    suggestions.append(cmd)

    suggestions = sorted(list(set(suggestions)))[:10]  # top 10
    return jsonify({"suggestions": suggestions})


# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
