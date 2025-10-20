"""Base classes for implementing linting rules."""

import re
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from ..core.issue import LintIssue
from ..core.severity import Severity
from .rule_id import RuleId


class AutofixResult:
    """Result of an autofix operation."""

    def __init__(
        self,
        success: bool,
        new_content: str = "",
        message: str = "",
        issues_fixed: int = 0,
    ):
        self.success = success
        self.new_content = new_content
        self.message = message
        self.issues_fixed = issues_fixed


class BaseRule(ABC):
    """Abstract base class for all linting rules.

    Each rule implementation must inherit from this class and implement
    the check method. Rules have access to the AST tree, file content,
    and configuration to perform their analysis.

    Rules can optionally implement autofix capability by overriding
    the autofix method.
    """

    def __init__(self, rule_id: Optional[RuleId], severity: Severity):
        self.rule_id = rule_id
        self.severity = severity
        self.issues: List[LintIssue] = []
        self.supports_autofix = (
            False  # Override in subclasses that support autofix
        )

    @abstractmethod
    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        """Perform the rule check on the given file.

        Args:
            file_path: Path to the file being analyzed
            content: Full content of the file
            tree: Tree-sitter AST tree for the file
            config: Linter configuration object

        Returns:
            List of issues found by this rule
        """

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        """Apply automatic fixes for issues found by this rule.

        Args:
            file_path: Path to the file being fixed
            content: Full content of the file
            tree: Tree-sitter AST tree for the file
            config: Linter configuration object
            issues: List of issues found by this rule

        Returns:
            AutofixResult with success status and fixed content
        """
        # Default implementation - no autofix support
        return AutofixResult(
            success=False,
            message=f"Rule {self.rule_id} does not support autofix",
        )

    def add_issue(
        self,
        file_path: str,
        line_number: int,
        column: int,
        message: str,
        suggested_fix: Optional[str] = None,
    ) -> None:
        """Helper method to add an issue."""
        # For plugin rules, use the plugin_rule_id if available
        if hasattr(self, "plugin_rule_id") and self.plugin_rule_id:
            rule_id_str = self.plugin_rule_id
        else:
            rule_id_str = str(self.rule_id)

        issue = LintIssue(
            file_path=file_path,
            line_number=line_number,
            column=column,
            severity=self.severity,
            rule_id=rule_id_str,
            message=message,
            suggested_fix=suggested_fix,
        )
        self.issues.append(issue)

    def has_file_level_disable(self, content: str, rule_id: str) -> bool:
        """Check if file has a file-level disable directive for this rule.
        
        File-level directives must be on their own line (not inline comments).
        Format: // niti-file-disable rule-id
        
        This prevents confusion with inline NOLINT comments which are for
        line-level suppression.
        """
        lines = content.split('\n')
        for line in lines[:50]:  # Check first 50 lines for file-level directives
            line_stripped = line.strip()
            if line_stripped == f"// niti-file-disable {rule_id}":
                return True
        return False

    def should_skip_line(self, line_content: str, rule_id: str) -> bool:
        """Check if a line should be skipped based on NOLINT comments."""
        line_stripped = line_content.strip()

        # Check for rule-specific skip directive first (more specific)
        if f"// NOLINT {rule_id}" in line_content:
            return True

        # Check for multiple rule skip with comma-separated list
        if "// NOLINT " in line_content:
            # Extract the rules list after "// NOLINT "
            import re
            # Match rule names (letters, numbers, hyphens) followed by optional whitespace or comments
            match = re.search(r"// NOLINT\s+([a-zA-Z0-9_-]+(?:,[a-zA-Z0-9_-]+)*)", line_content)
            if match:
                rules_text = match.group(1).strip()
                disabled_rules = [r.strip() for r in rules_text.split(",")]
                if rule_id in disabled_rules or "all" in disabled_rules:
                    return True
                return False  # If there are specific rules, don't do general skip
            # If NOLINT has space but no valid rules, treat as general NOLINT

        # Check for general skip directive (NOLINT with no specific rules or with space but no valid rules)
        if "// NOLINT" in line_content:
            return True

        return False

    def should_skip_next_line(
        self, content: str, line_num: int
    ) -> tuple[bool, str]:
        """Check if the next line should be skipped based on NOLINTNEXTLINE."""
        if line_num <= 1:
            return False, ""

        lines = content.split("\n")
        if line_num - 2 < 0 or line_num - 2 >= len(lines):
            return False, ""

        prev_line = lines[line_num - 2]  # line_num is 1-indexed

        if "// NOLINTNEXTLINE" in prev_line:
            # Extract specific rules if any
            import re
            
            # Check if there are specific rules after NOLINTNEXTLINE
            if "// NOLINTNEXTLINE " in prev_line:
                match = re.search(r"// NOLINTNEXTLINE\s+(.+?)(?://|$)", prev_line)
                if match:
                    return True, match.group(1).strip()
            
            # General NOLINTNEXTLINE (no specific rules)
            return True, "all"

        return False, ""

    def get_text_from_node(self, node: Any, content: str) -> str:
        """Extract text content from a tree-sitter node."""
        # Tree-sitter uses byte offsets, but Python strings use character offsets
        # We need to convert byte offsets to character offsets for UTF-8 content
        content_bytes = content.encode('utf-8')
        node_bytes = content_bytes[node.start_byte : node.end_byte]
        return node_bytes.decode('utf-8', errors='replace')

    def get_line_from_byte(self, byte_offset: int, content: str) -> int:
        """Convert byte offset to line number (1-indexed)."""
        # Tree-sitter uses byte offsets, we need to handle UTF-8 properly
        content_bytes = content.encode('utf-8')
        bytes_before = content_bytes[:byte_offset]
        text_before = bytes_before.decode('utf-8', errors='replace')
        return text_before.count("\n") + 1

    def get_line(self, content: str, line_num: int) -> str:
        """Get a specific line from content (1-indexed)."""
        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def regex_search(self, pattern: str, text: str) -> Optional[re.Match]:
        """Search for regex pattern in text."""
        try:
            return re.search(pattern, text)
        except re.error:
            return None

    # ------------------------------------------------------------------
    #  Lightweight parser-sanity guard
    # ------------------------------------------------------------------

    def _is_parsing_corrupted(self, tree: Any, content: str) -> bool:
        """Heuristic: return True when the tree looks clearly broken.

        We sample up to ~50 identifier / literal nodes and verify their byte
        ranges lie within file bounds and that the extracted text roughly
        matches the node type.  This is **far** cheaper than a full walk and
        avoids earlier heavyweight logic that incurred unnecessary cost.
        """
        max_samples = 50
        samples = 0
        bad = 0

        def visit(node):
            nonlocal samples, bad
            if samples >= max_samples:
                return

            # Only sample identifiers & primitive literals – easy sanity check.
            if node.type in {"identifier", "number_literal", "primitive_type"}:
                samples += 1
                if node.start_byte >= len(content) or node.end_byte > len(
                    content
                ):
                    bad += 1
                    return
                text = content[node.start_byte : node.end_byte]
                if node.type == "identifier" and not text:
                    bad += 1
                elif node.type == "number_literal" and not text.isdigit():
                    bad += 1

            for child in node.children:
                visit(child)

        visit(tree.root_node)

        # Consider parse corrupted if more than 40% of sampled nodes are bad
        return samples > 0 and bad / samples > 0.4


class ASTRule(BaseRule):
    """Base class for rules that analyze the AST structure.

    Provides helper methods for traversing and analyzing tree-sitter AST nodes.
    """

    def find_nodes_by_type(self, tree: Any, node_type: str) -> List[Any]:
        """Find all nodes of a specific type in the AST."""
        nodes = []

        def visit(node):
            if node.type == node_type:
                nodes.append(node)
            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return nodes

    def find_nodes_by_types(
        self, tree: Any, node_types: List[str]
    ) -> List[Any]:
        """Find all nodes matching any of the specified types."""
        nodes = []

        def visit(node):
            if node.type in node_types:
                nodes.append(node)
            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return nodes

    def get_parent_of_type(self, node: Any, parent_type: str) -> Optional[Any]:
        """Find the first parent node of the specified type."""
        current = node.parent
        while current:
            if current.type == parent_type:
                return current
            current = current.parent
        return None

    def is_inside_comment(self, node: Any, content: str) -> bool:
        """Check if a node is inside a comment."""
        line_start = content.rfind("\n", 0, node.start_byte) + 1
        line_end = content.find("\n", node.start_byte)
        if line_end == -1:
            line_end = len(content)

        line_content = content[line_start:line_end]
        node_offset = node.start_byte - line_start

        # Check for // comment
        comment_pos = line_content.find("//")
        if comment_pos != -1 and comment_pos < node_offset:
            return True

        return False

    # ------------------------------------------------------------------
    # Shared C++-specific helper utilities (centralised here so that every
    # rule can rely on a single, battle-tested implementation instead of
    # re-implementing its own variants).
    # ------------------------------------------------------------------

    # Common built-in or STL-alias type tokens that should be ignored when
    # heuristically searching for a function name in raw text.
    _COMMON_TYPE_NAMES: set[str] = {
        "void",
        "bool",
        "char",
        "wchar_t",
        "char8_t",
        "char16_t",
        "char32_t",
        "float",
        "double",
        "long",
        "short",
        "signed",
        "unsigned",
        "auto",
        "size_t",
        "std::size_t",
        "int8_t",
        "int16_t",
        "int32_t",
        "int64_t",
        "uint8_t",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "string",
        "std::string",
        "shared_ptr",
        "unique_ptr",
        "vector",
        "map",
        "set",
    }

    # Widely recognised C/C++ keywords.  Exposed so that all rules share the
    # exact same whitelist / blacklist logic rather than hard-coding their own
    # reduced variants.
    _CPP_KEYWORDS: set[str] = {
        # storage class / type qualifiers
        "const",
        "static",
        "constexpr",
        "volatile",
        "mutable",
        "register",
        "inline",
        "extern",
        "thread_local",
        # compound type specifiers
        "class",
        "struct",
        "union",
        "enum",
        "typename",
        "template",
        "using",
        # fundamental types
        "void",
        "bool",
        "char",
        "wchar_t",
        "char8_t",
        "char16_t",
        "char32_t",
        "short",
        "int",
        "long",
        "float",
        "double",
        "signed",
        "unsigned",
        # control flow / operators
        "if",
        "else",
        "switch",
        "case",
        "break",
        "continue",
        "return",
        "for",
        "while",
        "do",
        "goto",
        "sizeof",
        "alignof",
        "decltype",
        # misc
        "namespace",
        "public",
        "private",
        "protected",
        "friend",
        "operator",
        "this",
        "nullptr",
        "new",
        "delete",
        "try",
        "catch",
        "throw",
    }

    # -------------------------------
    #  Identifier utility helpers
    # -------------------------------

    def is_keyword(self, ident: str) -> bool:
        """Return True if *ident* is a C++ keyword/qualifier."""
        return ident in self._CPP_KEYWORDS

    def is_type_name(self, ident: str) -> bool:
        """Heuristic: does *ident* look like a type (class/struct/alias)?"""
        if not ident:
            return False

        # Fully qualified types (std::string, namespace::Type, etc.)
        if "::" in ident:
            return True

        # Known built-in and common STL types
        if ident in self._COMMON_TYPE_NAMES:
            return True

        # Template instantiations (vector<int>, map<string, int>, etc.)
        if "<" in ident and ">" in ident:
            return True

        # C++ convention: PascalCase typically indicates user-defined types
        if self._is_pascalcase_type_pattern(ident):
            return True

        # Short uppercase identifiers (2-4 chars) often used for type aliases
        # Examples: ID, UI, DB, API, URL, JSON, XML, etc.
        if ident.isupper() and 2 <= len(ident) <= 4:
            return True

        # Identifiers ending with common type indicators
        # This catches types like MyCallback, EventHandler, etc.
        type_indicators = (
            "Callback",
            "Handler",
            "Listener",
            "Observer",
            "Visitor",
            "Factory",
            "Builder",
            "Manager",
            "Controller",
            "Service",
            "Provider",
            "Adapter",
            "Wrapper",
            "Iterator",
            "Comparator",
        )
        if any(ident.endswith(indicator) for indicator in type_indicators):
            return True

        return False

    def _is_pascalcase_type_pattern(self, ident: str) -> bool:
        """Check if identifier follows PascalCase pattern typical of types."""
        if len(ident) < 2:
            return False

        # Must start with uppercase
        if not ident[0].isupper():
            return False

        # Exclude ALL_CAPS (typically constants/macros)
        if ident.isupper():
            return False

        # Exclude kConstant naming pattern (Google style constants)
        if ident.startswith("k") and len(ident) > 1 and ident[1].isupper():
            return False

        # Exclude common non-type patterns
        non_type_prefixes = ("get", "set", "is", "has", "can", "should", "will")
        if any(
            ident.lower().startswith(prefix) for prefix in non_type_prefixes
        ):
            return False

        # Be more conservative - only consider it a type if it has additional indicators
        # This reduces false positives where PascalCase variables are misidentified as types

        # Strong type indicators (common patterns in type names)
        type_indicators = (
            # Common type suffixes
            "Type",
            "Ptr",
            "Ref",
            "Class",
            "Struct",
            "Enum",
            "Interface",
            # Design pattern suffixes
            "Factory",
            "Builder",
            "Manager",
            "Controller",
            "Handler",
            "Service",
            "Provider",
            "Adapter",
            "Wrapper",
            "Iterator",
            "Comparator",
            "Observer",
            "Visitor",
            "Strategy",
            "Command",
            "State",
            # Data structure suffixes
            "List",
            "Map",
            "Set",
            "Queue",
            "Stack",
            "Tree",
            "Node",
            "Graph",
            # Other common type endings
            "Config",
            "Settings",
            "Options",
            "Info",
            "Data",
            "Model",
            "Entity",
        )

        # Check if it ends with a known type indicator
        if any(ident.endswith(indicator) for indicator in type_indicators):
            return True

        # Short PascalCase (3 chars or less) more likely to be type abbreviations
        if len(ident) <= 3:
            return True

        # Conservative approach: require additional context for longer PascalCase
        # This prevents common variable names like "CountItems" from being treated as types
        return False

    # -------------------------------
    #  Function detection helpers
    # -------------------------------
    def _is_function_node(self, node: Any, content: str) -> bool:
        """Check if a node represents a function declaration (not a variable declaration).
        
        Distinguishes between:
        - Function declarations: void DoSomething();
        - Variable declarations with constructors: MyClass obj(args);
        
        Both can have function_declarator nodes in the AST (the "most vexing parse"),
        so we check the parent context to differentiate them.
        """
        # Function declarations and definitions are always functions
        if node.type in ["function_declaration", "function_definition"]:
            return True

        # For field_declaration and declaration nodes, check if they have function_declarator
        # BUT also check they're not local variable declarations inside function bodies
        has_function_declarator = False
        for child in node.children:
            if child.type == "function_declarator":
                has_function_declarator = True
                break

        if not has_function_declarator:
            return False

        # EXCLUDE: Local variable declarations inside function bodies
        # Check if parent is a compound_statement (function body) or declaration_list (inside function)
        parent = node.parent
        while parent:
            if parent.type in ["compound_statement", "declaration_list"]:
                # This is a local variable declaration, not a function
                return False
            # Stop at function definition or class boundary
            if parent.type in ["function_definition", "class_specifier", "namespace_definition", "translation_unit"]:
                break
            parent = parent.parent

        return True

    # -------------------------------
    #  Name-extraction helpers
    # -------------------------------
    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            # Try multiple strategies to find function name

            # Strategy 1: Look for function_declarator child
            for child in func_node.children:
                if child.type == "function_declarator":
                    # Check for operator overload - look at all children before parameter_list
                    operator_name = None
                    for subchild in child.children:
                        if subchild.type == "parameter_list":
                            break
                        # Tree-sitter may represent operator as "operator" node or as a sequence
                        if subchild.type in ("operator", "operator_name"):
                            operator_text = self.get_text_from_node(subchild, content).strip()
                            # Remove any trailing parenthesis
                            operator_text = operator_text.rstrip('(').strip()
                            return operator_text
                    
                    # Regular function - look for identifier
                    for subchild in child.children:
                        if subchild.type == "identifier":
                            return self.get_text_from_node(subchild, content)

            # Strategy 2: Look for direct identifier children
            for child in func_node.children:
                if child.type == "identifier":
                    return self.get_text_from_node(child, content)

            # Strategy 3: Parse the text directly to extract function name (This is what is used generally)
            func_text = self.get_text_from_node(func_node, content)
            lines = func_text.split("\n")
            for line in lines:
                # Look for function declaration patterns
                import re

                # Check for operator overload first (before cleaning)
                # Match: operator followed by operator symbols, but stop before opening paren
                operator_match = re.search(r'\boperator\s*([+\-*/=<>!&|^%~\[\]]+)\s*\(', line)
                if operator_match:
                    return f"operator{operator_match.group(1)}"
                
                # Also handle operator() and similar cases
                operator_paren_match = re.search(r'\boperator\s*(\(\)|\[\])\s*\(', line)
                if operator_paren_match:
                    return f"operator{operator_paren_match.group(1)}"

                # Clean up the line - remove attributes and qualifiers
                clean_line = line.strip()
                clean_line = re.sub(
                    r"\[\[.*?\]\]", "", clean_line
                )  # Remove [[nodiscard]] etc
                clean_line = re.sub(r"\bvirtual\b", "", clean_line)
                clean_line = re.sub(r"\bstatic\b", "", clean_line)
                clean_line = re.sub(r"\bconst\b", "", clean_line)
                clean_line = re.sub(r"\binline\b", "", clean_line)
                clean_line = re.sub(r"\bexplicit\b", "", clean_line)
                clean_line = re.sub(r"\boverride\b", "", clean_line)
                clean_line = re.sub(r"\bfinal\b", "", clean_line)

                # Try multiple patterns to find function name
                patterns = [
                    r"(?:std::)?(?:\w+)?\s+(\w+)\s*\(",  # return_type name(
                    r"(\w+)\s*\(",  # Simple name(
                ]

                for pattern in patterns:
                    match = re.search(pattern, clean_line)
                    if match:
                        potential_name = match.group(1)
                        # Skip common type keywords
                        if potential_name not in [
                            "string",
                            "int",
                            "bool",
                            "void",
                            "auto",
                            "size_t",
                            "uint32_t",
                            "shared_ptr",
                            "unique_ptr",
                            "vector",
                            "map",
                            "set",
                            "char",
                        ]:
                            return potential_name

            return "unknown"
        except Exception:
            return "unknown"

    def extract_function_name(self, func_node: Any, content: str) -> str:
        """Return the unqualified function name for a declaration/definition."""
        try:
            # Strategy 1: inspect the top-level children of function_declarator
            # – the first identifier there is the function name.
            for child in func_node.children:
                if child.type == "function_declarator":
                    # Check for operator overload first using regex on the text
                    func_text = self.get_text_from_node(child, content)
                    import re
                    
                    # Match: operator followed by operator symbols, but stop before opening paren
                    operator_match = re.search(r'\boperator\s*([+\-*/=<>!&|^%~\[\]]+)\s*\(', func_text)
                    if operator_match:
                        return f"operator{operator_match.group(1)}"
                    
                    # Also handle operator() and similar cases
                    operator_paren_match = re.search(r'\boperator\s*(\(\)|\[\])\s*\(', func_text)
                    if operator_paren_match:
                        return f"operator{operator_paren_match.group(1)}"
                    
                    # Check for operator overload via AST nodes
                    for grand in child.children:
                        if grand.type in ("operator", "operator_name"):
                            # Get the full operator text (e.g., "operator=", "operator+", etc.)
                            operator_text = self.get_text_from_node(grand, content)
                            # Clean up: remove any trailing opening parenthesis that might have been captured
                            operator_text = operator_text.strip().rstrip('(').strip()
                            return operator_text
                    
                    # Sequential scan until parameter_list; the last identifier
                    # encountered before the parameter list is the function
                    # name (per C++ grammar).
                    cand = None
                    for grand in child.children:
                        if grand.type == "parameter_list":
                            break
                        if grand.type == "identifier":
                            token = self.get_text_from_node(grand, content)
                            if not self.is_type_name(token):
                                cand = token
                    if cand:
                        return cand
                    # Else fallback to deeper search (rare macros)
                    stack = [child]
                    while stack:
                        node = stack.pop()
                        if node.type == "parameter_list":
                            continue
                        stack.extend(node.children)
                        if node.type == "identifier":
                            token = self.get_text_from_node(node, content)
                            if not self.is_type_name(token):
                                cand = token
                    if cand:
                        return cand
        except Exception:
            pass
        return "unknown"

    def _get_doxygen_comment(self, class_node: Any, content: str) -> str:
        """Get Doxygen comment before class."""
        try:
            class_start_line = class_node.start_point[0]
            lines = content.split("\n")

            comment_lines = []
            in_comment = False

            # Look at lines before the class, searching backwards for the closest comment
            for i in range(
                class_start_line - 1, max(0, class_start_line - 50) - 1, -1
            ):
                if i < len(lines):
                    line = lines[i].strip()
                    if "*/" in line:
                        if not in_comment:
                            in_comment = True
                            comment_lines.insert(0, line)
                        else:
                            comment_lines.insert(0, line)
                            break
                    elif in_comment:
                        comment_lines.insert(0, line)
                        if "/**" in line:
                            break
                    elif line == "":
                        # Empty line - continue looking
                        continue
                    else:
                        # Non-empty, non-comment line - stop looking
                        break

            return "\n".join(comment_lines)
        except Exception:
            return ""


    # -------------------------------
    #  Parameter helpers
    # -------------------------------

    def extract_parameter_names(
        self, func_node: Any, content: str
    ) -> list[str]:
        """Return a list of parameter identifiers for *func_node*."""
        names: list[str] = []
        try:
            # Locate the function_declarator node (may be nested in pointer_declarator)
            func_declarator = self._find_function_declarator(func_node)
            if not func_declarator:
                return names

            # Find the parameter_list
            param_list = None
            for child in func_declarator.children:
                if child.type == "parameter_list":
                    param_list = child
                    break

            if not param_list:
                return names

            # DFS to capture the *last* identifier within each parameter decl.
            for param in param_list.children:
                if param.type not in (
                    "parameter_declaration",
                    "optional_parameter_declaration",
                ):
                    continue
                last_id: str | None = None
                stack = list(param.children)
                while stack:
                    node = stack.pop()
                    # Skip attribute nodes (like [[maybe_unused]]) to avoid capturing attribute identifiers
                    if node.type in ("attribute_declaration", "attribute_specifier", "attribute"):
                        continue
                    if node.type == "identifier":
                        last_id = self.get_text_from_node(node, content)
                    # Only traverse children if not an attribute node
                    if node.type not in ("attribute_declaration", "attribute_specifier", "attribute"):
                        stack.extend(node.children)
                if last_id:
                    names.append(last_id)
        except Exception:
            pass
        return names

    def has_unnamed_parameters(self, func_node: Any, content: str) -> bool:
        """Check if function has any unnamed parameters (parameters with type but no name).
        
        In C++, parameters can be declared without names (e.g., void foo(int) { }), 
        which is common for unused parameters in overrides.
        """
        try:
            # Locate the function_declarator node
            func_declarator = self._find_function_declarator(func_node)
            if not func_declarator:
                return False

            # Find the parameter_list
            param_list = None
            for child in func_declarator.children:
                if child.type == "parameter_list":
                    param_list = child
                    break

            if not param_list:
                return False

            # Check each parameter declaration
            for param in param_list.children:
                if param.type not in (
                    "parameter_declaration",
                    "optional_parameter_declaration",
                ):
                    continue
                
                # Check if this parameter has an identifier (name)
                has_identifier = False
                stack = list(param.children)
                while stack:
                    node = stack.pop()
                    # Skip attribute nodes
                    if node.type in ("attribute_declaration", "attribute_specifier", "attribute"):
                        continue
                    if node.type == "identifier":
                        # Check if this identifier is a type or a parameter name
                        # Type identifiers are typically children of type_identifier, qualified_identifier, etc.
                        # Parameter names are typically direct children of parameter_declaration
                        # A simple heuristic: if we find any identifier at the "parameter name" position, 
                        # the parameter is named
                        has_identifier = True
                        break
                    if node.type not in ("attribute_declaration", "attribute_specifier", "attribute"):
                        stack.extend(node.children)
                
                # If we found a parameter declaration but no identifier was found, it's unnamed
                if not has_identifier:
                    return True
            
            return False
        except Exception:
            return False

    def _find_function_declarator(self, node: Any) -> Any:
        """Recursively find function_declarator node.
        
        function_declarator may be nested inside pointer_declarator or reference_declarator
        when the function returns a pointer or reference.
        """
        if node.type == "function_declarator":
            return node
        for child in node.children:
            result = self._find_function_declarator(child)
            if result:
                return result
        return None

    # -------------------------------
    #  Comment helpers
    # -------------------------------

    def preceding_doxygen_comment(
        self, node: Any, content: str, look_back_lines: int = 10
    ) -> str:
        """Return the raw text of the Doxygen block immediately before *node*."""
        try:
            start_line = node.start_point[0]
            lines = content.split("\n")
            comment_lines: list[str] = []
            in_block = False
            for i in range(max(0, start_line - look_back_lines), start_line):
                line = lines[i].strip()
                if "/**" in line or line.startswith("///"):
                    in_block = True
                if in_block:
                    comment_lines.append(line)
                    if "*/" in line:
                        break
            return "\n".join(comment_lines)
        except Exception:
            return ""

    # -------------------------------
    #  Simple tag regex helpers
    # -------------------------------

    @staticmethod
    def parse_param_tags(doc_comment: str) -> set[str]:
        import re as _re

        return set(_re.findall(r"@param\s+(\w+)", doc_comment, _re.IGNORECASE))

    # -------------------------------
    #  Misc heuristics
    # -------------------------------

    @staticmethod
    def is_destructor(func_name: str) -> bool:
        return func_name.startswith("~") if func_name else False

    @staticmethod
    def is_constructor(
        func_name: str, enclosing_class: str | None = None
    ) -> bool:
        if not func_name:
            return False
        if enclosing_class and func_name == enclosing_class:
            return True
        # Simple heuristic: PascalCase starting with uppercase and no return type.
        return func_name[0].isupper()


class RegexRule(BaseRule):
    """Base class for rules that use regex pattern matching.

    Useful for rules that need to check comments, string literals,
    or other patterns that are better handled with regex than AST traversal.
    """

    def get_lines(self, content: str) -> List[str]:
        """Split content into lines."""
        return content.splitlines()

    def is_in_string_literal(self, line: str, position: int) -> bool:
        """Check if a position in a line is inside a string literal."""
        quote_count = line[:position].count('"')
        return quote_count % 2 == 1

    def is_in_comment(self, line: str, position: int) -> bool:
        """Check if a position in a line is inside a comment."""
        comment_pos = line.find("//")
        return comment_pos != -1 and comment_pos < position
