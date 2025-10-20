from google.genai import types
import subprocess,os
def execute_network_commands(command:str):
    output=subprocess.run(['python','shell.py',command,'1'],
                   cwd=os.getcwd().rstrip('agenticai\\functions'),
                   timeout=30,
                   capture_output=True,
                   text=True,
                   encoding='utf8')
    return f"STDOUT:{output.stdout}\nSTDERR:{output.stderr}"

schema_execute_network_commands=types.FunctionDeclaration(
    name="execute_network_commands",
    description="Executes VALLAIPALLAM(VNAS) network commands",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            'command':types.Schema(
                type=types.Type.STRING,
                description='The VNAS COMMAND to be executed.'
            )
        }
    )
)