'''
PUSO: Python User Sanity Obliterator
'''
import os
import sys
import inspect
import textwrap


def run():

    frame = inspect.currentframe().f_back
    filepath = inspect.getframeinfo(frame).filename
    #filename = os.path.basename(filepath)

    end_chars = {':', ';', ',', '\\'}
    imports = {'from', 'import'}
    comment_enabled = 0

    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        line = line.strip()

        if line.startswith('\'\'\'') or line.startswith('"""'):
            comment_enabled = not(comment_enabled)
            continue

        if not line \
            or any(line.startswith(x) for x in imports) \
            or any(line.endswith(x) for x in end_chars) \
            or comment_enabled \
            or line[0] == '#':
            continue

        else:
            line_length = len(line)

            error_message = f"""
              File "{filepath}", line {idx + 1} 
                {line} 
                {'':>{line_length}}^ 
            SyntaxError: expected ';' 
            """

            error_message = textwrap.dedent(error_message).lstrip('\n')
            print(error_message, file=sys.stderr)

            #print(f"{filepath}:{idx+1}: error: expected ';'")


            sys.exit(1)
