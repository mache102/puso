import ast
import os
import sys
import inspect
import textwrap

"""
PUSO: Python User Sanity Obliterator
"""

class _PUSO:
    def __init__(self, content, file_path, flags=None, action=None):
        """
        Initialize the vibe checker.

        Parameters:
        -----------
        content (list): Contents of file to be checked

        file_path (str): File path shown in error messages 
                         (defaults to path of content; 
                         can be customized to hide paths)

        flags (set): Checks to keep/filter out

        action (int): Action to be taken on flags:
                      - 0: Flags will be disabled, rest enabled
                      - 1: Flags will be enabled, rest disabled
        """
        self.content = content
        self.file_path = file_path

        self.flags = flags
        self.action = action

        self.import_strs = {'from', 'import'}
        self.end_chars = {':', ';', ',', '\\'}
        self.implicit_end_chars = {')', ']', '}', '"""', "'''"}

    def func_enabled(func):
        def wrapper(self, *args, **kwargs):
            is_enabled = 1
        
            function_name = func.__name__.strip()

            if self.action == 0:
                is_enabled = function_name not in self.flags
            
            elif self.action == 1:
                is_enabled = function_name in self.flags
            
            #print(function_name, is_enabled)
            if is_enabled:
                func(self, *args, **kwargs)
        return wrapper

    def throw_error(self, 
                    idx, 
                    type='SyntaxError', 
                    message='invalid syntax', 
                    error_position=None):
        
        line = self.content[idx].strip()

        if error_position is None:
            # Defaults to end of line
            error_position = len(line)

        error_message = f"""
          File "{self.file_path}", line {idx + 1}
            {line}
            {'':>{error_position}}^
        {type}: {message}
        """

        error_message = textwrap.dedent(error_message).lstrip('\n')
        print(error_message, file=sys.stderr)
        
        # The OG error message. Prayge
        #print(f"{filepath}:{idx+1}: error: expected ';'")

        sys.exit(1)

    def get_true_contents(line, max_iters=100):
        contents = line

        for iter in range(max_iters):
            prev_contents = contents
            try:
                tree = ast.parse(contents)
            except SyntaxError:
                pass

            for item in ast.walk(tree):
                if isinstance(item, ast.Expr) \
                    and isinstance(item.value, ast.Call) \
                    and isinstance(item.value.func, ast.Name) \
                    and item.value.func.id == 'exec':

                    if isinstance(item.value.args[0], ast.Str):
                        contents = item.value.args[0].s
                    elif isinstance(item.value.args[0], ast.Bytes):
                        contents = item.value.args[0].s.decode('utf-8')

            if prev_contents == contents:
                break

        return prev_contents
    
    def has_implicit_line_break(self, line):
        try:
            ast.parse(line, mode='eval')
            return False
        except SyntaxError:
            return not any(line[-1] == x for x in self.implicit_end_chars)
        
    def semicolon_split(self, line):
        ast_tree = ast.parse(line)

        split_lines = []

        for node in ast_tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func_call_line = ast.get_source_segment(line, node)
                split_lines.extend(func_call_line.split(';'))
            else:
                split_lines.append(ast.get_source_segment(line, node))

        split_lines = [line.strip() for line in split_lines]
        return split_lines
    
    @func_enabled
    def imports(self, length_req=True):
        def imports_check_line(line):
            if any(x in line for x in banned_keywords):
                self.throw_error(idx, 
                                 type='SyntaxError', 
                                 message="deprecated syntax; please use \"from...import\" instead",
                                 error_position=0)
            # check if statement actually imports something
            is_importer = 0  
            try:
                tree = ast.parse(line)
            except Exception:
                return

            for node in ast.walk(tree):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    is_importer = 1
                    break 
            if not is_importer:
                return

            # fix for one-liners
            line = line.split(';')[0]

            # Code imports something
            if line.startswith('import'):
                self.throw_error(idx, 
                                 type='SyntaxError', 
                                 message="deprecated syntax; please use \"from...import\" instead",
                                 error_position=0)
            
            imports = line.split(',')

            # from module_name import ...
            module_len = len(imports[0].split()[1])

            error_position = 0
            for string in imports: 
                error_position += len(string)
                words = string.split()

                if 'as' not in words:
                    self.throw_error(idx, 
                                    type='SyntaxError', 
                                    message="syntax may cause conflicts; please use \"from...import...as\" instead",
                                    error_position=error_position)
                    
                elif words[-1] == words[-3]:
                    # member and alias are the same

                    error_position -= len(words[-1])
                    self.throw_error(idx, 
                                    type='SyntaxError', 
                                    message="alias cannot be the same as member name",
                                    error_position=error_position)    
                    
                elif length_req:
                    minimum_len = 2 * (module_len + len(words[-3]))
                    if len(words[-1]) < minimum_len:
                        error_position -= 1
                        self.throw_error(idx, 
                                    type='SyntaxError', 
                                    message=f"alias must be {minimum_len} characters or longer",
                                    error_position=error_position)    
                # account for the comma
                error_position += 1

        # bypass bans
        banned_keywords = ['__import__', 'import_module']

        for idx, line in enumerate(self.content):
            if not line.strip():
                continue 

            if ';' in line:
                lines = self.semicolon_split(line)
                print(lines)
                for split_line in lines:
                    imports_check_line(split_line)
            else:
                imports_check_line(line)

        # if line.startswith('from') or 'as' in line.split():
        #     # invalid syntax
        #     self.throw_error(idx, 
        #                      type='SyntaxError', 
        #                      message="deprecated syntax")
        
        # elif line.startswith('import') and '.' in line:
        #     self.throw_error(idx, 
        #                      type='SyntaxError', 
        #                      message="submodule imports are no longer supported")

    @func_enabled
    def semicolon(self):
        comment_enabled = 0

        for idx, line in enumerate(self.content):
            if not line.strip():
                continue 

            if self.has_implicit_line_break(line):
                continue

            if line.startswith('\'\'\'') or line.startswith('"""'):
                comment_enabled = not(comment_enabled)
                continue

            if any(line.startswith(x) for x in self.import_strs) \
                or any(line.endswith(x) for x in self.end_chars) \
                or comment_enabled \
                or line[0] == '#':
                continue

            else:
                self.throw_error(idx, type='SyntaxError', message="expected ';'")

    @func_enabled
    def one_line(self, strict=False):
        # 'strict' means no spaces after semicolon here

        if len(self.content) > 1:
            self.throw_error(1, 
                            type='SyntaxError', 
                            message=f"maximum program line count (1) exceeded",
                            error_position=0)  

        # prevent the word wrap + space bypass
        one_liner = self.content[0]
        lines = one_liner.split(';')
        
        if strict: 
            line_start = 1
            msg = 'space after semicolon is not allowed' 
        else:
            # starts with two or more spaces 
            line_start = 2
            msg = 'nice try buddy.'

        error_position = 0
        for line in lines:
            if line[:line_start].isspace():
                self.throw_error(0, 
                                type='SyntaxError', 
                                message=msg,
                                error_position=error_position+int(not(strict))+1)  
            
            error_position += len(line)


def run(custom_fp=None, enable=[], disable=[]):

    if len(enable) and len(disable):
        raise ValueError('cannot simultaneously define enables and disables')

    # Retrieve caller file info
    frame = inspect.currentframe().f_back
    file_path = inspect.getframeinfo(frame).filename
    #filename = os.path.basename(filepath)

    with open(file_path, 'r') as f:
        content = f.read().splitlines()
    
    # for vid
    if custom_fp is None:
        custom_fp = file_path
    

    if len(enable):
        puso_obj = _PUSO(content, 
                         custom_fp, 
                         flags=enable, 
                         action=1)
    elif len(disable):
        puso_obj = _PUSO(content, 
                         custom_fp, 
                         flags=disable, 
                         action=0)
    else:
        puso_obj = _PUSO(content, 
                         custom_fp)

    puso_obj.imports()
    puso_obj.semicolon()
    puso_obj.one_line()



# import ast

# # Set of paired delimiters to check for
# PAIRED_DELIMITERS = {ast.Tuple, ast.List, ast.Set, ast.Dict}

# def contains_only_paired_delimiters(stmt):
#     """
#     Check if a statement only contains a set of paired delimiters and nothing else.

#     Args:
#         stmt (str): The input statement to check.

#     Returns:
#         bool: True if the statement only contains paired delimiters, False otherwise.
#     """
#     try:
#         # Parse the input statement into an AST
#         tree = ast.parse(stmt)

#         # Recursive function to inspect nodes in the AST
#         def inspect(node):
#             if isinstance(node, tuple(PAIRED_DELIMITERS)):
#                 # If the node is one of the expected delimiter types, recursively inspect its children
#                 return all(inspect(child) for child in ast.iter_child_nodes(node))
#             elif not isinstance(node, ast.Expr):
#                 # If any non-delimiter node is found, return False
#                 return False
#             return True

#         # Start inspecting from the root of the AST
#         return inspect(tree)
#     except SyntaxError:
#         # If the statement is not a valid Python syntax, return False
#         return False

# # Example usage
# stmt1 = "(1, 2, 3)"  # Only contains a tuple delimiter, returns True
# stmt2 = "[1, 2, 3]"  # Only contains a list delimiter, returns True
# stmt3 = "{1, 2, 3}"  # Only contains a set delimiter, returns True
# stmt4 = "{'a': 1, 'b': 2}"  # Only contains a dict delimiter, returns True
# stmt5 = "(1, 2], 3)"  # Contains a non-matching delimiter, returns False
# stmt6 = "1, 2, 3"  # Contains non-delimiter nodes, returns False

# print(contains_only_paired_delimiters(stmt1))  # True
# print(contains_only_paired_delimiters(stmt2))  # True
# print(contains_only_paired_delimiters(stmt3))  # True
# print(contains_only_paired_delimiters(stmt4))  # True
# print(contains_only_paired_delimiters(stmt5))  # False
# print(contains_only_paired_delimiters(stmt6))  # False