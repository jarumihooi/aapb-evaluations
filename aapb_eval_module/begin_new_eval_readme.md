# For Developers of new Clams Apps Evaluations
Hello, it seems you are trying to create new evaluation code for a CLAMS app. 
To do so: 
```bash
# make the current /aapb_eval_module dir your current working directory. 
cd aapb_eval_module
# run the project directory generator
# the code will ask you to name the directory. Name it something ending with "_eval". e.g. "your_new_app_eval".
python generate_new_eval_dir.py
# download any requirements
cd .. 
cd your_new_app_eval
# edit the requirements.txt for any new requirements you would need.
pip install -r requirements.txt
```
This will create a new subdirectory for your evaluation task. It will contain: 
1. `__init__.py` for modular running of the app. 
2. `requirements.txt` for quickly downloading any requirements and common imports for writing eval code. 
3. `eval_abc.py` this is a copy of an abstract base class (abc) for you to begin writing the eval code with expected
required methods. 
4. `template_for_new_reports.md` as a pre-generated report template, again suggesting commonly expected parts of the 
report format for human reading. 

> [!Note]  
> TODO: Numbers 3 and 4 need to be renamed to a better file name.
