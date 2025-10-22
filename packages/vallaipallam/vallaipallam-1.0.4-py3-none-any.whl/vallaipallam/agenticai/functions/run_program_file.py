import os,subprocess
from google.genai import types

def run_program_file(working_directory,filepath):
    abs_working_dir=os.path.abspath(working_directory)
    abs_directory=os.path.abspath(os.path.join(working_directory,filepath))

    if not abs_directory.startswith(abs_working_dir):
        return f"Error:{filepath} is not inside working directory."
    if not os.path.isfile(abs_directory):
        return f"Error:{filepath} is not a file."
    try:
        if filepath.endswith(".jnr"):
            output=subprocess.run(
                ["python","shell.py",abs_directory],
                cwd=os.getcwd(),
                timeout=30,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
        elif filepath.endswith(".py"):
            output=subprocess.run(
                ["python",abs_directory],
                cwd=abs_working_dir,
                timeout=30,
                capture_output=True,
                text=True,
                encoding='utf-8'
            ) 
        else:
            return f"Not specified programming language"  
        final_string=f'''
                  STDOUT:{output.stdout}
                  STDERR:{output.stderr}
        '''   
        if output.stdout or output.stdout:
            final_string+= f"No output produced"
        if output.returncode !=0:
            final_string+=f"Process exited with code{output.returncode}"
        return final_string
    except Exception as e:
        print(e)
        return f"Error while executing the file{filepath}{e}" 

schema_run_program_file=types.FunctionDeclaration(
    name="run_program_file",
    description="Runs a program file of languages Vallaipallam with extension .jnr,C,Cpp,Python and Java",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            'filepath':types.Schema(
                type=types.Type.STRING,
                description='The path to the file from the working directory to run.'
            )
        }
    )
)