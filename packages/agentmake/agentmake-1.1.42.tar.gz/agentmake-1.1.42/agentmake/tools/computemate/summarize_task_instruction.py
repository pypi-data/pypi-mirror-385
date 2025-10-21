from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH
from agentmake.utils.handle_text import readTextFile
import os

system_path_1 = os.path.join(AGENTMAKE_USER_DIR, "computemate", "summarize_task_instruction.md")
system_path_2 = os.path.join(PACKAGE_PATH, "computemate", "summarize_task_instruction.md")

TOOL_SYSTEM = readTextFile(system_path_1 if os.path.isfile(system_path_1) else system_path_2)

TOOL_SCHEMA = {
    "name": "summarize_task_instruction",
    "description": "Identify the task goal regarding computer-related tasks and transform it into a direct instruction in one sentence.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_instruction": {
                "type": "string",
                "description": "Identify the task goal regarding computer-related tasks and transform it into a direct instruction in one sentence.",
            },
        },
        "required": ["task_instruction"],
    },
}

def summarize_task_instruction(task_instruction: str, **kwargs):
    print(f"```instruction\n{task_instruction}\n```")
    return ""

TOOL_FUNCTION = summarize_task_instruction