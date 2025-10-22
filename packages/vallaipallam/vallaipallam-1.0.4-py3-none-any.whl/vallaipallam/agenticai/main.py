import os
from google import genai
from google.genai import types
from vallaipallam.agenticai.functions.get_files_info import schema_get_files_info
from vallaipallam.agenticai.functions.get_file_content import schema_get_file_content
from vallaipallam.agenticai.functions.run_program_file import schema_run_program_file
from vallaipallam.agenticai.functions.writefile import schema_write_file
from vallaipallam.agenticai.functions.call_function import call_function
from vallaipallam.agenticai.functions.execute_network_commands import schema_execute_network_commands

def main(user_input,working_dir,gemini_api_key,chat=None):
    api_key=gemini_api_key
    prompt=user_input
    filepath=os.path.join(os.path.dirname(__file__), "systemprompt.txt")
    system_prompt=open(filepath,encoding='utf8').read()
    available_functions=types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_write_file,
            schema_get_file_content,
            schema_run_program_file,
            schema_execute_network_commands
        ]
    )
    messages=[types.Content(role="user",parts=[types.Part(text=prompt)])] if not chat else [i[-1] for i in chat]+[types.Content(role="user",parts=[types.Part(text=prompt)])]
    config=types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt)

    client=genai.Client(api_key=api_key)
    for i in range(20):
        response=client.models.generate_content(
            model="gemini-2.0-flash-001",contents=messages,
            config=config
        )
        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None:
                    continue
                messages.append(candidate.content)

        if response.function_calls:
            for function in response.function_calls:
                result=call_function(function_call_part=function,working_directory=working_dir)
                messages.append(result)
        else:
            return response.text
