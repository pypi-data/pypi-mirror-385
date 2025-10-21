"""
Code Explainer Skill

Explain code functionality in accessible terms for architects and developers.

Capabilities:
- explain_file: Summarize what a file does
- explain_function: Explain a specific function
- explain_class: Explain a specific class
- explain_pattern: Explain a code pattern

Used by: architect (understanding existing code), assistant (documentation)
"""

import ast
from pathlib import Path
from typing import Any, Dict, List


class CodeExplainer:
    """Explain code functionality in accessible terms."""

    def __init__(self, codebase_root: str = None):
        """Initialize code explainer."""
        self.codebase_root = Path(codebase_root or Path.cwd())

    def explain_file(self, file_path: str) -> Dict[str, Any]:
        """
        Summarize what a file does.

        Args:
            file_path: Path to Python file (relative to codebase root)

        Returns:
            {
                "file": "coffee_maker/auth/jwt.py",
                "summary": "Handles JWT token validation and generation",
                "purpose": "Provides JWT-based authentication mechanisms",
                "exports": [
                    {
                        "name": "validate_jwt",
                        "type": "function",
                        "description": "Validates JWT tokens using RS256 algorithm"
                    }
                ],
                "dependencies": ["PyJWT", "cryptography"],
                "key_concepts": ["JWT", "Token validation", "RSA signatures"]
            }
        """
        full_path = self.codebase_root / file_path
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {e}"}

        # Extract module docstring
        docstring = ast.get_docstring(tree) or ""

        # Extract functions and classes
        functions = []
        classes = []
        imports = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    func_doc = ast.get_docstring(node) or ""
                    functions.append(
                        {
                            "name": node.name,
                            "type": "function",
                            "description": func_doc.split("\n")[0] if func_doc else f"Function {node.name}",
                            "line": node.lineno,
                        }
                    )

            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    class_doc = ast.get_docstring(node) or ""
                    classes.append(
                        {
                            "name": node.name,
                            "type": "class",
                            "description": class_doc.split("\n")[0] if class_doc else f"Class {node.name}",
                            "line": node.lineno,
                        }
                    )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])

        # Extract key concepts from file name and content
        file_name = Path(file_path).stem.lower()
        key_concepts = self._extract_key_concepts(file_name, content)

        result = {
            "file": file_path,
            "summary": self._generate_summary(file_path, docstring, functions, classes),
            "purpose": docstring.split("\n\n")[0] if docstring else f"Provides {file_name} functionality",
            "exports": functions + classes,
            "dependencies": sorted(list(set(imports))),
            "key_concepts": key_concepts,
        }

        return result

    def explain_function(self, file_path: str, function_name: str) -> Dict[str, Any]:
        """
        Explain a specific function.

        Args:
            file_path: Path to Python file
            function_name: Name of function to explain

        Returns:
            {
                "file": "coffee_maker/auth/jwt.py",
                "function": "validate_jwt",
                "summary": "Validates JWT tokens using RS256 algorithm",
                "description": "...",
                "parameters": [
                    {
                        "name": "token",
                        "type": "str",
                        "description": "JWT token to validate"
                    }
                ],
                "returns": {
                    "type": "dict",
                    "description": "Decoded token payload"
                },
                "line_range": [45, 89],
                "complexity": "medium",
                "throws": ["ValueError", "InvalidTokenError"]
            }
        """
        full_path = self.codebase_root / file_path
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {e}"}

        # Find function node
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                func_node = node
                break

        if not func_node:
            return {"error": f"Function '{function_name}' not found in {file_path}"}

        # Extract function info
        docstring = ast.get_docstring(func_node) or ""
        parameters = self._extract_parameters(func_node)
        exceptions = self._extract_exceptions(func_node, content)
        line_range = [func_node.lineno, func_node.end_lineno or func_node.lineno]

        # Get complexity
        complexity = self._calculate_function_complexity(func_node)

        result = {
            "file": file_path,
            "function": function_name,
            "summary": (docstring.split("\n\n")[0] if docstring else f"Function {function_name}"),
            "description": docstring,
            "parameters": parameters,
            "returns": self._extract_return_type(func_node, docstring),
            "line_range": line_range,
            "complexity": complexity,
            "throws": exceptions,
        }

        return result

    def explain_class(self, file_path: str, class_name: str) -> Dict[str, Any]:
        """
        Explain a specific class.

        Args:
            file_path: Path to Python file
            class_name: Name of class to explain

        Returns:
            {
                "file": "coffee_maker/auth/jwt.py",
                "class": "JWTValidator",
                "summary": "Handles JWT token validation",
                "description": "...",
                "methods": [
                    {
                        "name": "validate",
                        "description": "Validates a JWT token"
                    }
                ],
                "attributes": [...],
                "inheritance": [],
                "line_range": [10, 150]
            }
        """
        full_path = self.codebase_root / file_path
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error reading file: {e}"}

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {e}"}

        # Find class node
        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_node = node
                break

        if not class_node:
            return {"error": f"Class '{class_name}' not found in {file_path}"}

        # Extract class info
        docstring = ast.get_docstring(class_node) or ""

        # Get methods
        methods = []
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                item_doc = ast.get_docstring(item) or ""
                methods.append(
                    {
                        "name": item.name,
                        "description": item_doc.split("\n")[0] if item_doc else f"Method {item.name}",
                    }
                )

        # Get inheritance
        inheritance = [base.id if hasattr(base, "id") else str(base) for base in class_node.bases]

        # Get attributes (from __init__)
        attributes = self._extract_class_attributes(class_node)

        line_range = [class_node.lineno, class_node.end_lineno or class_node.lineno]

        result = {
            "file": file_path,
            "class": class_name,
            "summary": (docstring.split("\n\n")[0] if docstring else f"Class {class_name}"),
            "description": docstring,
            "methods": methods,
            "attributes": attributes,
            "inheritance": inheritance,
            "line_range": line_range,
        }

        return result

    def explain_pattern(self, pattern_name: str) -> Dict[str, Any]:
        """
        Explain a code pattern.

        Args:
            pattern_name: Name of pattern (e.g., "dependency_injection", "singleton")

        Returns:
            {
                "pattern": "dependency_injection",
                "description": "...",
                "when_to_use": "...",
                "pros": [...],
                "cons": [...],
                "examples_in_codebase": [...]
            }
        """
        patterns = {
            "singleton": {
                "description": "Ensures only one instance of a class exists",
                "when_to_use": "For shared resources, configuration, registries",
                "pros": [
                    "Centralized state",
                    "Lazy initialization",
                    "Thread-safe",
                ],
                "cons": [
                    "Global state",
                    "Harder to test",
                    "Can hide dependencies",
                ],
            },
            "mixin": {
                "description": "Adds functionality to classes without inheritance",
                "when_to_use": "For cross-cutting concerns, code reuse",
                "pros": [
                    "Code reuse",
                    "Explicit composition",
                    "Flexible",
                ],
                "cons": [
                    "Method resolution order complexity",
                    "Can be overused",
                ],
            },
            "dependency_injection": {
                "description": "Provides dependencies to a class instead of creating them",
                "when_to_use": "For testability, loose coupling",
                "pros": ["Testable", "Loose coupling", "Flexible"],
                "cons": ["More boilerplate", "Can be over-engineered"],
            },
        }

        if pattern_name not in patterns:
            return {
                "error": f"Pattern '{pattern_name}' not found",
                "available_patterns": list(patterns.keys()),
            }

        result = patterns[pattern_name]
        result["pattern"] = pattern_name

        # Try to find examples in codebase
        result["examples_in_codebase"] = self._find_pattern_examples(pattern_name)

        return result

    def _extract_parameters(self, func_node: ast.FunctionDef) -> List[Dict]:
        """Extract function parameters from AST."""
        parameters = []

        for arg in func_node.args.args:
            param = {
                "name": arg.arg,
                "type": "unknown",
                "description": "",
            }
            parameters.append(param)

        return parameters

    def _extract_return_type(self, func_node: ast.FunctionDef, docstring: str) -> Dict:
        """Extract return type from function signature and docstring."""
        return_info = {
            "type": "unknown",
            "description": "",
        }

        # Try to extract from docstring
        if "Returns:" in docstring:
            return_info["description"] = docstring.split("Returns:")[1].split("\n\n")[0].strip()

        return return_info

    def _extract_exceptions(self, func_node: ast.FunctionDef, content: str) -> List[str]:
        """Extract exceptions raised by function."""
        exceptions = set()

        for node in ast.walk(func_node):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call):
                    if hasattr(node.exc.func, "id"):
                        exceptions.add(node.exc.func.id)

        return sorted(exceptions)

    def _extract_class_attributes(self, class_node: ast.ClassDef) -> List[Dict]:
        """Extract class attributes from __init__."""
        attributes = []

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                for node in ast.walk(item):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name):
                                    if target.value.id == "self":
                                        attributes.append(
                                            {
                                                "name": target.attr,
                                                "type": "instance",
                                            }
                                        )

        return attributes

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> str:
        """Calculate function complexity."""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                complexity += 1

        if complexity <= 2:
            return "low"
        elif complexity <= 5:
            return "medium"
        else:
            return "high"

    def _generate_summary(self, file_path: str, docstring: str, functions: List, classes: List) -> str:
        """Generate a summary of what the file does."""
        if docstring:
            return docstring.split("\n")[0]

        # Infer from file name and exports
        file_name = Path(file_path).stem.replace("_", " ").title()

        if classes:
            return f"Provides {file_name} functionality via {', '.join(c['name'] for c in classes[:2])}"
        elif functions:
            return f"Contains {file_name} functions including {', '.join(f['name'] for f in functions[:2])}"
        else:
            return f"Provides {file_name} functionality"

    def _extract_key_concepts(self, file_name: str, content: str) -> List[str]:
        """Extract key concepts from file name and content."""
        concepts = []

        # From file name
        name_parts = file_name.split("_")
        concepts.extend([p.title() for p in name_parts if len(p) > 2])

        # Look for common keywords
        keywords = {
            "auth": "Authentication",
            "database": "Database",
            "cache": "Caching",
            "async": "Asynchronous",
            "security": "Security",
            "validation": "Validation",
        }

        for keyword, concept in keywords.items():
            if keyword in content.lower():
                concepts.append(concept)

        return sorted(list(set(concepts)))

    def _find_pattern_examples(self, pattern_name: str) -> List[str]:
        """Find examples of a pattern in the codebase."""
        # This would search for the pattern in actual code
        # For now, return empty
        return []
