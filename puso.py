import ast
import os
import sys
import inspect
import textwrap

'''
PUSO: Python User Sanity Obliterator
'''

class _Check:
    def __init__(self, file_path, content):
        self.file_path = file_path
        self.content = content

        self.import_strs = {'from', 'import'}
        self.end_chars = {':', ';', ',', '\\'}
        self.implicit_end_chars = {')', ']', '}', '"""', '\'\'\''}

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
    
    def imports(self, length_requirement=True):
        for idx, line in enumerate(self.content):
            if not line.strip():
                continue 

            if '__import__' in line:
                self.throw_error(idx, 
                                 type='SyntaxError', 
                                 message="deprecated syntax; please use \"from...import\" instead (thx Albert lol)",
                                 error_position=0)
            # check if statement actually imports something
            is_importer = 0  
            try:
                tree = ast.parse(line)
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    is_importer = 1
                    break 
            if not is_importer:
                continue 

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
                    
                elif length_requirement:
                    minimum_len = 2 * (module_len + len(words[-3]))
                    if len(words[-1]) < minimum_len:
                        error_position -= 1
                        self.throw_error(idx, 
                                    type='SyntaxError', 
                                    message=f"alias must be {minimum_len} characters or longer",
                                    error_position=error_position)    
                # account for the comma
                error_position += 1

            # if line.startswith('from') or 'as' in line.split():
            #     # invalid syntax
            #     self.throw_error(idx, 
            #                      type='SyntaxError', 
            #                      message="deprecated syntax")
            
            # elif line.startswith('import') and '.' in line:
            #     self.throw_error(idx, 
            #                      type='SyntaxError', 
            #                      message="submodule imports are no longer supported")


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
            line_start = ' '
            msg = 'space after semicolon is not allowed' 
        else:
            # starts with two or more spaces 
            line_start = '  '
            msg = 'nice try buddy.'

        error_position = 0
        for line in lines:
            if line.startswith(line_start):
                self.throw_error(0, 
                                type='SyntaxError', 
                                message=msg,
                                error_position=error_position+int(not(strict))+1)  
            
            error_position += len(line)


def run(custom_file_path=None):

    # Retrieve caller file info
    frame = inspect.currentframe().f_back
    file_path = inspect.getframeinfo(frame).filename
    #filename = os.path.basename(filepath)

    with open(file_path, 'r') as f:
        content = f.read().splitlines()
    
    # for vid
    if custom_file_path is None:
        custom_file_path = file_path
    
    check = _Check(custom_file_path, content)

    check.imports()
    check.semicolon()
    check.one_line()

