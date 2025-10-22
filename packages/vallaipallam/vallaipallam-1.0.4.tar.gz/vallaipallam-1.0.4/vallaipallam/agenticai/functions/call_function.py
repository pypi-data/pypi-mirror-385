from google.genai import types
from vallaipallam.agenticai.functions.get_files_info import get_files_info
from vallaipallam.agenticai.functions.get_file_content import get_file_content
from vallaipallam.agenticai.functions.run_program_file import run_program_file
from vallaipallam.agenticai.functions.writefile import write_file
from vallaipallam.agenticai.functions.execute_network_commands import execute_network_commands


def call_function(function_call_part,working_directory):

    if function_call_part.name == 'get_files_info':
        result=get_files_info(working_directory,**function_call_part.args)
    elif function_call_part.name == 'get_file_content':
        result=get_file_content(working_directory,**function_call_part.args)
    elif function_call_part.name == 'write_file':
        result=write_file(working_directory,**function_call_part.args)
    elif function_call_part.name == 'run_program_file':
        result=run_program_file(working_directory,**function_call_part.args)
    elif function_call_part.name == 'execute_network_commands':
        result=execute_network_commands(**function_call_part.args)
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"Error":f"Unkown function:{function_call_part.name}"}

                )
            ]
        )
    return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result":result}

                )
            ]
        )

