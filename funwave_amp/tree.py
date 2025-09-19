import os
import ast
import sys

def find_functions_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def scan_module_functions(module_dir):
    results = {}
    for root, _, files in os.walk(module_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, module_dir)
                results[rel_path] = find_functions_in_file(file_path)
    return results

def print_tree(results, module_dir, out_file="functions_tree.txt"):
    sys.stdout = open(out_file, "w", encoding="utf-8")

    def walk_dir(base, prefix=""):
        entries = sorted(os.listdir(base))
        for i, entry in enumerate(entries):
            path = os.path.join(base, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            if os.path.isdir(path):
                print(prefix + connector + entry + "/")
                extension = "    " if i == len(entries) - 1 else "│   "
                walk_dir(path, prefix + extension)
            elif entry.endswith(".py"):
                rel_path = os.path.relpath(path, module_dir)
                funcs = results.get(rel_path, [])
                print(prefix + connector + entry)
                for j, func in enumerate(funcs):
                    sub_connector = "└── " if j == len(funcs) - 1 else "├── "
                    print(prefix + "    " + sub_connector + func)

    walk_dir(module_dir)
    sys.stdout.close()

# Example usage
if __name__ == "__main__":
    module_dir = r"C:\Users\rschanta\OneDrive - University of Delaware - o365\Desktop\Research\FUNWAVE_DS\funwave_ds"
    results = scan_module_functions(module_dir)
    print_tree(results, module_dir)
    print("Tree dumped to functions_tree.txt")
