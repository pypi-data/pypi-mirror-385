"""AST-based code parsing utilities for production-quality analysis."""
import ast
import re
from typing import Set, List, Dict


class ImportVisitor(ast.NodeVisitor):
    """Extract imports using AST for accurate parsing."""
    def __init__(self):
        self.imports: Set[str] = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)


class CallVisitor(ast.NodeVisitor):
    """Extract function calls using AST for accurate parsing."""
    def __init__(self):
        self.calls: Set[str] = set()
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.add(node.func.attr)
        self.generic_visit(node)


class FunctionVisitor(ast.NodeVisitor):
    """Extract function definitions and their details using AST."""
    def __init__(self):
        self.functions: List[Dict] = []
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'params': len(node.args.args),
            'decorators': len(node.decorator_list),
            'has_docstring': ast.get_docstring(node) is not None
        })
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'params': len(node.args.args),
            'decorators': len(node.decorator_list),
            'has_docstring': ast.get_docstring(node) is not None
        })
        self.generic_visit(node)


def parse_imports_ast(content: str) -> Set[str]:
    """Parse imports using AST (production-quality replacement for regex)."""
    try:
        tree = ast.parse(content)
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except SyntaxError:
        # Fallback to regex if AST parsing fails
        imports = set()
        import_patterns = [
            r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
        ]
        for pattern in import_patterns:
            imports.update(re.findall(pattern, content, re.MULTILINE))
        return imports


def parse_calls_ast(content: str, function_name: str) -> Set[str]:
    """Parse function calls using AST (production-quality replacement for regex)."""
    try:
        tree = ast.parse(content)
        # Find the specific function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                visitor = CallVisitor()
                visitor.visit(node)
                # Filter out built-ins and common keywords
                keywords = {'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'print', 'range'}
                return {c for c in visitor.calls if c not in keywords}
        return set()
    except SyntaxError:
        # Fallback to regex
        func_pattern = rf'def {re.escape(function_name)}\s*\('
        func_match = re.search(func_pattern, content)
        if not func_match:
            return set()
        start = func_match.start()
        next_def = re.search(r'\ndef \w+\s*\(', content[start + 1:])
        end = start + next_def.start() if next_def else len(content)
        func_body = content[start:end]
        call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        calls = set(re.findall(call_pattern, func_body))
        keywords = {'if', 'for', 'while', 'return', 'yield', 'def', 'class', 'with', 'try', 'except', 'print'}
        return {c for c in calls if c not in keywords and c != function_name}


def parse_functions_ast(content: str) -> List[Dict]:
    """Parse function definitions using AST."""
    try:
        tree = ast.parse(content)
        visitor = FunctionVisitor()
        visitor.visit(tree)
        return visitor.functions
    except SyntaxError:
        return []


def extract_purpose(content: str, file_path: str) -> str:
    """Extract file purpose from docstrings and comments."""
    # Try docstring first
    m = re.search(r'^\s*"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
    if m:
        return m.group(1).strip()[:200]
    # Try comment
    m = re.search(r'^\s*#\s*(.*?)(?:\n|$)', content, re.MULTILINE)
    if m:
        return m.group(1).strip()[:200]
    # Fallback to filename
    import os
    return f"File: {os.path.basename(file_path)}"


def extract_key_exports(content: str, file_path: str) -> List[str]:
    """Extract key exports (classes, functions) from file."""
    exports = []
    # Classes
    exports.extend(re.findall(r'class\s+(\w+)', content)[:10])
    # Public functions (not starting with _)
    exports.extend([f for f in re.findall(r'def\s+([a-zA-Z_]\w*)', content) if not f.startswith('_')][:10])
    # JS/TS exports
    if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
        exports.extend(re.findall(r'export\s+(?:function|class|const|let|var)\s+(\w+)', content)[:10])
    return list(set(exports))[:15]
