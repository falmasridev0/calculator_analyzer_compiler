import re
import tkinter as tk
from tkinter import scrolledtext

# Token types
NUMBER = 'NUMBER'
IDENTIFIER = 'IDENTIFIER'
OPERATOR = 'OPERATOR'
STOP = 'STOP'
EOF = 'EOF'

# Token specification
token_specification = [
    (NUMBER,       r'\d+(\.\d*)?'),   # Integer or decimal number
    (IDENTIFIER,   r'[A-Za-z_]\w*'),  # Identifiers
    (OPERATOR,     r'[+\-*/^=()]'),   # Arithmetic operators and parentheses
    (STOP,         r';'),             # Stop token
    (EOF,          r'$'),             # End of file
    ('SKIP',       r'\s+'),           # Skip over spaces and tabs
    ('MISMATCH',   r'.'),             # Any other character
]

token_re = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'

def tokenize(code):
    tokens = []
    for mo in re.finditer(token_re, code):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == NUMBER:
            value = float(value) if '.' in value else int(value)
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Illegal character {value}')
        tokens.append(Token(kind, value))
    tokens.append(Token(EOF, None))
    return tokens

# Syntax Analyzer Code
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0]
        self.symbol_table = set()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        else:
            raise SyntaxError(f'Expected token {token_type}, got {self.current_token.type}')

    def parse(self):
        return self.program()

    def program(self):
        node = self.stmts()
        self.eat(EOF)
        return node

    def stmts(self):
        stmts = []
        while self.current_token.type != EOF:
            stmts.append(self.stmt())
        return stmts

    def stmt(self):
        if self.current_token.type == IDENTIFIER:
            node = self.expr()
            self.eat(STOP)
            return node
        else:
            return self.expr()

    def expr(self):
        if self.current_token.type == OPERATOR:
            left_operand = self.current_token
            self.eat(OPERATOR)
            right_operand = self.expr()
            return (left_operand, right_operand)
        elif self.current_token.type == IDENTIFIER:
            id_token = self.current_token
            self.eat(IDENTIFIER)
            if self.current_token.type == OPERATOR:
                op_token = self.current_token
                self.eat(OPERATOR)
                if self.current_token.type in {IDENTIFIER, NUMBER}:
                    right_operand = self.expr()
                    if op_token.value == '=':
                        self.symbol_table.add(id_token.value)
                    else:
                        if id_token.value not in self.symbol_table:
                            raise SyntaxError(f'Undefined variable {id_token.value}')
                    return (id_token, op_token, right_operand)
                else:
                    raise SyntaxError('Incomplete expression after operator')
            if id_token.value not in self.symbol_table:
                raise SyntaxError(f'Undefined variable {id_token.value}')
            return id_token
        elif self.current_token.type == NUMBER:
            num_token = self.current_token
            self.eat(NUMBER)
            return num_token
        else:
            raise SyntaxError('Unexpected token')

# GUI Code
def tokenize_code():
    code = input_text.get("1.0", tk.END).strip()
    try:
        tokens = tokenize(code)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Tokens:\n")
        for token in tokens:
            output_text.insert(tk.END, str(token) + "\n")
    except SyntaxError as e:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Syntax Error: {e}\n")

def parse_code():
    code = input_text.get("1.0", tk.END).strip()
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        parse_tree = parser.parse()
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "Parse Tree:\n")
        output_text.insert(tk.END, str(parse_tree) + "\n")
    except SyntaxError as e:
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Syntax Error: {e}\n")

root = tk.Tk()
root.title("Lexical and Syntax Analyzer")
root.configure(bg='black')

input_label = tk.Label(root, text="Input Code:", bg='black', fg='white')
input_label.pack()

input_text = scrolledtext.ScrolledText(root, width=80, height=10, bg='black', fg='white', insertbackground='white')
input_text.pack()

tokenize_button = tk.Button(root, text="Tokenize", command=tokenize_code, bg='black', fg='white')
tokenize_button.pack()

parse_button = tk.Button(root, text="Parse", command=parse_code, bg='black', fg='white')
parse_button.pack()

output_label = tk.Label(root, text="Output:", bg='black', fg='white')
output_label.pack()

output_text = scrolledtext.ScrolledText(root, width=80, height=20, bg='black', fg='white', insertbackground='white')
output_text.pack()

root.mainloop()
