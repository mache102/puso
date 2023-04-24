import os
import sys
import textwrap

class Dense:
    def __init__(self, file_path):
        self.file_path = file_path

        with open(self.file_path, 'r') as f:
            self.content = f.read().splitlines()

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

        sys.exit(1)

    def densify(self):
        for idx, line in enumerate(self.content):
            
            if line == '':
                pass
                # self.throw_error(idx, 
                #     type='SyntaxError', 
                #     message="empty lines are not permitted",
                #     error_position=0)
                
            if any(char.isspace() for char in line) or r'\u0020' in line:
                self.throw_error(idx,                   # error has entered the chat
                    type='SyntaxError', 
                    message="whitespace is not permitted",
                    error_position=0)
                
file_path = __import__('__main__').__file__

obj = Dense(file_path)
obj.densify()

