"""
Model command stub - redirects to workflow command in ~/.mcli/commands/model.json

This stub exists for backwards compatibility with tests and imports.
The actual model command implementation is now in ~/.mcli/commands/model.json
"""

import sys
from pathlib import Path

# Try to load the model command from the workflow system
try:
    from mcli.lib.custom_commands import load_command_from_file

    # Load model command from ~/.mcli/commands/model.json
    model_json_path = Path.home() / ".mcli" / "commands" / "model.json"

    if model_json_path.exists():
        # Load the command from the JSON file
        import json

        with open(model_json_path, "r") as f:
            command_data = json.load(f)

        # Execute the code to get the app (model command group)
        code = command_data.get("code", "")
        namespace = {}
        exec(code, namespace)

        # Extract the app (model command group) and individual commands
        app = namespace.get("app")
        if app:
            # The model group command
            model = app

            # Extract individual subcommands from the model group
            if hasattr(model, "commands"):
                commands = model.commands
                list = commands.get("list")
                download = commands.get("download")
                start = commands.get("start")
                recommend = commands.get("recommend")
                status = commands.get("status")
                stop = commands.get("stop")
                pull = commands.get("pull")
                delete = commands.get("delete")
            else:
                # Fallback if commands aren't available
                list = download = start = recommend = status = stop = pull = delete = None
        else:
            # If app is not found, create empty placeholders
            model = list = download = start = recommend = status = stop = pull = delete = None
    else:
        # If the JSON file doesn't exist, create empty placeholders
        print(f"Warning: {model_json_path} not found", file=sys.stderr)
        model = list = download = start = recommend = status = stop = pull = delete = None

except Exception as e:
    print(f"Error loading model command from workflow: {e}", file=sys.stderr)
    import traceback

    traceback.print_exc()
    model = list = download = start = recommend = status = stop = pull = delete = None

# Export the commands for backwards compatibility
__all__ = ["model", "list", "download", "start", "recommend", "status", "stop", "pull", "delete"]
