import ast
from typing import Dict, Any

class CodeProfiler:
    """Static AST and structural metric analyzer."""

    def analyze_ast(self, code: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
        except Exception:
            return {"ast_node_count": 0, "cyclomatic_complexity": 1}

        node_count = sum(1 for _ in ast.walk(tree))
        
        # Cyclomatic complexity: 1 + decision points (If, While, For, ExceptHandler, With, BoolOp)
        cc = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                cc += 1
            elif isinstance(node, ast.BoolOp):
                cc += len(node.values) - 1
            elif isinstance(node, ast.IfExp):
                cc += 1

        return {
            "ast_node_count": node_count,
            "cyclomatic_complexity": cc,
        }

profiler = CodeProfiler()
