import ast
from typing import Tuple, List

BANNED_MODULES = {
    "os", "sys", "subprocess", "socket", "requests", "urllib",
    "http", "ftplib", "shutil", "builtins", "importlib",
    "ctypes", "multiprocessing", "threading", "pty", "posix"
}

BANNED_BUILTIN_CALLS = {
    "eval", "exec", "open", "__import__", "compile",
    "globals", "locals", "getattr", "setattr", "delattr"
}

class SandboxSecurityError(Exception):
    pass

class ASTSecurityChecker(ast.NodeVisitor):
    def __init__(self):
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root_pkg = alias.name.split(".")[0]
            if root_pkg in BANNED_MODULES:
                self.violations.append(f"Forbidden import '{alias.name}' detected.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root_pkg = node.module.split(".")[0]
            if root_pkg in BANNED_MODULES:
                self.violations.append(f"Forbidden from-import '{node.module}' detected.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in BANNED_BUILTIN_CALLS:
                self.violations.append(f"Forbidden function call '{node.func.id}()' detected.")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr.startswith("__") and node.func.attr.endswith("__"):
                self.violations.append(f"Forbidden dunder attribute access '{node.func.attr}'.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in {"__subclasses__", "__bases__", "__globals__", "__code__"}:
            self.violations.append(f"Forbidden reflection attribute access '{node.attr}'.")
        self.generic_visit(node)

def validate_code_safety(code: str) -> Tuple[bool, List[str]]:
    """Static AST security gatekeeper for unverified candidate code."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"SyntaxError: {str(e)}"]

    checker = ASTSecurityChecker()
    checker.visit(tree)
    if checker.violations:
        return False, checker.violations
    return True, []
