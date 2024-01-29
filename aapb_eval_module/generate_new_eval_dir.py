import os
import shutil
from datetime import datetime

def create_project_directory(project_name):
    # Get the parent directory of the current working directory
    parent_dir = os.path.dirname(os.getcwd())
    # Create main project directory in the parent directory
    project_dir = os.path.join(parent_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir

def create_init_file(project_dir):
    # Create __init__.py file for modular running of evaluations.
    init_file_contents = ""
    init_file_path = os.path.join(project_dir, '__init__.py')
    with open(init_file_path, 'w') as init_file:
        init_file.write(init_file_contents)

    print(f"__init__.py module file created at: {init_file_path}")

def create_requirements_txt(project_dir):
    # Create requirements.txt file
    requirements_content = "# Add your project dependencies here"
    requirements_path = os.path.join(project_dir, 'requirements.txt')
    with open(requirements_path, 'w') as requirements_file:
        requirements_file.write(requirements_content)

    print(f"Requirements.txt file created at: {requirements_path}")

def copy_evaluation_module_template(project_dir):
    # Copy evaluation module template
    eval_abc_name = 'eval_abc.py'
    eval_abc_path = os.path.join(os.getcwd(), eval_abc_name)
    print(f"{eval_abc_path=}")
    if os.path.exists(eval_abc_path):
        shutil.copy(eval_abc_path, project_dir)\
        # TODO: RENAME THIS THING!! AND THE OTHER COPIED FILE TOO!
        print(f"Evaluation module template created at: {eval_abc_path}")
    else:
        # Raise a FileNotFoundError and stop execution
        raise FileNotFoundError(f"Error: Evaluation module template file '{eval_abc_name}' not found in the current directory. "
                                f"Please edit Evaluation module template file path and target file.")
    # end

def copy_report_template_file(project_dir):
    # Get the parent directory of the current working directory # a lil redundant
    parent_dir = os.path.dirname(os.getcwd())
    # Path to the template file in the parent directory
    template_file_name = 'template_for_new_reports.md'
    template_file_path = os.path.join(parent_dir, template_file_name)
    if os.path.exists(template_file_path):
        # Copy the template file to the new dir
        shutil.copy(template_file_path, project_dir)
        print(f"Template file copied to: {project_dir}")
    else:
        # Raise a FileNotFoundError and stop execution
        raise FileNotFoundError(f"Error: Template file '{template_file_name}' not found in the parent directory. "
                                f"Please edit template file path and target file.")

if __name__ == "__main__":
    print("Reminder: This code assumes your current working dir is /aapb_eval_module where this code resides.")
    project_name = input("Enter project name ending with '_eval': ")
    print()

    project_dir = create_project_directory(project_name)
    create_init_file(project_dir)
    create_requirements_txt(project_dir)
    copy_evaluation_module_template(project_dir)
    copy_report_template_file(project_dir)

    print(f"Project structure and template files created in: {project_dir}")
