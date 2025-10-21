import os
import inspect
import subprocess
import sys
import types
from typing import Tuple, Any
from biosero.datamodels.adapter.decorators import parameter
from biosero.datamodels.adapter.helpers import Helpers


class ClientLibraryGenerator:
    CLASS_TEMPLATE = """
from biosero.datamodels.adapter.decorators import parameter
from biosero.datamodels.adapter.helpers import Helpers
from typing import Tuple, Any

class Actions(object):

    def __init__(self, url):
        self.helpers = Helpers(url)
"""

    METHOD_TEMPLATE = """
    @parameter(name='{template_name}', inputs={inputs}, outputs={outputs})
    def {name}(self, {params}) -> Tuple[{return_type}]:
        return self.helpers.process_order()
"""

    def __init__(self, base_path: str, action_templates):
        """
        Initializes the client library generator.

        :param base_path: The base directory where the client library will be generated.
        :param action_templates: The imported action_templates module.
        """
        self.base_path = os.path.abspath(base_path)  # Ensure absolute path
        self.package_dir = os.path.join(self.base_path, "src/dataservices/adapter")
        self.dist_dir = os.path.join(self.base_path, "dist")
        self.build_dir = os.path.join(self.base_path, "build")
        self.egg_info_dir = os.path.join(self.base_path, "src/dataservices.egg-info")
        self.action_templates = action_templates  # Pass action_templates dynamically

    def extract_outputs(self, decorator):
        """Extract the outputs from the parameter decorator."""
        return decorator.get('outputs', [])

    def generate_methods(self):
        methods = []
        for name in dir(self.action_templates):
            method = getattr(self.action_templates, name)
            if isinstance(method, types.FunctionType) and hasattr(method, '_parameter_decorator'):
                methods.append(method)

        generated_methods = []
        for method in methods:
            decorator = method._parameter_decorator
            template_name = decorator['name']
            print(f"Generating method for {template_name}")

            name = method.__name__
            sig = inspect.signature(method)
            params = ", ".join(
                [f"{p}: {t.annotation.__name__ if t.annotation != inspect._empty else 'Any'}"
                 for p, t in sig.parameters.items()]
            )
            inputs = [p.replace("_", " ").title() for p in sig.parameters.keys()]
            outputs = self.extract_outputs(decorator)

            return_annotation = sig.return_annotation
            if return_annotation is inspect._empty:
                return_type = "Any"
            elif hasattr(return_annotation, '__args__'):
                return_type = ", ".join([t.__name__ for t in return_annotation.__args__])
            else:
                return_type = return_annotation.__name__

            method_code = self.METHOD_TEMPLATE.format(
                name=name,
                template_name=template_name,
                params=params,
                inputs=inputs,
                outputs=outputs,
                return_type=return_type
            )
            generated_methods.append(method_code)
        return generated_methods

    def generate_client_library(self):
        # Step 1: Create necessary directories
        os.makedirs(self.package_dir, exist_ok=True)
        os.makedirs(self.dist_dir, exist_ok=True)
        os.makedirs(self.build_dir, exist_ok=True)

        # Step 2: Create __init__.py files
        self.create_init_file(os.path.join(self.base_path, "src/dataservices"))
        self.create_init_file(self.package_dir)

        # Step 3: Generate the Python file
        with open(os.path.join(self.package_dir, "actions.py"), "w") as f:
            class_code = self.CLASS_TEMPLATE + "\n".join(self.generate_methods())
            f.write(class_code)

        # Step 4: Create setup.py file
        self.create_setup_file()

        print(f"Client library generated successfully in {self.base_path}!")

        # Step 5: Ensure wheel is installed
        subprocess.run([sys.executable, "-m", "pip", "install", "wheel"], check=True)

        # Step 6: Build the distribution files
        self.build_distribution()

    def create_init_file(self, path):
        with open(os.path.join(path, "__init__.py"), "w") as init_file:
            init_file.write("# This is the __init__.py file\n")

    def create_setup_file(self):
        setup_path = os.path.join(self.base_path, "setup.py")
        with open(setup_path, "w") as setup_file:
            setup_file.write(
    f"""from setuptools import setup, find_packages

setup(
    name='dataservices',
    version='0.1',
    package_dir={{'': 'src'}},
    packages=find_packages(where='src'),
    install_requires=[
        # Add your dependencies here
    ],
)
"""
)


    def build_distribution(self):
        try:
            subprocess.run(
                [sys.executable, os.path.join(self.base_path, "setup.py"), "sdist", "bdist_wheel"],
                cwd=self.base_path,  # Ensure build output stays in base path
                check=True
            )
            print(f"Distribution files generated successfully in {self.base_path}!")

            # Ensure dataservices.egg-info is in the base path
            if os.path.exists(self.egg_info_dir):
                print(f"Egg info directory created: {self.egg_info_dir}")
            else:
                print("dataservices.egg-info not found. It may be created dynamically during install.")

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while building distribution files: {e}")

