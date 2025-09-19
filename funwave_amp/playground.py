import os
import ast
import sys
def find_functions_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    return functions

def scan_module_functions(module_dir):
    results = {}
    for root, _, files in os.walk(module_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                funcs = find_functions_in_file(file_path)
                if funcs:
                    results[file_path] = funcs
    return results

sys.stdout = open("functions_by_file.txt", "w", encoding="utf-8")
module_dir = r"C:\Users\rschanta\OneDrive - University of Delaware - o365\Desktop\Research\FUNWAVE_DS\funwave_ds"
functions_by_file = scan_module_functions(module_dir)
for file, funcs in functions_by_file.items():
    print(f"{file}:")
    for func in funcs:
        print(f"  - {func}")