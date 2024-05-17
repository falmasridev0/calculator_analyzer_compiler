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
        node = self.stmt_or_expr()
        if self.current_token.type == STOP:
            self.eat(STOP)
            node = ('STMTS', node, self.stmts())
        return node

    def stmt_or_expr(self):
        if self.current_token.type == IDENTIFIER:
            if self.tokens[self.pos + 1].type == OPERATOR and self.tokens[self.pos + 1].value == '=':
                return self.stmt()
            else:
                return self.expr()
        else:
            return self.expr()

    def stmt(self):
        id_token = self.current_token
        self.eat(IDENTIFIER)
        self.eat(OPERATOR)  # for '='
        expr_node = self.expr()
        return ('STMT', id_token, expr_node)

    def expr(self):
        term_node = self.term()
        return self.expr_prime(term_node)

    def expr_prime(self, left):
        if self.current_token.type == OPERATOR and self.current_token.value in ('+', '-'):
            op = self.current_token
            self.eat(OPERATOR)
            term_node = self.term()
            node = ('EXPR', left, op, term_node)
            return self.expr_prime(node)
        return left

    def term(self):
        factor_node = self.factor()
        return self.term_prime(factor_node)

    def term_prime(self, left):
        if self.current_token.type == OPERATOR and self.current_token.value in ('*', '/'):
            op = self.current_token
            self.eat(OPERATOR)
            factor_node = self.factor()
            node = ('TERM', left, op, factor_node)
            return self.term_prime(node)
        elif self.current_token.type == OPERATOR and self.current_token.value == '^':
            op = self.current_token
            self.eat(OPERATOR)
            factor_node = self.factor()
            node = ('TERM', left, op, factor_node)
            return self.term_prime(node)
        return left

    def factor(self):
        if self.current_token.type == OPERATOR and self.current_token.value == '(':
            self.eat(OPERATOR)
            expr_node = self.expr()
            self.eat(OPERATOR)
            return expr_node
        elif self.current_token.type == IDENTIFIER:
            id_token = self.current_token
            self.eat(IDENTIFIER)
            return id_token
        elif self.current_token.type == NUMBER:
            num_token = self.current_token
            self.eat(NUMBER)
            return num_token

# GUI Code
def tokenize_code():
    code = input_text.get("1.0", tk.END).strip()
    tokens = tokenize(code)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Tokens:\n")
    for token in tokens:
        output_text.insert(tk.END, str(token) + "\n")

def parse_code():
    code = input_text.get("1.0", tk.END).strip()
    tokens = tokenize(code)
    parser = Parser(tokens)
    try:
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
