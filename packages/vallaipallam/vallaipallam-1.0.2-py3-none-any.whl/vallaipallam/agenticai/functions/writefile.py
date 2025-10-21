import os
from google.genai import types


def write_file(working_directory,filepath,content):
    abs_working_dir=os.path.abspath(working_directory)
    abs_directory=os.path.abspath(os.path.join(working_directory,filepath))
    
    parent_dir=os.path.dirname(abs_directory)
    if not os.path.isdir(parent_dir):
        try:
            os.makedirs(parent_dir)
        except Exception as e :
            return f"Could not make the parent dir:{parent_dir} :{e}"
    if not abs_directory.startswith(abs_working_dir):
        return f"Error:{filepath} is not inside working directory."
    try:
        with open(abs_directory,'w',encoding='utf-8') as f:
            f.write(content)
        return f"Successfully written content into the file{abs_directory}"
    except Exception as e:
        return f"Exception while writing into file {abs_directory} : {e}"
    
schema_write_file=types.FunctionDeclaration(
    name="write_file",
    description="Overwriters a existing file or writes in a new file if it doesn't exist (and creates required parent dirs safely) constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            'filepath':types.Schema(
                type=types.Type.STRING,
                description='The path of the file  to be writtern.'
            ),
            'content':types.Schema(
                type=types.Type.STRING,
                description="Content to be written in the file as a string."
            )
        }
    )
)    