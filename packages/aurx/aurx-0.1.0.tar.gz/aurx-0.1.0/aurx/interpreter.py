# ------------------------------
# Aurascript Interpreter v8 - Merged full interpreter with Extended I/O, Generators, OOP, Exceptions
# ------------------------------

import re
import math
import random
import datetime
import sys
import traceback
import os

# ------------------------------
# Nothing sentinel
# ------------------------------
class NothingType:
    def __repr__(self):
        return "Nothing"
    def __str__(self):
        return "Nothing"

Nothing = NothingType()

# ------------------------------
# Math helper builtin (small)
# ------------------------------
class Mathematics:
    pi = math.pi
    e = math.e

    @staticmethod
    def add(a, b): return a + b
    @staticmethod
    def subtract(a, b): return a - b
    @staticmethod
    def multiply(a, b): return a * b
    @staticmethod
    def divide(a, b): return a / b
    @staticmethod
    def floor_divide(a, b): return a // b
    @staticmethod
    def remainder(a, b): return a % b
    @staticmethod
    def power(a, b): return a ** b
    @staticmethod
    def sqrt(a): return math.sqrt(a)
    @staticmethod
    def abs(a): return abs(a)
    @staticmethod
    def factorial(a): return math.factorial(int(a))
    @staticmethod
    def gcd(a, b): return math.gcd(int(a), int(b))
    @staticmethod
    def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b)) if a and b else 0
    @staticmethod
    def mean(seq): return sum(seq) / len(seq) if seq else 0
    @staticmethod
    def median(seq):
        s = sorted(seq)
        n = len(s)
        if n == 0: return 0
        if n % 2 == 1: return s[n//2]
        return (s[n//2 - 1] + s[n//2]) / 2
    @staticmethod
    def clamp(x, lo, hi): return max(lo, min(hi, x))
    @staticmethod
    def rand_int(a, b): return random.randint(a, b)
    @staticmethod
    def rand_float(): return random.random()
    @staticmethod
    def deg2rad(x): return math.radians(x)
    @staticmethod
    def rad2deg(x): return math.degrees(x)

# ------------------------------
# Flow control exceptions
# ------------------------------
class BreakException(Exception): pass
class ContinueException(Exception): pass
class ReturnException(Exception):
    def __init__(self, value): self.value = value
class RaiseException(Exception):
    def __init__(self, value): self.value = value

# ------------------------------
# Interpreter
# ------------------------------
class AurascriptInterpreter:
    def __init__(self):
        self.variables = {}   # global vars
        self.functions = {}   # name -> list of overload dicts {'params':[], 'body': list or str, 'decorators':[]}
        self.classes = {}     # class_name -> {'bases':[], 'methods':{}, 'class_vars':{}, 'instances':{}}
        self.decorators = {}  # name -> body expression (string)
        self.builtins = {
            'math': math,
            'random': random,
            'datetime': datetime,
            'input': input,
            'read_file': lambda p: open(p, 'r', encoding='utf-8').read(),
            'write_file': lambda p, t: open(p, 'w', encoding='utf-8').write(str(t)),
            'append_file': lambda p, t: open(p, 'a', encoding='utf-8').write(str(t)),
            'input_file_lines': lambda p: open(p, 'r', encoding='utf-8').read().splitlines(),
            'file_exists': lambda p: os.path.exists(p),
            'list_dir': lambda p='.': os.listdir(p),
            'mathematics': Mathematics
        }

    # ------------------------------
    # REPL
    # ------------------------------
    def start_repl(self):
        print("Welcome to Aurascript REPL v8! Type 'exit.' to quit.")
        multiline = False
        block_lines = []
        block_start = None
        while True:
            try:
                prompt = '... ' if multiline else '>> '
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print('\nExiting Aurascript. Bye!')
                break

            if not line and not multiline:
                continue

            # multi-line mode handling: lines may be fed until 'end.' inside a block
            if not line.endswith('.'):
                if multiline:
                    block_lines.append(line)
                    if line.strip().lower() == 'end.':
                        multiline = False
                        source = '\n'.join(block_lines)
                        block_lines = []
                        self.run_block(source)
                    continue
                else:
                    print(f"[Syntax Error] Missing dot at end of line: '{line}'")
                    continue

            core = line[:-1].strip()
            lower = core.lower()

            # start of multi-line block (define, class, try, switch)
            if re.match(r'^(define|class|try|switch)\b', lower):
                multiline = True
                block_lines = [line]
                block_start = lower.split()[0]
                continue

            # single-line
            try:
                if core.lower() == 'exit':
                    print('Exiting Aurascript. Bye!')
                    break
                self.run_line(core)
            except Exception as e:
                print(f"[Error] {e}")
                traceback.print_exc()

    # ------------------------------
    # Run block (multi-line text with trailing dots)
    # ------------------------------
    def run_block(self, source):
        lines = [ln.rstrip() for ln in source.splitlines() if ln.strip()]
        for ln in lines:
            if not ln.endswith('.'):
                print(f"[Syntax Error] Missing dot in block line: '{ln}'")
                return
            core = ln[:-1].strip()
            try:
                self.run_line(core)
            except ReturnException as r:
                print('[Warning] give/return outside function')
            except Exception as e:
                print(f"[Error] {e}")
                traceback.print_exc()

    # ------------------------------
    # Top-level line dispatcher
    # ------------------------------
    def run_line(self, core):
        original = core
        lower = core.lower().strip()

        # quick control tokens
        if lower == 'break':
            raise BreakException()
        if lower == 'continue':
            raise ContinueException()

        # raise handling
        if lower.startswith('raise '):
            # raise expression (evaluate expr or string)
            arg = core[6:].strip()
            val = self.evaluate_expression(arg)
            raise RaiseException(val)

        # statements
        if lower.startswith('variable '):
            return self.handle_variable(core)
        if lower.startswith('say '):
            return self.handle_say(core)
        if lower.startswith('import '):
            return self.handle_import(core)
        if lower.startswith('define '):
            return self.handle_function_define_block(core)
        if lower.startswith('lambda '):
            return self.handle_lambda(core)
        if lower.startswith('class '):
            return self.handle_class_define_block(core)
        if lower.startswith('$'):
            return self.handle_decorator_define(core)
        if lower.startswith('try '):
            return self.handle_try_block(core)
        if lower.startswith('switch '):
            return self.handle_switch_block(core)

        # assignment
        if re.match(r'\w+\s*(=|set to|equals)\s*', core, re.IGNORECASE):
            return self.handle_assignment(core)

        # method call (object.method(...))
        if re.match(r'\*?\w+\.(\*?\w+)\(.*\)$', core):
            return self.handle_method_call(core)

        # function call
        if re.match(r'\w+\(.*\)$', core):
            return self.handle_function_call(core)

        # fallback to expression eval
        return self.evaluate_expression(core)

    # ------------------------------
    # Expression normalization: English -> python tokens and variable substitution
    # ------------------------------
    def normalize_expr(self, expr, local_vars=None):
        if local_vars is None:
            local_vars = {}
        # stash string literals to avoid replacing inside them
        literals = []
        def stash(m):
            literals.append(m.group(0))
            return f'__STR{len(literals)-1}__'
        expr = re.sub(r'(\"(?:\\.|[^\"])*\"|\'(?:\\.|[^\'])*\')', stash, expr)


        # english to symbol mapping
        reps = [
            (r'\bequals to\b', '=='),
            (r'\bnot equals to\b', '!='),
            (r'\b><\b', '!='), (r'\b<>\b','!='),
            (r'\bgreater or equal to\b','>='), (r'\blower or equal to\b','<='),
            (r'\bgreater than or equal to\b','>='), (r'\blower than or equal to\b','<='),
            (r'\bgreater than\b','>'), (r'\blower than\b','<'),
            (r'\bset to\b','='), (r'\bequals\b','=='),
            (r'\bdivide without decimal by\b','//'),
            (r'\bdivided by\b','/'),
            (r'\binto\b','*'),
            (r'\bpercentage\b','%'), (r'\bremainder\b','%'),
            (r'\bpower\b','**'),
            (r'\bplus\b','+'), (r'\bminus\b','-'),
            (r'\band\b',' and '), (r'\bor\b',' or '), (r'\bnot\b',' not '),
        ]
        for p, rpl in reps:
            expr = re.sub(p, rpl, expr, flags=re.IGNORECASE)

        # symbol aliases
        expr = expr.replace('&', ' and ').replace('\\', ' or ').replace('!', ' not ')

        # substitute variables and local_vars into expression as repr where appropriate
        # order: local_vars then global variables
        combined = {}
        combined.update(local_vars or {})
        combined.update(self.variables or {})
        # replace only whole-word occurrences
        for var, val in combined.items():
            # var can be like *name or contain special char in your language - escape
            var_escaped = re.escape(str(var))
            expr = re.sub(rf'\b{var_escaped}\b', repr(val), expr)

        # restore string literals
        for i, s in enumerate(literals):
            expr = expr.replace(f'__STR{i}__', s)
        return expr

    # ------------------------------
    # Evaluate expression (sandboxed eval with builtins)
    # supports simple generator detection via 'yield' in expr
    # ------------------------------
    def evaluate_expression(self, expr, local_vars=None):
        expr = expr.strip()
        if local_vars is None:
            local_vars = {}

        # string literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # direct lookup
        if expr in local_vars:
            return local_vars[expr]
        if expr in self.variables:
            return self.variables[expr]

        # special-case Nothing
        if expr.lower() == 'nothing':
            return Nothing

        # generator support: if user wrote something containing 'yield', try to make a generator
        try:
            if 'yield' in expr:
                # build a small function wrapper to exec into a namespace
                # Note: this is a convenience shim, not a full generator parser
                fn_code = 'def __gen():\n'
                # indent the expression lines (if multi-line)
                for line in expr.splitlines():
                    fn_code += '    ' + line + '\n'
                ns = {}
                # Execute with only safe builtins and our provided builtins in globals
                exec(fn_code, {'__builtins__': {} , **self.builtins}, ns)
                return ns['__gen']()
        except Exception:
            # fall back to normal eval
            pass

        # normalize english -> python
        pyexpr = self.normalize_expr(expr, local_vars)

        # evaluate with limited builtins (the builtins dict is provided as locals so expressions can call them)
        env = {}
        env.update(self.builtins)

        try:
            return eval(pyexpr, {'__builtins__': {}}, env)
        except Exception:
            # fallback: try evaluating with builtins available as globals
            try:
                env2 = {}
                env2.update(self.builtins)
                return eval(pyexpr, {}, env2)
            except Exception:
                # If nothing works, return expression literally
                return expr

    # ------------------------------
    # Variable declaration
    # ------------------------------
    def handle_variable(self, core):
        m = re.match(r'variable\s+(\*?\w+)\s+(set to|equals|=)\s+(.+)', core, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid variable declaration.')
        name = m.group(1)
        val = self.evaluate_expression(m.group(3).strip())
        self.variables[name] = val
        return None

    # ------------------------------
    # Assignment
    # ------------------------------
    def handle_assignment(self, core):
        m = re.match(r'(\*?\w+)\s*(?:=|set to|equals)\s*(.+)', core, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid assignment syntax.')
        name = m.group(1)
        if name not in self.variables:
            raise NameError(f"Variable '{name}' not defined.")
        val = self.evaluate_expression(m.group(2).strip())
        self.variables[name] = val
        return None

    # ------------------------------
    # say
    # ------------------------------
    def handle_say(self, core):
        m = re.match(r'say\s+(.+)', core, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid say syntax.')
        val = self.evaluate_expression(m.group(1).strip())
        if val is Nothing:
            print('Nothing')
        else:
            print(val)
        return None

    # ------------------------------
    # import (very naive module loader)
    # ------------------------------
    def handle_import(self, core):
        # supports: import "path" or import modulename
        m = re.match(r'import\s+"(.+)"', core, re.IGNORECASE)
        if m:
            path = m.group(1)
        else:
            m2 = re.match(r'import\s+(\w+)', core, re.IGNORECASE)
            if not m2:
                raise SyntaxError('Invalid import syntax.')
            path = m2.group(1) + '.aur'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Module file '{path}' not found.")
        # execute module in same interpreter (naive)
        self.run_block(data)
        return None

    # ------------------------------
    # Functions - multi-line define ... end.
    # ------------------------------
    def handle_function_define_block(self, first_line):
        header = first_line
        # single-line define variant
        if ':' in first_line and not first_line.strip().endswith(':'):
            m = re.match(r'define\s+(\w+)\s*\((.*?)\)\s*:\s*(.+)', first_line, re.IGNORECASE)
            if not m:
                raise SyntaxError('Invalid single-line function definition.')
            name, params_raw, body = m.group(1), m.group(2), m.group(3)
            params = self.parse_params(params_raw)
            self.register_function(name, params, [body])
            return None

        # otherwise read interactive body until 'end.'
        func_name = first_line.split()[1] if len(first_line.split()) > 1 else '<anon>'
        print(f"Enter function body for {func_name}, end with 'end.'")
        lines = []
        while True:
            ln = input()
            if ln.strip().lower() == 'end.':
                break
            lines.append(ln)
        # parse header
        m = re.match(r'define\s+(\w+)\s*\((.*?)\)\s*:', header, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid function header.')
        name, params_raw = m.group(1), m.group(2)
        params = self.parse_params(params_raw)
        self.register_function(name, params, lines)
        return None

    def parse_params(self, raw):
        raw = raw.strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(',')]
        return parts

    def register_function(self, name, params, body_lines):
        entry = {'params': params, 'body': body_lines, 'decorators': []}
        self.functions.setdefault(name, []).append(entry)

    def execute_function_body(self, body_lines, local_vars):
        # body_lines are raw lines (with or without trailing dot)
        # returns value or None
        try:
            for ln in body_lines:
                # allow passing either with or without trailing dot
                core = ln[:-1].strip() if ln.endswith('.') else ln.strip()
                res = self.run_line(core)
                # handle explicit return/give via ReturnException if implemented (not implemented fully)
                if isinstance(res, ReturnException):
                    return res.value
            return None
        except ReturnException as r:
            return r.value

    def handle_function_call(self, core):
        m = re.match(r'(\w+)\((.*?)\)$', core)
        if not m:
            raise SyntaxError('Invalid function call.')
        name, args_raw = m.group(1), m.group(2)
        # split respecting quoted commas
        args = [a.strip() for a in re.split(r',(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', args_raw) if a.strip()]
        arg_values = [self.evaluate_expression(a) for a in args] if args else []
        if name not in self.functions:
            raise NameError(f"Function '{name}' not defined.")
        overloads = self.functions[name]
        func_entry = None
        for o in overloads:
            if len(o['params']) == len(arg_values):
                func_entry = o; break
        if func_entry is None:
            func_entry = overloads[0]
        # map params to local vars
        local_vars = {}
        for p, v in zip(func_entry['params'], arg_values):
            local_vars[p] = v
        # execute
        if isinstance(func_entry['body'], list):
            rv = self.execute_function_body(func_entry['body'], local_vars)
        else:
            rv = self.evaluate_expression(func_entry['body'], local_vars)
        # decorators
        for deco in func_entry.get('decorators', []):
            if deco in self.decorators:
                rv = self.apply_decorator(deco, rv)
        return rv

    def apply_decorator(self, deco_name, value):
        body = self.decorators.get(deco_name)
        if not body:
            return value
        expr = body.replace('$value', repr(value))
        return self.evaluate_expression(expr)

    # ------------------------------
    # lambda
    # ------------------------------
    def handle_lambda(self, core):
        m = re.match(r'lambda\s*\((.*?)\)\s*:\s*(.+)$', core, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid lambda syntax.')
        params_raw, body = m.group(1), m.group(2)
        params = [p.strip() for p in params_raw.split(',') if p.strip()]
        def _lambda(*args):
            local_vars = dict(zip(params, args))
            return self.evaluate_expression(body, local_vars)
        return _lambda

    # ------------------------------
    # class define block (simple)
    # ------------------------------
    def handle_class_define_block(self, first_line):
        m = re.match(r'class\s+(\w+)\s*(?:\((.*?)\))?\s*:', first_line, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid class header.')
        name = m.group(1)
        bases_raw = m.group(2) or ''
        bases = [b.strip() for b in bases_raw.split(',')] if bases_raw else []
        print(f"Enter class body for {name}, end with 'end.'")
        lines = []
        while True:
            ln = input()
            if ln.strip().lower() == 'end.':
                break
            lines.append(ln)
        methods = {}
        class_vars = {}
        i = 0
        while i < len(lines):
            ln = lines[i].strip()
            if ln.lower().startswith('variable '):
                mm = re.match(r'variable\s+(\w+)\s+(set to|equals|=)\s+(.+)', ln, re.IGNORECASE)
                if mm:
                    class_vars[mm.group(1)] = self.evaluate_expression(mm.group(3))
                i += 1
                continue
            if ln.lower().startswith('define '):
                hdr = ln
                body_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().lower().startswith('define '):
                    body_lines.append(lines[i])
                    i += 1
                m2 = re.match(r'define\s+(\w+)\s*\((.*?)\)\s*:', hdr, re.IGNORECASE)
                if not m2:
                    raise SyntaxError('Invalid method header in class')
                mname = m2.group(1)
                params = [p.strip() for p in m2.group(2).split(',') if p.strip()]
                methods[mname] = {'params': params, 'body': body_lines}
                continue
            i += 1
        self.classes[name] = {'bases': bases, 'methods': methods, 'class_vars': class_vars, 'instances': {}}
        return None

    # ------------------------------
    # instantiate helper
    # ------------------------------
    def instantiate(self, class_name, *args):
        if class_name not in self.classes:
            raise NameError(f"Class '{class_name}' not defined.")
        cls = self.classes[class_name]
        inst = {'__class__': class_name, '__vars__': dict(cls.get('class_vars', {}))}
        # call __init__ if present
        if '__init__' in cls['methods']:
            method = cls['methods']['__init__']
            local = {'self': inst}
            for p, a in zip(method['params'], args): local[p] = a
            self.execute_function_body(method['body'], local)
        return inst

    # ------------------------------
    # method call
    # ------------------------------
    def handle_method_call(self, core):
        m = re.match(r'(\*?\w+)\.(\w+)\((.*?)\)$', core)
        if not m:
            raise SyntaxError('Invalid method call syntax.')
        objname, methodname, args_raw = m.group(1), m.group(2), m.group(3)
        if objname not in self.variables:
            raise NameError(f"Object '{objname}' not defined.")
        obj = self.variables[objname]
        clsname = obj.get('__class__')
        if not clsname or clsname not in self.classes:
            raise TypeError('Not an object instance.')
        cls = self.classes[clsname]
        if methodname not in cls['methods']:
            raise NameError(f"Method '{methodname}' not found in class '{clsname}'.")
        method = cls['methods'][methodname]
        args = [a.strip() for a in args_raw.split(',') if a.strip()]
        argvals = [self.evaluate_expression(a) for a in args]
        local = {'self': obj}
        for p, v in zip(method['params'], argvals): local[p] = v
        return self.execute_function_body(method['body'], local)

    # ------------------------------
    # decorators
    # ------------------------------
    def handle_decorator_define(self, core):
        m = re.match(r'\$(\w+)\s*:\s*(.+)', core)
        if not m:
            raise SyntaxError('Invalid decorator syntax.')
        name, body = m.group(1), m.group(2)
        self.decorators[name] = body
        return None

    # ------------------------------
    # try/except/finally block
    # ------------------------------
    def handle_try_block(self, first_line):
        print("Enter try block lines, end with 'except <ExceptionType>:' or 'finally:' or 'end.'")
        try_lines = []
        except_handlers = []
        finally_lines = []
        mode = 'try'
        while True:
            ln = input()
            if ln.strip().lower() == 'end.':
                break
            if re.match(r'^except\b', ln.strip(), re.IGNORECASE):
                mode = 'except'
                except_type = ln.strip()[6:].strip().rstrip(':').strip() or 'Exception'
                except_handlers.append({'type': except_type, 'body': []})
                continue
            if re.match(r'^finally\b', ln.strip(), re.IGNORECASE):
                mode = 'finally'
                continue
            if mode == 'try':
                try_lines.append(ln)
            elif mode == 'except':
                except_handlers[-1]['body'].append(ln)
            else:
                finally_lines.append(ln)
        try:
            for ln in try_lines:
                self.run_line(ln[:-1] if ln.endswith('.') else ln)
        except Exception as e:
            handled = False
            for h in except_handlers:
                if h['type'] == 'Exception' or h['type'] == type(e).__name__:
                    for ln in h['body']:
                        self.run_line(ln[:-1] if ln.endswith('.') else ln)
                    handled = True
                    break
            if not handled:
                raise
        finally:
            for ln in finally_lines:
                self.run_line(ln[:-1] if ln.endswith('.') else ln)
        return None

    # ------------------------------
    # switch/case block
    # ------------------------------
    def handle_switch_block(self, first_line):
        m = re.match(r'switch\s+(.+):', first_line, re.IGNORECASE)
        if not m:
            raise SyntaxError('Invalid switch header')
        expr = m.group(1).strip()
        val = self.evaluate_expression(expr)
        print("Enter switch cases, use 'case <value>:' and 'default:'; end with 'end.'")
        chosen = False
        while True:
            ln = input()
            if ln.strip().lower() == 'end.':
                break
            if re.match(r'^case\b', ln.strip(), re.IGNORECASE):
                case_val = ln.strip()[4:].strip().rstrip(':').strip()
                case_evaluated = self.evaluate_expression(case_val)
                body = []
                while True:
                    bl = input()
                    if bl.strip().lower().startswith('case') or bl.strip().lower().startswith('default') or bl.strip().lower()=='end.':
                        bk = bl
                        break
                    body.append(bl)
                if val == case_evaluated and not chosen:
                    for b in body:
                        self.run_line(b[:-1] if b.endswith('.') else b)
                    chosen = True
                # handle pushed back header
                if 'bk' in locals():
                    ln = bk
                    del bk
                    continue
            if re.match(r'^default\b', ln.strip(), re.IGNORECASE):
                body = []
                while True:
                    bl = input()
                    if bl.strip().lower() == 'end.': break
                    body.append(bl)
                if not chosen:
                    for b in body:
                        self.run_line(b[:-1] if b.endswith('.') else b)
                break
        return None

# ------------------------------
# Run interpreter
# ------------------------------

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: aurx <file.aurx>")
        sys.exit(1)
    filename = sys.argv[1]
    # your code to open and run the .aurx file
    print(f"Running {filename} with AuraScript interpreter...")
    # e.g. interpreter logic here

if __name__ == '__main__':
    interpreter = AurascriptInterpreter()
    interpreter.start_repl()

