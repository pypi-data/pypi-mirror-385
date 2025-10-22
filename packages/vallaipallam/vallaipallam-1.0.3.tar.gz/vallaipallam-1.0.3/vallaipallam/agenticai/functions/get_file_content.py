import os
from google.genai import types

def get_file_content(working_directory,filepath):
    abs_working_dir=os.path.abspath(working_directory)
    abs_directory=os.path.abspath(os.path.join(working_directory,filepath))

    if not abs_directory.startswith(abs_working_dir):
        return f"Error:{filepath} is not inside working directory."
    if not os.path.isfile(abs_directory):
        return f"Error:{filepath} is not a file."
    try:
        with open(abs_directory,'r',encoding='utf8') as f:
            file_content_string = f.read()
        return file_content_string
    except Exception as e:
        print(f'Exception while reading:{e}')

schema_get_file_content=types.FunctionDeclaration(
    name="get_file_content",
    description="Gets the contents of the given file as a string,constrained to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            'filepath':types.Schema(
                type=types.Type.STRING,
                description='The path to the file from the working directory'
            )
        }
    )
)