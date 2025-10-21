"""Utility functions and classes for Jac compilation toolchain."""

import dis
import marshal
import os
import pdb
import re
from traceback import TracebackException


def pascal_to_snake(pascal_string: str) -> str:
    """Convert pascal case to snake case."""
    snake_string = re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_string).lower()
    return snake_string


def heading_to_snake(heading: str) -> str:
    """Convert string to snakecase including replacing(/ ,- )."""
    return heading.strip().replace("-", "_").replace("/", "_").replace(" ", "_").lower()


def add_line_numbers(s: str) -> str:
    """Add line numbers to a string."""
    lines = s.split("\n")
    return "\n".join(f"{i + 1}: \t{line}" for i, line in enumerate(lines))


def clip_code_section(s: str, target_line: int, line_range: int) -> str:
    """Clip a section of code and highlight target line."""
    lines = s.split("\n")
    start = max(0, target_line - line_range - 1)
    end = min(target_line + line_range, len(lines))

    result = []
    for i in range(start, end):
        line = lines[i]
        if i == target_line - 1:
            line = "*" + line
        result.append(line)
    return "\n".join(result)


def get_uni_nodes_as_snake_case() -> list[str]:
    """Get all AST nodes as snake case."""
    import inspect
    import sys
    import jaclang.compiler.unitree as uni

    module_name = uni.__name__
    module = sys.modules[module_name]

    # Retrieve the source code of the module
    source_code = inspect.getsource(module)

    classes = inspect.getmembers(module, inspect.isclass)
    uni_node_classes = [cls for _, cls in classes if issubclass(cls, uni.UniNode)]

    ordered_classes = sorted(
        uni_node_classes, key=lambda cls: source_code.find(f"class {cls.__name__}")
    )
    snake_names = []
    for cls in ordered_classes:
        class_name = cls.__name__
        snake_names.append(pascal_to_snake(class_name))
    return snake_names


def extract_headings(file_path: str) -> dict[str, tuple[int, int]]:
    """Extract headings of contetnts in Jac grammer."""
    with open(file_path, "r") as file:
        lines = file.readlines()
    headings = {}
    current_heading = None
    start_line = 0
    for idx, line in enumerate(lines, start=1):
        line = line.strip().removesuffix(".")
        if line.startswith("// [Heading]:"):
            if current_heading is not None:
                headings[current_heading] = (
                    start_line,
                    idx - 2,
                )  # Subtract 1 to get the correct end line
            current_heading = line.removeprefix("// [Heading]:")
            start_line = idx + 1
    # Add the last heading
    if current_heading is not None:
        headings[current_heading] = (start_line, len(lines))
    return headings


def auto_generate_refs() -> str:
    """Auto generate lang reference for docs."""
    file_path = os.path.join(
        os.path.split(os.path.dirname(__file__))[0], "../jaclang/compiler/jac.lark"
    )
    result = extract_headings(file_path)

    # Create the reference subdirectory if it doesn't exist
    docs_ref_dir = os.path.join(
        os.path.split(os.path.dirname(__file__))[0], "../../docs/docs/learn/jac_ref"
    )
    os.makedirs(docs_ref_dir, exist_ok=True)

    # Generate individual markdown files for each section
    for heading, lines in result.items():
        heading = heading.strip()
        heading_snakecase = heading_to_snake(heading)
        content = (
            f'# {heading}\n\n**Code Example**\n!!! example "Runnable Example in Jac and JacLib"\n'
            '    === "Try it!"\n        <div class="code-block">\n'
            "        ```jac\n"
            f'        --8<-- "jac/examples/reference/{heading_snakecase}.jac"\n'
            "        ```\n"
            "        </div>\n"
            '    === "Jac"\n        ```jac linenums="1"\n'
            f'        --8<-- "jac/examples/reference/{heading_snakecase}.jac"\n'
            f'        ```\n    === "Python"\n'
            '        ```python linenums="1"\n'
            '        --8<-- "jac/examples/reference/'
            f'{heading_snakecase}.py"\n        ```\n'
            f'??? info "Jac Grammar Snippet"\n    ```yaml linenums="{lines[0]}"\n    --8<-- '
            f'"jac/jaclang/compiler/jac.lark:{lines[0]}:{lines[1]}"\n    ```\n\n'
            "**Description**\n\n--8<-- "
            f'"jac/examples/reference/'
            f'{heading_snakecase}.md"\n'
        )

        # Write individual file
        output_file = os.path.join(docs_ref_dir, f"{heading_snakecase}.md")
        with open(output_file, "w") as f:
            f.write(content)

    # Return just the introduction for the main jac_ref.md file
    md_str = (
        '# Jac Language Reference\n\n--8<-- "jac/examples/reference/introduction.md"\n'
    )
    return md_str


def is_standard_lib_module(module_path: str) -> bool:
    """Check if a module is a standard library module."""
    import os
    import sysconfig

    stdlib_dir = sysconfig.get_paths()["stdlib"]
    direc_path = os.path.join(stdlib_dir, module_path)
    file_path = direc_path + ".py"
    return os.path.isfile(file_path) or os.path.isdir(direc_path)


def dump_traceback(e: Exception) -> str:
    """Dump the stack frames of the exception."""
    trace_dump = ""

    # Utility function to get the error line char offset.
    def byte_offset_to_char_offset(string: str, offset: int) -> int:
        return len(string.encode("utf-8")[:offset].decode("utf-8", errors="replace"))

    # Utility function to check if a file is a compiled Jac file and get the original .jac source
    def get_jac_source_info(py_filename: str) -> tuple[str | None, str | None]:
        """Return (jac_filename, jac_source) if available, else (None, None)."""
        # Check if this is a generated Python file from Jac compilation
        # Generated Python files are stored in __jac_gen__ directory
        if "__jac_gen__" in py_filename and py_filename.endswith(".py"):
            # Try to find the corresponding .jac file
            # The generated .py file typically mirrors the original .jac structure
            jac_filename = py_filename.replace("__jac_gen__", "").replace(".py", ".jac")
            if os.path.exists(jac_filename):
                try:
                    with open(jac_filename, "r") as f:
                        jac_source = f.read()
                    return jac_filename, jac_source
                except Exception:
                    pass
        return None, None

    tb = TracebackException(type(e), e, e.__traceback__, limit=None, compact=True)
    trace_dump += f"Error: {str(e)}\n"

    # The first frame is the call the to the above `exec` function, not usefull to the enduser,
    # and Make the most recent call first.
    tb.stack.pop(0)
    tb.stack.reverse()

    # FIXME: should be some settings, we should replace to ensure the anchors length match.
    dump_tab_width = 2

    for idx, frame in enumerate(tb.stack):
        func_signature = frame.name + ("()" if frame.name.isidentifier() else "")

        # Check if we can map this to a .jac file
        jac_filename, jac_source = get_jac_source_info(frame.filename)
        display_filename = jac_filename if jac_filename else frame.filename
        display_source = jac_source if jac_source else None

        # Pretty print the most recent call's location.
        if idx == 0 and (
            (frame.lineno is not None) and frame.line and frame.line.strip() != ""
        ):

            # Note: This is CPython internals we're trying to get since python doesn't provide
            # the frames original line but the stripped version so we had to do this.
            line_o = frame.line  # Fallback line.
            if hasattr(frame, "_original_line"):
                line_o = frame._original_line.rstrip()  # type: ignore [attr-defined]
            elif hasattr(frame, "_original_lines"):
                # https://github.com/python/cpython/issues/106922
                line_o = frame._original_lines.split("\n")[0].rstrip()  # type: ignore [attr-defined]

            if frame.colno is not None and frame.end_colno is not None:
                off_start = byte_offset_to_char_offset(line_o, frame.colno) - 1
                off_end = byte_offset_to_char_offset(line_o, frame.end_colno) - 1

                # Get the source - prefer .jac source if available, otherwise use .py
                file_source = display_source
                if file_source is None:
                    try:
                        with open(frame.filename, "r") as file:
                            file_source = file.read()
                    except Exception:
                        file_source = ""

                if file_source:
                    # Get the source offset.
                    lines = file_source.split("\n")
                    for i in range(frame.lineno - 1):
                        off_start += len(lines[i]) + 1
                        off_end += len(lines[i]) + 1

                    trace_dump += pretty_print_source_location(
                        display_filename, file_source, frame.lineno, off_start, off_end
                    )

        trace_dump += f'\n{" " * dump_tab_width}at {func_signature} {display_filename}:{frame.lineno}'

    return trace_dump


# FIXME: Use a proper color library and/or move this somewhere common to jac stack and use it everywhere.
# Reference: https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
class ANSIColors:
    """ANSI color codes."""

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


# TODO: After implementing the TextRange (or simillar named) class to mark a text range
# refactor the parameter to accept an instace of that text range object.
def pretty_print_source_location(
    file_path: str,
    file_source: str,
    error_line: int,
    pos_start: int,
    pos_end: int,
    *,
    colors: bool = False,
) -> str:
    """Pretty print internal method for the pretty_print method."""
    # NOTE: The Line numbers and the column numbers are starts with 1.
    # We print totally 5 lines (error line and above 2 and bellow 2).

    # The width of the line number we'll be printing (more of a settings).
    line_num_width: int = 5

    idx: int = pos_start  # Pointer for the current character.

    if file_source == "" or file_path == "":
        return ""

    start_line: int = error_line - 2
    if start_line < 1:
        start_line = 1
    end_line: int = start_line + 5  # Index is exclusive.

    # Get the first character of the [start_line].
    file_source.splitlines(True)[start_line - 1]
    curr_line: int = error_line
    while idx >= 0 and curr_line >= start_line:
        idx -= 1
        if idx < 0:
            break
        if file_source[idx] == "\n":
            curr_line -= 1

    idx += 1  # Enter the line.
    assert idx == 0 or file_source[idx - 1] == "\n"

    pretty_dump = ""

    # Print each lines.
    curr_line = start_line
    while curr_line < end_line:
        pretty_dump += f"%{line_num_width}d | " % curr_line

        idx_line_start = idx
        while idx < len(file_source) and file_source[idx] != "\n":
            idx += 1  # Run to the line end.

        if colors and (curr_line == error_line):
            pretty_dump += (
                file_source[idx_line_start:pos_start]
                + f"{ANSIColors.RED}{file_source[pos_start:pos_end]}{ANSIColors.END}"
                + file_source[pos_end:idx]
            )
        else:
            pretty_dump += file_source[idx_line_start:idx]

        pretty_dump += "\n"

        if curr_line == error_line:  # Print the current line with indicator.
            pretty_dump += f"%{line_num_width}s | " % " "

            spaces = ""
            for idx_pre in range(idx_line_start, pos_start):
                spaces += "\t" if file_source[idx_pre] == "\t" else " "

            err_token_len = pos_end - pos_start
            underline = "^" * err_token_len
            if colors:
                underline = f"{ANSIColors.RED}{underline}{ANSIColors.END}"
            pretty_dump += spaces + underline + "\n"

        if idx == len(file_source):
            break
        curr_line += 1
        idx += 1

    return pretty_dump[:-1]  # Get rid of the last newline (of the last line).


class Jdb(pdb.Pdb):
    """Jac debugger."""

    def __init__(self, *args, **kwargs) -> None:  # noqa
        """Initialize the Jac debugger."""
        super().__init__(*args, **kwargs)
        self.prompt = "Jdb > "

    def has_breakpoint(self, bytecode: bytes) -> bool:
        """Check for breakpoint."""
        code = marshal.loads(bytecode)
        instructions = dis.get_instructions(code)
        return any(
            instruction.opname in ("LOAD_GLOBAL", "LOAD_NAME", "LOAD_FAST")
            and instruction.argval == "breakpoint"
            for instruction in instructions
        )


debugger = Jdb()
