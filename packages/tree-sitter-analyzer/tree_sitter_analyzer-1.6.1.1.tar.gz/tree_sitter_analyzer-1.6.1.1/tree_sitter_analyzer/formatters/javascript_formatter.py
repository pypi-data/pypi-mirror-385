#!/usr/bin/env python3
"""
JavaScript-specific table formatter.

Provides specialized formatting for JavaScript code analysis results,
handling modern JavaScript features like ES6+ syntax, async/await,
classes, modules, and framework-specific patterns.
"""

from typing import Any

from .base_formatter import BaseTableFormatter


class JavaScriptTableFormatter(BaseTableFormatter):
    """Table formatter specialized for JavaScript"""

    def format(self, data: dict[str, Any]) -> str:
        """Format data using the configured format type"""
        return self.format_structure(data)

    def _format_full_table(self, data: dict[str, Any]) -> str:
        """Full table format for JavaScript"""
        lines = []

        # Header - JavaScript (module/file based)
        file_path = data.get("file_path", "Unknown")
        file_name = file_path.split("/")[-1].split("\\")[-1]
        module_name = (
            file_name.replace(".js", "").replace(".jsx", "").replace(".mjs", "")
        )

        # Check if this is a module (has exports)
        exports = data.get("exports", [])
        is_module = len(exports) > 0

        if is_module:
            lines.append(f"# Module: {module_name}")
        else:
            lines.append(f"# Script: {module_name}")
        lines.append("")

        # Imports
        imports = data.get("imports", [])
        if imports:
            lines.append("## Imports")
            lines.append("```javascript")
            for imp in imports:
                import_statement = imp.get("statement", "")
                if not import_statement:
                    # Construct import statement from parts
                    source = imp.get("source", "")
                    name = imp.get("name", "")
                    if name and source:
                        import_statement = f"import {name} from {source};"
                lines.append(import_statement)
            lines.append("```")
            lines.append("")

        # Module Info
        stats = data.get("statistics", {})
        classes = data.get("classes", [])

        lines.append("## Module Info")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| File | {file_name} |")
        lines.append(f"| Type | {'ES6 Module' if is_module else 'Script'} |")
        lines.append(f"| Functions | {stats.get('function_count', 0)} |")
        lines.append(f"| Classes | {len(classes)} |")
        lines.append(f"| Variables | {stats.get('variable_count', 0)} |")
        lines.append(f"| Exports | {len(exports)} |")
        lines.append("")

        # Classes (if any)
        if classes:
            lines.append("## Classes")
            lines.append("| Class | Type | Extends | Lines | Methods | Properties |")
            lines.append("|-------|------|---------|-------|---------|------------|")

            for class_info in classes:
                name = str(class_info.get("name", "Unknown"))
                class_type = "class"  # JavaScript only has classes
                extends = str(class_info.get("superclass", "")) or "-"
                line_range = class_info.get("line_range", {})
                lines_str = f"{line_range.get('start', 0)}-{line_range.get('end', 0)}"

                # Count methods within the class
                class_methods = [
                    m
                    for m in data.get("methods", [])
                    if line_range.get("start", 0)
                    <= m.get("line_range", {}).get("start", 0)
                    <= line_range.get("end", 0)
                ]

                # Count properties (class fields)
                class_properties = [
                    v
                    for v in data.get("variables", [])
                    if line_range.get("start", 0)
                    <= v.get("line_range", {}).get("start", 0)
                    <= line_range.get("end", 0)
                ]

                lines.append(
                    f"| {name} | {class_type} | {extends} | {lines_str} | {len(class_methods)} | {len(class_properties)} |"
                )
            lines.append("")

        # Variables/Constants
        variables = data.get("variables", [])
        if variables:
            lines.append("## Variables")
            lines.append("| Name | Type | Scope | Kind | Line | Value |")
            lines.append("|------|------|-------|------|------|-------|")

            for var in variables:
                name = str(var.get("name", ""))
                # Try to get value from initializer or value field
                var_value = var.get("initializer") or var.get("value", "")
                var_type = self._infer_js_type(var_value)
                scope = self._determine_scope(var)
                kind = self._get_variable_kind(var)
                line = var.get("line_range", {}).get("start", 0)
                value = str(var_value)[:30] + (
                    "..." if len(str(var_value)) > 30 else ""
                )
                value = value.replace("\n", " ").replace("|", "\\|")

                lines.append(
                    f"| {name} | {var_type} | {scope} | {kind} | {line} | {value} |"
                )
            lines.append("")

        # Functions
        functions = data.get("functions", [])
        if functions:
            # Group functions by type
            regular_functions = [
                f
                for f in functions
                if not self._is_method(f) and not f.get("is_async", False)
            ]
            async_functions = [
                f
                for f in functions
                if not self._is_method(f) and f.get("is_async", False)
            ]
            methods = [f for f in functions if self._is_method(f)]

            # Regular Functions
            if regular_functions:
                lines.append("## Functions")
                lines.append(
                    "| Function | Parameters | Type | Lines | Complexity | JSDoc |"
                )
                lines.append(
                    "|----------|------------|------|-------|------------|-------|"
                )

                for func in regular_functions:
                    lines.append(self._format_function_row(func))
                lines.append("")

            # Async Functions
            if async_functions:
                lines.append("## Async Functions")
                lines.append(
                    "| Function | Parameters | Type | Lines | Complexity | JSDoc |"
                )
                lines.append(
                    "|----------|------------|------|-------|------------|-------|"
                )

                for func in async_functions:
                    lines.append(self._format_function_row(func))
                lines.append("")

            # Methods (class methods)
            if methods:
                lines.append("## Methods")
                lines.append(
                    "| Method | Class | Parameters | Type | Lines | Complexity | JSDoc |"
                )
                lines.append(
                    "|--------|-------|------------|------|-------|------------|-------|"
                )

                for method in methods:
                    lines.append(self._format_method_row(method))
                lines.append("")

        # Exports
        if exports:
            lines.append("## Exports")
            lines.append("| Export | Type | Name | Default |")
            lines.append("|--------|------|------|---------|")

            for export in exports:
                export_type = self._get_export_type(export)
                name = str(export.get("name", ""))
                is_default = "✓" if export.get("is_default", False) else "-"

                lines.append(f"| {export_type} | {name} | {is_default} |")
            lines.append("")

        # Trim trailing blank lines
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def _format_compact_table(self, data: dict[str, Any]) -> str:
        """Compact table format for JavaScript"""
        lines = []

        # Header
        file_path = data.get("file_path", "Unknown")
        file_name = file_path.split("/")[-1].split("\\")[-1]
        module_name = (
            file_name.replace(".js", "").replace(".jsx", "").replace(".mjs", "")
        )
        lines.append(f"# {module_name}")
        lines.append("")

        # Info
        stats = data.get("statistics", {})
        lines.append("## Info")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| Functions | {stats.get('function_count', 0)} |")
        lines.append(f"| Classes | {len(data.get('classes', []))} |")
        lines.append(f"| Variables | {stats.get('variable_count', 0)} |")
        lines.append(f"| Exports | {len(data.get('exports', []))} |")
        lines.append("")

        # Functions (compact)
        functions = data.get("functions", [])
        if functions:
            lines.append("## Functions")
            lines.append("| Function | Params | Type | L | Cx | Doc |")
            lines.append("|----------|--------|------|---|----|----|")

            for func in functions:
                name = str(func.get("name", ""))
                params = self._create_compact_params(func)
                func_type = self._get_function_type_short(func)
                line_range = func.get("line_range", {})
                lines_str = f"{line_range.get('start', 0)}-{line_range.get('end', 0)}"
                complexity = func.get("complexity_score", 0)
                doc = self._clean_csv_text(
                    self._extract_doc_summary(str(func.get("jsdoc", "")))
                )

                lines.append(
                    f"| {name} | {params} | {func_type} | {lines_str} | {complexity} | {doc} |"
                )
            lines.append("")

        # Trim trailing blank lines
        while lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def _format_function_row(self, func: dict[str, Any]) -> str:
        """Format a function table row for JavaScript"""
        name = str(func.get("name", ""))
        params = self._create_full_params(func)
        func_type = self._get_function_type(func)
        line_range = func.get("line_range", {})
        lines_str = f"{line_range.get('start', 0)}-{line_range.get('end', 0)}"
        complexity = func.get("complexity_score", 0)
        doc = self._clean_csv_text(
            self._extract_doc_summary(str(func.get("jsdoc", "")))
        )

        return (
            f"| {name} | {params} | {func_type} | {lines_str} | {complexity} | {doc} |"
        )

    def _format_method_row(self, method: dict[str, Any]) -> str:
        """Format a method table row for JavaScript"""
        name = str(method.get("name", ""))
        class_name = self._get_method_class(method)
        params = self._create_full_params(method)
        method_type = self._get_method_type(method)
        line_range = method.get("line_range", {})
        lines_str = f"{line_range.get('start', 0)}-{line_range.get('end', 0)}"
        complexity = method.get("complexity_score", 0)
        doc = self._clean_csv_text(
            self._extract_doc_summary(str(method.get("jsdoc", "")))
        )

        return f"| {name} | {class_name} | {params} | {method_type} | {lines_str} | {complexity} | {doc} |"

    def _create_full_params(self, func: dict[str, Any]) -> str:
        """Create full parameter list for JavaScript functions"""
        params = func.get("parameters", [])
        if not params:
            return "()"

        param_strs = []
        for param in params:
            if isinstance(param, dict):
                param_name = param.get("name", "")
                param_type = param.get("type", "")
                if param_type:
                    param_strs.append(f"{param_name}: {param_type}")
                else:
                    param_strs.append(param_name)
            else:
                param_strs.append(str(param))

        params_str = ", ".join(param_strs)
        if len(params_str) > 50:
            params_str = params_str[:47] + "..."

        return f"({params_str})"

    def _create_compact_params(self, func: dict[str, Any]) -> str:
        """Create compact parameter list for JavaScript functions"""
        params = func.get("parameters", [])
        if not params:
            return "()"

        param_count = len(params)
        if param_count <= 3:
            param_names = [
                param.get("name", str(param)) if isinstance(param, dict) else str(param)
                for param in params
            ]
            return f"({','.join(param_names)})"
        else:
            return f"({param_count} params)"

    def _get_function_type(self, func: dict[str, Any]) -> str:
        """Get full function type for JavaScript"""
        if func.get("is_async", False):
            return "async function"
        elif func.get("is_generator", False):
            return "generator"
        elif func.get("is_arrow", False):
            return "arrow"
        elif self._is_method(func):
            if func.get("is_constructor", False):
                return "constructor"
            elif func.get("is_getter", False):
                return "getter"
            elif func.get("is_setter", False):
                return "setter"
            elif func.get("is_static", False):
                return "static method"
            else:
                return "method"
        else:
            return "function"

    def _get_function_type_short(self, func: dict[str, Any]) -> str:
        """Get short function type for JavaScript"""
        if func.get("is_async", False):
            return "async"
        elif func.get("is_generator", False):
            return "gen"
        elif func.get("is_arrow", False):
            return "arrow"
        elif self._is_method(func):
            return "method"
        else:
            return "func"

    def _get_method_type(self, method: dict[str, Any]) -> str:
        """Get method type for JavaScript"""
        if method.get("is_constructor", False):
            return "constructor"
        elif method.get("is_getter", False):
            return "getter"
        elif method.get("is_setter", False):
            return "setter"
        elif method.get("is_static", False):
            return "static"
        elif method.get("is_async", False):
            return "async"
        else:
            return "method"

    def _is_method(self, func: dict[str, Any]) -> bool:
        """Check if function is a class method"""
        return func.get("is_method", False) or func.get("class_name") is not None

    def _get_method_class(self, method: dict[str, Any]) -> str:
        """Get the class name for a method"""
        return str(method.get("class_name", "Unknown"))

    def _infer_js_type(self, value: Any) -> str:
        """Infer JavaScript type from value"""
        if value is None:
            return "undefined"

        value_str = str(value).strip()

        # Check for specific patterns
        if (
            value_str.startswith('"')
            or value_str.startswith("'")
            or value_str.startswith("`")
        ):
            return "string"
        elif value_str in ["true", "false"]:
            return "boolean"
        elif value_str == "null":
            return "null"
        elif value_str.startswith("[") and value_str.endswith("]"):
            return "array"
        elif value_str.startswith("{") and value_str.endswith("}"):
            return "object"
        elif value_str.startswith("function") or "=>" in value_str:
            return "function"
        elif value_str.startswith("class"):
            return "class"
        elif value_str.replace(".", "").replace("-", "").isdigit():
            return "number"
        else:
            return "unknown"

    def _determine_scope(self, var: dict[str, Any]) -> str:
        """Determine variable scope"""
        # This would need more context from the parser
        # For now, return basic scope info
        kind = self._get_variable_kind(var)
        if kind == "const":
            return "block"
        elif kind == "let":
            return "block"
        elif kind == "var":
            return "function"
        else:
            return "unknown"

    def _get_variable_kind(self, var: dict[str, Any]) -> str:
        """Get variable declaration kind (const, let, var)"""
        # Check if variable has is_constant flag
        if var.get("is_constant", False):
            return "const"

        # Fall back to parsing raw text
        raw_text = str(var.get("raw_text", "")).strip()
        if raw_text.startswith("const"):
            return "const"
        elif raw_text.startswith("let"):
            return "let"
        elif raw_text.startswith("var"):
            return "var"
        else:
            return "unknown"

    def _get_export_type(self, export: dict[str, Any]) -> str:
        """Get export type"""
        if export.get("is_default", False):
            return "default"
        elif export.get("is_named", False):
            return "named"
        elif export.get("is_all", False):
            return "all"
        else:
            return "unknown"
