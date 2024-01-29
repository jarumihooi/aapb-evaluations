'''Abstract Base Class for new Evaluations of Clams Apps
There are two helper code modules for writing new clams app evaluations.
1. This abstract base class and inherited class for writing the new evaluation code. This has methods that are
suggestively required steps for a new evaluation code that are not standardized.
2. Some standardized/common functions have been implemented for you and are contained in this eval module as a package.
Furthermore, the other pieces are imported here. These include things like: goldretriever, locate_inputs.
Moving forward, common accuracy metrics from known libraries will be included in the import as well.

To use this template, run "generate_new_eval.py <project_name> to create a project directory. Add any extra dependencies
you want in the requirements.txt.  Then run "pip install -r requirements.txt" to import all the suggested modules/code
along with any new requirements you require.

'''

from abc import ABC, abstractmethod
import aapb_eval_module # import its own module when copied to a new dir.
# add general imports here.

class NewEvaluation(ABC):
    @abstractmethod
    def abstract_method(self):
        pass

    @abstractmethod
    def another_abstract_method(self):
        pass

class MyEvaluation(NewEvaluation): # change the name of MyEvaluation
    def abstract_method(self):
        print("Implemented abstract_method")

    def another_abstract_method(self):
        print("Implemented another_abstract_method")

# You cannot create an instance of an abstract class
# obj = MyAbstractClass()  # This would raise an error

# Instantiate the concrete class
obj = MyEvaluation() # change the name of MyEvaluation

# Call the implemented methods
obj.abstract_method()
obj.another_abstract_method()
