# ============================================================================ #
#                                                                              #
#     Title: Docstring Format Checker Core Module                              #
#     Purpose: Core docstring checking functionality.                          #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Overview                                                              ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#  Description                                                              ####
# ---------------------------------------------------------------------------- #


"""
!!! note "Summary"
    Core docstring checking functionality.
"""


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import ast
import fnmatch
import re
from pathlib import Path
from typing import Iterator, Literal, NamedTuple, Optional, Union

# ## Local First Party Imports ----
from docstring_format_checker.config import Config, SectionConfig
from docstring_format_checker.utils.exceptions import (
    DirectoryNotFoundError,
    DocstringError,
    InvalidFileError,
)


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "DocstringChecker",
    "FunctionAndClassDetails",
    "SectionConfig",
    "DocstringError",
]


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Section                                                          ####
#                                                                              #
# ---------------------------------------------------------------------------- #


class FunctionAndClassDetails(NamedTuple):
    """
    !!! note "Summary"
        Details about a function or class found in the AST.
    """

    item_type: Literal["function", "class", "method"]
    name: str
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
    lineno: int
    parent_class: Optional[str] = None


class DocstringChecker:
    """
    !!! note "Summary"
        Main class for checking docstring format and completeness.
    """

    def __init__(self, config: Config) -> None:
        """
        !!! note "Summary"
            Initialize the docstring checker.

        Params:
            config (Config):
                Configuration object containing global settings and section definitions.
        """
        self.config: Config = config
        self.sections_config: list[SectionConfig] = config.sections
        self.required_sections: list[SectionConfig] = [s for s in config.sections if s.required]
        self.optional_sections: list[SectionConfig] = [s for s in config.sections if not s.required]

    def check_file(self, file_path: Union[str, Path]) -> list[DocstringError]:
        """
        !!! note "Summary"
            Check docstrings in a Python file.

        Params:
            file_path (Union[str, Path]):
                Path to the Python file to check.

        Raises:
            (FileNotFoundError):
                If the file doesn't exist.
            (InvalidFileError):
                If the file is not a Python file.
            (UnicodeError):
                If the file can't be decoded.
            (SyntaxError):
                If the file contains invalid Python syntax.

        Returns:
            (list[DocstringError]):
                List of DocstringError objects for any validation failures.
        """

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix != ".py":
            raise InvalidFileError(f"File must be a Python file (.py): {file_path}")

        # Read and parse the file
        try:
            with open(file_path, encoding="utf-8") as f:
                content: str = f.read()
        except UnicodeDecodeError as e:
            raise UnicodeError(f"Cannot decode file {file_path}: {e}") from e

        try:
            tree: ast.Module = ast.parse(content)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in {file_path}: {e}") from e

        # Extract all functions and classes
        items: list[FunctionAndClassDetails] = self._extract_items(tree)

        # Check each item
        errors: list[DocstringError] = []
        for item in items:
            try:
                self._check_single_docstring(item, str(file_path))
            except DocstringError as e:
                errors.append(e)

        return errors

    def check_directory(
        self,
        directory_path: Union[str, Path],
        exclude_patterns: Optional[list[str]] = None,
    ) -> dict[str, list[DocstringError]]:
        """
        !!! note "Summary"
            Check docstrings in all Python files in a directory recursively.

        Params:
            directory_path (Union[str, Path]):
                Path to the directory to check.
            exclude_patterns (Optional[list[str]]):
                List of glob patterns to exclude.

        Raises:
            (FileNotFoundError):
                If the directory doesn't exist.
            (DirectoryNotFoundError):
                If the path is not a directory.

        Returns:
            (dict[str, list[DocstringError]]):
                Dictionary mapping file paths to lists of DocstringError objects.
        """

        directory_path = Path(directory_path)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not directory_path.is_dir():
            raise DirectoryNotFoundError(f"Path is not a directory: {directory_path}")

        python_files: list[Path] = list(directory_path.glob("**/*.py"))

        # Filter out excluded patterns
        if exclude_patterns:
            filtered_files: list[Path] = []
            for file_path in python_files:
                relative_path: Path = file_path.relative_to(directory_path)
                should_exclude = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(relative_path), pattern):
                        should_exclude = True
                        break
                if not should_exclude:
                    filtered_files.append(file_path)
            python_files = filtered_files

        # Check each file
        results: dict[str, list[DocstringError]] = {}
        for file_path in python_files:
            try:
                errors: list[DocstringError] = self.check_file(file_path)
                if errors:  # Only include files with errors
                    results[str(file_path)] = errors
            except (FileNotFoundError, ValueError, SyntaxError) as e:
                # Create a special error for file-level issues
                error = DocstringError(
                    message=str(e),
                    file_path=str(file_path),
                    line_number=0,
                    item_name="",
                    item_type="file",
                )
                results[str(file_path)] = [error]

        return results

    def _is_overload_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> bool:
        """
        !!! note "Summary"
            Check if a function definition is decorated with @overload.

        Params:
            node (Union[ast.FunctionDef, ast.AsyncFunctionDef]):
                The function node to check for @overload decorator.

        Returns:
            (bool):
                True if the function has @overload decorator, False otherwise.
        """

        for decorator in node.decorator_list:
            # Handle direct name reference: @overload
            if isinstance(decorator, ast.Name) and decorator.id == "overload":
                return True
            # Handle attribute reference: @typing.overload
            elif isinstance(decorator, ast.Attribute) and decorator.attr == "overload":
                return True
        return False

    def _extract_items(self, tree: ast.AST) -> list[FunctionAndClassDetails]:
        """
        !!! note "Summary"
            Extract all functions and classes from the AST.

        Params:
            tree (ast.AST):
                The Abstract Syntax Tree (AST) to extract items from.

        Returns:
            (list[FunctionAndClassDetails]):
                A list of extracted function and class details.
        """

        items: list[FunctionAndClassDetails] = []

        class ItemVisitor(ast.NodeVisitor):
            """
            !!! note "Summary"
                AST visitor to extract function and class definitions
            """

            def __init__(self, checker: DocstringChecker) -> None:
                """
                !!! note "Summary"
                    Initialize the AST visitor.
                """
                self.class_stack: list[str] = []
                self.checker: DocstringChecker = checker

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                """
                !!! note "Summary"
                    Visit class definition node.
                """
                # Skip private classes unless check_private is enabled
                should_check: bool = self.checker.config.global_config.check_private or not node.name.startswith("_")
                if should_check:
                    items.append(
                        FunctionAndClassDetails(
                            item_type="class",
                            name=node.name,
                            node=node,
                            lineno=node.lineno,
                            parent_class=None,
                        )
                    )

                # Visit methods in this class
                self.class_stack.append(node.name)
                self.generic_visit(node)
                self.class_stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                """
                !!! note "Summary"
                    Visit function definition node.
                """
                self._visit_function(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                """
                !!! note "Summary"
                    Visit async function definition node.
                """
                self._visit_function(node)

            def _visit_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
                """
                !!! note "Summary"
                    Visit function definition node (sync or async).
                """

                # Skip private functions unless check_private is enabled
                should_check: bool = self.checker.config.global_config.check_private or not node.name.startswith("_")
                if should_check:
                    # Skip @overload functions - they don't need docstrings
                    if not self.checker._is_overload_function(node):
                        item_type: Literal["function", "method"] = "method" if self.class_stack else "function"
                        parent_class: Optional[str] = self.class_stack[-1] if self.class_stack else None

                        items.append(
                            FunctionAndClassDetails(
                                item_type=item_type,
                                name=node.name,
                                node=node,
                                lineno=node.lineno,
                                parent_class=parent_class,
                            )
                        )

                self.generic_visit(node)

        visitor = ItemVisitor(self)
        visitor.visit(tree)

        return items

    def _check_single_docstring(self, item: FunctionAndClassDetails, file_path: str) -> None:
        """
        !!! note "Summary"
            Check a single function or class docstring.

        Params:
            item (FunctionAndClassDetails):
                The function or class to check.
            file_path (str):
                The path to the file containing the item.

        Returns:
            (None):
                Nothing is returned.
        """

        docstring: Optional[str] = ast.get_docstring(item.node)

        # Check if any required sections apply to this item type
        requires_docstring = False
        applicable_sections: list[SectionConfig] = []

        for section in self.sections_config:
            if section.required:
                # Check if this section applies to this item type
                if section.type == "free_text":
                    # Free text sections apply only to functions and methods, not classes
                    if isinstance(item.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        requires_docstring = True
                        applicable_sections.append(section)
                elif section.type == "list_name_and_type":
                    if section.name.lower() == "params" and isinstance(
                        item.node, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):
                        # Params only apply to functions/methods
                        requires_docstring = True
                        applicable_sections.append(section)
                    elif section.name.lower() in ["returns", "return"] and isinstance(
                        item.node, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):
                        # Returns only apply to functions/methods
                        requires_docstring = True
                        applicable_sections.append(section)
                elif section.type in ["list_type", "list_name"]:
                    # These sections apply to functions/methods that might have them
                    if isinstance(item.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        requires_docstring = True
                        applicable_sections.append(section)

        if not docstring:
            # Only require docstrings if the global flag is enabled
            if requires_docstring and self.config.global_config.require_docstrings:
                message: str = f"Missing docstring for {item.item_type}"
                raise DocstringError(
                    message=message,
                    file_path=file_path,
                    line_number=item.lineno,
                    item_name=item.name,
                    item_type=item.item_type,
                )
            return  # No docstring required or docstring requirement disabled

        # Validate docstring sections if docstring exists
        self._validate_docstring_sections(docstring, item, file_path)

    def _validate_docstring_sections(
        self,
        docstring: str,
        item: FunctionAndClassDetails,
        file_path: str,
    ) -> None:
        """
        !!! note "Summary"
            Validate the sections within a docstring.

        Params:
            docstring (str):
                The docstring to validate.
            item (FunctionAndClassDetails):
                The function or class to check.
            file_path (str):
                The path to the file containing the item.

        Returns:
            (None):
                Nothing is returned.
        """
        errors: list[str] = []

        # Validate required sections
        required_section_errors = self._validate_all_required_sections(docstring, item)
        errors.extend(required_section_errors)

        # Perform comprehensive validation checks
        comprehensive_errors = self._perform_comprehensive_validation(docstring)
        errors.extend(comprehensive_errors)

        # Report errors if found
        if errors:
            combined_message: str = "; ".join(errors)
            raise DocstringError(
                message=combined_message,
                file_path=file_path,
                line_number=item.lineno,
                item_name=item.name,
                item_type=item.item_type,
            )

    def _validate_all_required_sections(self, docstring: str, item: FunctionAndClassDetails) -> list[str]:
        """Validate all required sections are present and valid."""
        errors: list[str] = []

        for section in self.required_sections:
            section_error = self._validate_single_required_section(docstring, section, item)
            if section_error:
                errors.append(section_error)

        return errors

    def _validate_single_required_section(
        self, docstring: str, section: SectionConfig, item: FunctionAndClassDetails
    ) -> Optional[str]:
        """Validate a single required section based on its type."""
        if section.type == "free_text":
            return self._validate_free_text_section(docstring, section)
        elif section.type == "list_name_and_type":
            return self._validate_list_name_and_type_section(docstring, section, item)
        elif section.type == "list_type":
            return self._validate_list_type_section(docstring, section)
        elif section.type == "list_name":
            return self._validate_list_name_section(docstring, section)

        return None

    def _validate_free_text_section(self, docstring: str, section: SectionConfig) -> Optional[str]:
        """Validate free text sections."""
        if not self._check_free_text_section(docstring, section):
            return f"Missing required section: {section.name}"
        return None

    def _validate_list_name_and_type_section(
        self, docstring: str, section: SectionConfig, item: FunctionAndClassDetails
    ) -> Optional[str]:
        """Validate list_name_and_type sections (params, returns)."""
        section_name = section.name.lower()

        if section_name == "params" and isinstance(item.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not self._check_params_section(docstring, item.node):
                return "Missing or invalid Params section"
        elif section_name in ["returns", "return"]:
            if not self._check_returns_section(docstring):
                return "Missing or invalid Returns section"

        return None

    def _validate_list_type_section(self, docstring: str, section: SectionConfig) -> Optional[str]:
        """Validate list_type sections (raises, yields)."""
        section_name = section.name.lower()

        if section_name in ["raises", "raise"]:
            if not self._check_raises_section(docstring):
                return "Missing or invalid Raises section"
        elif section_name in ["yields", "yield"]:
            if not self._check_yields_section(docstring):
                return "Missing or invalid Yields section"

        return None

    def _validate_list_name_section(self, docstring: str, section: SectionConfig) -> Optional[str]:
        """Validate list_name sections."""
        if not self._check_simple_section(docstring, section.name):
            return f"Missing required section: {section.name}"
        return None

    def _perform_comprehensive_validation(self, docstring: str) -> list[str]:
        """Perform comprehensive validation checks on docstring."""
        errors: list[str] = []

        # Check section order
        order_errors = self._check_section_order(docstring)
        errors.extend(order_errors)

        # Check for mutual exclusivity (returns vs yields)
        if self._has_both_returns_and_yields(docstring):
            errors.append("Docstring cannot have both Returns and Yields sections")

        # Check for undefined sections (only if not allowed)
        if not self.config.global_config.allow_undefined_sections:
            undefined_errors = self._check_undefined_sections(docstring)
            errors.extend(undefined_errors)

        # Perform formatting validation
        formatting_errors = self._perform_formatting_validation(docstring)
        errors.extend(formatting_errors)

        return errors

    def _perform_formatting_validation(self, docstring: str) -> list[str]:
        """Perform formatting validation checks."""
        errors: list[str] = []

        # Check admonition values
        admonition_errors = self._check_admonition_values(docstring)
        errors.extend(admonition_errors)

        # Check colon usage
        colon_errors = self._check_colon_usage(docstring)
        errors.extend(colon_errors)

        # Check title case
        title_case_errors = self._check_title_case_sections(docstring)
        errors.extend(title_case_errors)

        # Check parentheses
        parentheses_errors = self._check_parentheses_validation(docstring)
        errors.extend(parentheses_errors)

        return errors

    def _check_free_text_section(self, docstring: str, section: SectionConfig) -> bool:
        """
        !!! note "Summary"
            Check if a free text section exists in the docstring.

        Params:
            docstring (str):
                The docstring to check.
            section (SectionConfig):
                The section configuration to validate.

        Returns:
            (bool):
                `True` if the section exists, `False` otherwise.
        """

        # Make the section name part case-insensitive too
        if isinstance(section.admonition, str) and section.admonition and section.prefix:
            # Format like: !!! note "Summary"
            escaped_name: str = re.escape(section.name)
            pattern: str = (
                rf'{re.escape(section.prefix)}\s+{re.escape(section.admonition)}\s+"[^"]*{escaped_name}[^"]*"'
            )
            return bool(re.search(pattern, docstring, re.IGNORECASE))

        # For summary, accept either formal format or simple docstring
        if section.name.lower() in ["summary"]:
            formal_pattern = r'!!! note "Summary"'
            if re.search(formal_pattern, docstring, re.IGNORECASE):
                return True
            # Accept any non-empty docstring as summary
            return len(docstring.strip()) > 0

        # Look for examples section
        elif section.name.lower() in ["examples", "example"]:
            return bool(re.search(r'\?\?\?\+ example "Examples"', docstring, re.IGNORECASE))

        # Default to true for unknown free text sections
        return True

    def _check_params_section(self, docstring: str, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> bool:
        """
        !!! note "Summary"
            Check if the Params section exists and documents all parameters.

        Params:
            docstring (str):
                The docstring to check.
            node (Union[ast.FunctionDef, ast.AsyncFunctionDef]):
                The function node to check.

        Returns:
            (bool):
                `True` if the section exists and is valid, `False` otherwise.
        """

        # Get function parameters (excluding 'self' for methods)
        params: list[str] = [arg.arg for arg in node.args.args if arg.arg != "self"]

        if not params:
            return True  # No parameters to document

        # Check if Params section exists
        if not re.search(r"Params:", docstring):
            return False

        # Check each parameter is documented
        for param in params:
            param_pattern: str = rf"{re.escape(param)}\s*\([^)]+\):"
            if not re.search(param_pattern, docstring):
                return False

        return True

    def _check_returns_section(self, docstring: str) -> bool:
        """
        !!! note "Summary"
            Check if the Returns section exists.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (bool):
                `True` if the section exists, `False` otherwise.
        """

        return bool(re.search(r"Returns:", docstring))

    def _check_raises_section(self, docstring: str) -> bool:
        """
        !!! note "Summary"
            Check if the Raises section exists.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (bool):
                `True` if the section exists, `False` otherwise.
        """

        return bool(re.search(r"Raises:", docstring))

    def _has_both_returns_and_yields(self, docstring: str) -> bool:
        """
        !!! note "Summary"
            Check if docstring has both Returns and Yields sections.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (bool):
                `True` if the section exists, `False` otherwise.
        """

        has_returns = bool(re.search(r"Returns:", docstring))
        has_yields = bool(re.search(r"Yields:", docstring))
        return has_returns and has_yields

    def _check_section_order(self, docstring: str) -> list[str]:
        """
        !!! note "Summary"
            Check that sections appear in the correct order.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (list[str]):
                A list of error messages, if any.
        """

        # Build expected order from configuration
        section_patterns: list[tuple[str, str]] = []
        for section in sorted(self.sections_config, key=lambda x: x.order):
            if (
                section.type == "free_text"
                and isinstance(section.admonition, str)
                and section.admonition
                and section.prefix
            ):
                pattern: str = (
                    rf'{re.escape(section.prefix)}\s+{re.escape(section.admonition)}\s+".*{re.escape(section.name)}"'
                )
                section_patterns.append((pattern, section.name))
            elif section.name.lower() == "params":
                section_patterns.append((r"Params:", "Params"))
            elif section.name.lower() in ["returns", "return"]:
                section_patterns.append((r"Returns:", "Returns"))
            elif section.name.lower() in ["yields", "yield"]:
                section_patterns.append((r"Yields:", "Yields"))
            elif section.name.lower() in ["raises", "raise"]:
                section_patterns.append((r"Raises:", "Raises"))

        # Add some default patterns for common sections
        default_patterns: list[tuple[str, str]] = [
            (r'!!! note "Summary"', "Summary"),
            (r'!!! details "Details"', "Details"),
            (r'\?\?\?\+ example "Examples"', "Examples"),
            (r'\?\?\?\+ success "Credit"', "Credit"),
            (r'\?\?\?\+ calculation "Equation"', "Equation"),
            (r'\?\?\?\+ info "Notes"', "Notes"),
            (r'\?\?\? question "References"', "References"),
            (r'\?\?\? tip "See Also"', "See Also"),
        ]

        all_patterns: list[tuple[str, str]] = section_patterns + default_patterns

        found_sections: list[tuple[int, str]] = []
        for pattern, section_name in all_patterns:
            match: Optional[re.Match[str]] = re.search(pattern, docstring, re.IGNORECASE)
            if match:
                found_sections.append((match.start(), section_name))

        # Sort by position in docstring
        found_sections.sort(key=lambda x: x[0])

        # Build expected order
        expected_order: list[str] = [s.name.title() for s in sorted(self.sections_config, key=lambda x: x.order)]
        expected_order.extend(
            [
                "Summary",
                "Details",
                "Examples",
                "Credit",
                "Equation",
                "Notes",
                "References",
                "See Also",
            ]
        )

        # Check order matches expected order
        errors: list[str] = []
        last_expected_index = -1
        for _, section_name in found_sections:
            try:
                current_index: int = expected_order.index(section_name)
                if current_index < last_expected_index:
                    errors.append(f"Section '{section_name}' appears out of order")
                last_expected_index: int = current_index
            except ValueError:
                # Section not in expected order list - might be OK
                pass

        return errors

    def _check_yields_section(self, docstring: str) -> bool:
        """
        !!! note "Summary"
            Check if the Yields section exists.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (bool):
                `True` if the section exists, `False` otherwise.
        """

        return bool(re.search(r"Yields:", docstring))

    def _check_simple_section(self, docstring: str, section_name: str) -> bool:
        """
        !!! note "Summary"
            Check if a simple named section exists.

        Params:
            docstring (str):
                The docstring to check.
            section_name (str):
                The name of the section to check for.

        Returns:
            (bool):
                `True` if the section exists, `False` otherwise.
        """

        pattern: str = rf"{re.escape(section_name)}:"
        return bool(re.search(pattern, docstring, re.IGNORECASE))

    def _check_undefined_sections(self, docstring: str) -> list[str]:
        """
        !!! note "Summary"
            Check for sections in docstring that are not defined in configuration.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (list[str]):
                A list of error messages for undefined sections.
        """

        errors: list[str] = []

        # Get all configured section names (case-insensitive)
        configured_sections: set[str] = {section.name.lower() for section in self.sections_config}

        # Common patterns for different section types
        section_patterns: list[tuple[str, str]] = [
            # Standard sections with colons (but not inside quotes)
            (r"^(\w+):\s*", "colon"),
            # Admonition sections with various prefixes
            (r"(?:\?\?\?[+]?|!!!)\s+\w+\s+\"([^\"]+)\"", "admonition"),
        ]

        found_sections: set[str] = set()

        for pattern, pattern_type in section_patterns:
            matches: Iterator[re.Match[str]] = re.finditer(pattern, docstring, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                section_name: str = match.group(1).lower().strip()

                # Remove colon if present (for colon pattern matches)
                section_name = section_name.rstrip(":")

                # Skip empty matches or common docstring content
                if not section_name or section_name in ["", "py", "python", "sh", "shell"]:
                    continue

                # Skip code blocks and inline code
                if any(char in section_name for char in ["`", ".", "/", "\\"]):
                    continue

                found_sections.add(section_name)

        # Check which found sections are not configured
        for section_name in found_sections:
            if section_name not in configured_sections:
                errors.append(f"Section '{section_name}' found in docstring but not defined in configuration")

        return errors

    def _check_admonition_values(self, docstring: str) -> list[str]:
        """
        !!! note "Summary"
            Check that admonition values in docstring match configuration.

        Params:
            docstring (str):
                The docstring to check.

        Returns:
            (list[str]):
                A list of error messages for mismatched admonitions.
        """

        errors: list[str] = []

        # Create mapping of section names to expected admonitions
        section_admonitions: dict[str, str] = {}
        for section in self.sections_config:
            if section.type == "free_text" and isinstance(section.admonition, str) and section.admonition:
                section_admonitions[section.name.lower()] = section.admonition.lower()

        # Pattern to find all admonition sections
        admonition_pattern = r"(?:\?\?\?[+]?|!!!)\s+(\w+)\s+\"([^\"]+)\""
        matches: Iterator[re.Match[str]] = re.finditer(admonition_pattern, docstring, re.IGNORECASE)

        for match in matches:
            actual_admonition: str = match.group(1).lower()
            section_title: str = match.group(2).lower()

            # Check if this section is configured with a specific admonition
            if section_title in section_admonitions:
                expected_admonition: str = section_admonitions[section_title]
                if actual_admonition != expected_admonition:
                    errors.append(
                        f"Section '{section_title}' has incorrect admonition '{actual_admonition}', "
                        f"expected '{expected_admonition}'"
                    )

            # Check if section shouldn't have admonition but does
            section_config: Optional[SectionConfig] = next(
                (s for s in self.sections_config if s.name.lower() == section_title), None
            )
            if section_config and section_config.admonition is False:
                errors.append(f"Section '{section_title}' is configured as non-admonition but found as admonition")

        return errors

    def _check_colon_usage(self, docstring: str) -> list[str]:
        """
        !!! note "Summary"
            Check that colons are used correctly for admonition vs non-admonition sections.
        """

        errors: list[str] = []

        # Check admonition sections (should not end with colon)
        admonition_pattern = r"(?:\?\?\?[+]?|!!!)\s+\w+\s+\"([^\"]+)\""
        matches: Iterator[re.Match[str]] = re.finditer(admonition_pattern, docstring, re.IGNORECASE)

        for match in matches:
            section_title: str = match.group(1)
            has_colon: bool = section_title.endswith(":")
            section_title_clean: str = section_title.rstrip(":").lower()

            # Find config for this section
            section_config: Optional[SectionConfig] = next(
                (s for s in self.sections_config if s.name.lower() == section_title_clean), None
            )
            if section_config and isinstance(section_config.admonition, str) and section_config.admonition:
                if has_colon:
                    errors.append(
                        f"Section '{section_title_clean}' is an admonition, therefore it should not end with ':', "
                        f"see: '{match.group(0)}'"
                    )

        # Check non-admonition sections (should end with colon)
        non_admonition_pattern = r"^(\w+)(:?)$"
        for line in docstring.split("\n"):
            line: str = line.strip()
            match: Optional[re.Match[str]] = re.match(non_admonition_pattern, line)
            if match:
                section_name: str = match.group(1).lower()
                has_colon: bool = match.group(2) == ":"

                # Find config for this section
                section_config = next((s for s in self.sections_config if s.name.lower() == section_name), None)
                if section_config and section_config.admonition is False:
                    if not has_colon:
                        errors.append(
                            f"Section '{section_name}' is non-admonition, therefore it must end with ':', "
                            f"see: '{line}'"
                        )

        return errors

    def _check_title_case_sections(self, docstring: str) -> list[str]:
        """
        !!! note "Summary"
            Check that non-admonition sections are single word, title case, and match config name.
        """

        errors: list[str] = []

        # Pattern to find section headers (single word followed by optional colon)
        section_pattern = r"^(\w+):?$"

        for line in docstring.split("\n"):
            line: str = line.strip()
            match: Optional[re.Match[str]] = re.match(section_pattern, line)
            if match:
                section_word: str = match.group(1)
                section_name_lower: str = section_word.lower()

                # Check if this is a configured non-admonition section
                section_config: Optional[SectionConfig] = next(
                    (s for s in self.sections_config if s.name.lower() == section_name_lower), None
                )
                if section_config and section_config.admonition is False:
                    # Check if it's title case
                    expected_title_case: str = section_config.name.title()
                    if section_word != expected_title_case:
                        errors.append(
                            f"Section '{section_name_lower}' must be in title case as '{expected_title_case}', "
                            f"found: '{section_word}'"
                        )

        return errors

    def _check_parentheses_validation(self, docstring: str) -> list[str]:
        """
        !!! note "Summary"
            Check that list_type and list_name_and_type sections have proper parentheses.
        """

        errors: list[str] = []

        # Get sections that require parentheses
        parentheses_sections: list[SectionConfig] = [
            s for s in self.sections_config if s.type in ["list_type", "list_name_and_type"]
        ]

        if not parentheses_sections:
            return errors

        # Process each line in the docstring
        lines: list[str] = docstring.split("\n")
        current_section: Optional[SectionConfig] = None
        type_line_indent: Optional[int] = None

        for line in lines:
            stripped_line: str = line.strip()

            # Check for any section header (to properly transition out of current section)
            section_detected: bool = self._detect_any_section_header(stripped_line, line)
            if section_detected:
                # Check if it's a parentheses-required section
                new_section: Optional[SectionConfig] = self._detect_section_header(
                    stripped_line, line, parentheses_sections
                )
                current_section = new_section  # None if not parentheses-required
                type_line_indent = None
                continue

            # Process content lines within parentheses-required sections
            if current_section and self._is_content_line(stripped_line):
                line_errors: list[str]
                new_indent: Optional[int]
                line_errors, new_indent = self._validate_parentheses_line(
                    line, stripped_line, current_section, type_line_indent
                )
                errors.extend(line_errors)
                if new_indent is not None:
                    type_line_indent = new_indent

        return errors

    def _detect_any_section_header(self, stripped_line: str, full_line: str) -> bool:
        """Detect any section header (for section transitions)."""
        # Admonition sections
        admonition_match: Optional[re.Match[str]] = re.match(
            r"(?:\?\?\?[+]?|!!!)\s+\w+\s+\"([^\"]+)\"", stripped_line, re.IGNORECASE
        )
        if admonition_match:
            section_name: str = admonition_match.group(1).lower()
            # Check if it's a known section
            return any(s.name.lower() == section_name for s in self.sections_config)

        # Non-admonition sections (must not be indented)
        if not full_line.startswith((" ", "\t")):
            simple_section_match: Optional[re.Match[str]] = re.match(r"^(\w+):?$", stripped_line)
            if simple_section_match:
                section_name: str = simple_section_match.group(1).lower()
                # Check if it's a known section
                return any(s.name.lower() == section_name for s in self.sections_config)

        return False

    def _detect_section_header(
        self, stripped_line: str, full_line: str, parentheses_sections: list[SectionConfig]
    ) -> Optional[SectionConfig]:
        """Detect section headers and return matching section config."""
        # Admonition sections
        admonition_match: Optional[re.Match[str]] = re.match(
            r"(?:\?\?\?[+]?|!!!)\s+\w+\s+\"([^\"]+)\"", stripped_line, re.IGNORECASE
        )
        if admonition_match:
            section_name: str = admonition_match.group(1).lower()
            return next((s for s in parentheses_sections if s.name.lower() == section_name), None)

        # Non-admonition sections (must not be indented)
        if not full_line.startswith((" ", "\t")):
            simple_section_match: Optional[re.Match[str]] = re.match(r"^(\w+):?$", stripped_line)
            if simple_section_match:
                section_name: str = simple_section_match.group(1).lower()
                # Check if it's a known section
                potential_section: Optional[SectionConfig] = next(
                    (s for s in self.sections_config if s.name.lower() == section_name), None
                )
                if potential_section:
                    return next((s for s in parentheses_sections if s.name.lower() == section_name), None)

        return None

    def _is_content_line(self, stripped_line: str) -> bool:
        """
        Check if line is content that needs validation.
        """
        return bool(stripped_line) and not stripped_line.startswith(("!", "?", "#")) and ":" in stripped_line

    def _is_description_line(self, stripped_line: str) -> bool:
        """
        Check if line is a description rather than a type definition.
        """
        description_prefixes: list[str] = [
            "default:",
            "note:",
            "example:",
            "see:",
            "warning:",
            "info:",
            "tip:",
            "returns:",
        ]

        return (
            any(stripped_line.lower().startswith(prefix) for prefix in description_prefixes)
            or "Default:" in stripped_line
            or "Output format:" in stripped_line
            or "Show examples:" in stripped_line
            or "Example code:" in stripped_line
            or stripped_line.strip().startswith(("-", "*", "•", "+"))
            or stripped_line.startswith(">>>")  # Doctest examples
        )

    def _validate_parentheses_line(
        self, full_line: str, stripped_line: str, current_section: SectionConfig, type_line_indent: Optional[int]
    ) -> tuple[list[str], Optional[int]]:
        """
        Validate a single line for parentheses requirements.
        """
        errors: list[str] = []
        new_indent: Optional[int] = None
        current_indent: int = len(full_line) - len(full_line.lstrip())

        # Skip description lines
        if self._is_description_line(stripped_line):
            return errors, type_line_indent

        if current_section.type == "list_type":
            errors, new_indent = self._validate_list_type_line(
                stripped_line, current_indent, type_line_indent, current_section
            )
        elif current_section.type == "list_name_and_type":
            errors, new_indent = self._validate_list_name_and_type_line(
                stripped_line, current_indent, type_line_indent, current_section
            )

        return errors, new_indent if new_indent is not None else type_line_indent

    def _validate_list_type_line(
        self, stripped_line: str, current_indent: int, type_line_indent: Optional[int], current_section: SectionConfig
    ) -> tuple[list[str], Optional[int]]:
        """
        Validate list_type section lines.
        """
        errors: list[str] = []

        # Check for valid type definition format
        if re.search(r"^\s*\([^)]+\):", stripped_line):
            return errors, current_indent

        # Handle lines without proper format
        if type_line_indent is None or current_indent > type_line_indent:
            # Allow as possible description
            return errors, None

        # This should be a type definition but lacks proper format
        errors.append(
            f"Section '{current_section.name}' (type: '{current_section.type}') requires "
            f"parenthesized types, see: '{stripped_line}'"
        )
        return errors, None

    def _validate_list_name_and_type_line(
        self, stripped_line: str, current_indent: int, type_line_indent: Optional[int], current_section: SectionConfig
    ) -> tuple[list[str], Optional[int]]:
        """
        Validate list_name_and_type section lines.
        """
        errors: list[str] = []

        # Check for valid parameter definition format
        if re.search(r"\([^)]+\):", stripped_line):
            return errors, current_indent

        # Check if this is likely a description line
        colon_part: str = stripped_line.split(":")[0].strip()

        # Skip description-like content
        if any(word in colon_part.lower() for word in ["default", "output", "format", "show", "example"]):
            return errors, None

        # Skip if more indented than parameter definition (description line)
        if type_line_indent is not None and current_indent > type_line_indent:
            return errors, None

        # Skip if too many words before colon (likely description)
        words_before_colon: list[str] = colon_part.split()
        if len(words_before_colon) > 2:
            return errors, None

        # Flag potential parameter definitions without proper format
        if not stripped_line.strip().startswith("#"):
            errors.append(
                f"Section '{current_section.name}' (type: '{current_section.type}') requires "
                f"parenthesized types, see: '{stripped_line}'"
            )

        return errors, None
