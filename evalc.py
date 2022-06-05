import os
import json
from pycparser import parse_file, c_ast

base_code = """
# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <unistd.h>

int func ({proto}) {{
    {code}
}}

int main(int argc, char **argv) {{
    return func({args});
}}
"""


allowed_functions = []

class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.forbidden = False
        pass

    def visit_FuncCall(self, node):
        if node.name.name not in allowed_functions:
            self.forbidden = True
        if node.args:
            self.visit(node.args)

def check_forbidden(code):
    with open("/tmp/check_code.c", "w+") as f:
        f.write("""void func() {{ {code} }}""".format(code=code))
    try:
        ast = parse_file("/tmp/check_code.c", use_cpp=True)
    except:
        return (True, "Could not parse code, syntax error...")
    v = FuncCallVisitor()
    v.visit(ast)
    os.remove("/tmp/check_code.c")
    return (v.forbidden, "Forbidden function call.")

class cExercises:
    def __init__(self):
        self.exercise = None
        self.file = None
        self.status = {"passed": False, "message": "No test passed."}
    def set_exercise(self, file):
        global allowed_functions
        with open(file) as f:
            self.exercise = json.load(f)
        self.file = file
        allowed_functions = self.exercise["allowed_functions"]
    def clean_files(self):
        if os.path.isfile("/tmp/code.c"):
            os.remove("/tmp/code.c")
        if os.path.isfile("/tmp/code"):
            os.remove("/tmp/code")
        if os.path.isfile("/tmp/code_output"):
            os.remove("/tmp/code_output")

    def check_exercise(self, code):
        if not self.exercise:
            return False
        forb = check_forbidden(code)
        if (forb[0]):
            self.status = {"passed": False, "message": forb[1]}
            return
        for test in self.exercise["asserts"]:
            with open("/tmp/code.c", "w+") as f:
                f.write(base_code.format(proto=self.exercise["proto"], code=code, args=test["args"]))
            if os.system("timeout 1s gcc -o /tmp/code /tmp/code.c") != 0:
                self.status = {"passed": False, "message": "Compilation error."}
                return self.clean_files()
            if not os.path.isfile("/tmp/code"):
                self.status = {"passed": False, "message": "Compilation error."}
                return self.clean_files()

            retval = int(os.system("timeout 1s /tmp/code > /tmp/code_output") / 256)
            stdout_val = ""
            with open("/tmp/code_output", "r") as f:
                try:
                    stdout_val = f.read()
                except UnicodeDecodeError:
                    self.status = {"passed": False, "message": "Wrong output... Weird characters."}
                    return self.clean_files()
            if retval != test["return"]:
                if retval == 124:
                    self.status = {"passed": False, "message": "Time limit exceeded."}
                elif retval == 139:
                    self.status = {"passed": False, "message": "Segmentation fault."}
                else:
                    self.status = {"passed": False, "message": "Wrong return value (e: {retval}, g: {gotret}).".format(retval=test["return"], gotret=retval)}
                return self.clean_files()
            if stdout_val != test["stdout"]:
                self.status = {"passed": False, "message": "Wrong output."}
                return self.clean_files()
            self.clean_files()
        self.status = {"passed": True, "message": "All tests passed."}
        return self.clean_files()