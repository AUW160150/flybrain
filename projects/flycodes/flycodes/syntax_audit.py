"""Syntax-only diagnostic interpretations, independent of task text and test answers.

Bracket and indentation repairs are hypotheses about intended syntax, not proof
of semantic equivalence. No generated program is executed with Python exec/eval.
"""
import ast
import difflib
import io
import re
import tokenize

BLOCK = re.compile(r'^(def\s|if\s|elif\s|else\s*:|else$|for\s|while\s)')
PAIRS = {'(': ')', '[': ']', '{': '}'}
LAYOUT = {tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE, tokenize.NL,
          tokenize.ENDMARKER, tokenize.ENCODING, tokenize.COMMENT}


def syntax_error(code):
    try:
        # Compile checks duplicate arguments and context errors missed by ast.parse.
        # The code object is discarded and never executed.
        compile(code, '<syntax-audit>', 'exec')
        return None
    except (SyntaxError, ValueError, OverflowError) as exc:
        return str(exc)


def line_tokens(line):
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(line + '\n').readline):
            if token.type == tokenize.ERRORTOKEN and not token.string.isspace():
                raise ValueError('Unterminated string or unrecognized token; no literal inferred')
            tokens.append(token)
    except tokenize.TokenError as exc:
        if not exc.args[0].endswith('EOF in multi-line statement'):
            raise ValueError('String/lexical repair requires guessing') from exc
    return tokens


def protected_tokens(code):
    """Every name, keyword, literal, comma and computation operator is immutable."""
    return [(t.type, t.string) for line in code.splitlines() for t in line_tokens(line.strip())
            if t.type not in LAYOUT and not (t.type == tokenize.OP and t.string in '()[]{}:')]


def repair_line(line, line_number):
    prefix = line[:len(line) - len(line.lstrip())]
    body = line.strip()
    if not body or body.startswith('#'):
        return line, []
    tokens = line_tokens(body)
    stack = []
    replacements = []
    changes = []
    terminal_colon = None
    comment_start = len(body)
    for token in tokens:
        value = token.string
        if token.type == tokenize.COMMENT:
            comment_start = token.start[1]
        if token.type != tokenize.OP:
            continue
        if value in PAIRS:
            stack.append(value)
        elif value in PAIRS.values():
            replacement = PAIRS[stack.pop()] if stack else ''
            if replacement != value:
                replacements.append((token.start[1], token.end[1], replacement))
                changes.append(f'line {line_number}: match/remove closing delimiter {value!r} -> {replacement!r}')
        elif value == ':' and not stack:
            terminal_colon = token.start[1]
    is_block = bool(BLOCK.match(body))
    tail = body[:comment_start].rstrip()
    if is_block and tail.endswith(':') and any(t.type == tokenize.OP and t.string == ':' and t.start[1] == len(tail) - 1 for t in tokens):
        terminal_colon = len(tail) - 1
    if terminal_colon != len(tail) - 1:
        terminal_colon = None
    if terminal_colon is not None and not is_block:
        replacements.append((terminal_colon, terminal_colon + 1, ''))
        changes.append(f'line {line_number}: remove trailing colon from simple statement')
    # A colon inside unfinished brackets is still a slice/dictionary token;
    # never remove it as if it were a suite marker.
    insertion = terminal_colon if is_block and terminal_colon is not None else len(tail)
    closers = ''.join(PAIRS[x] for x in reversed(stack))
    if closers:
        replacements.append((insertion, insertion, closers))
        changes.append(f'line {line_number}: append missing closing delimiters {closers!r}')
    for start, end, replacement in sorted(replacements, reverse=True):
        body = body[:start] + replacement + body[end:]
    # A missing suite colon is added only at the end of a header.
    if is_block and terminal_colon is None:
        comment = body.find('#') if not any(t.type == tokenize.STRING for t in tokens) else -1
        at = len(body[:comment].rstrip()) if comment >= 0 else len(body)
        body = body[:at] + ':' + body[at:]
        changes.append(f'line {line_number}: append header colon')
    return prefix + body, changes


def interpret(code):
    original_error = syntax_error(code)
    if original_error is None:
        return dict(status='already_valid', code=code, edits=[], original_error=None,
                    remaining_error=None, protected_tokens_preserved=True, diff='')
    edits = []
    candidate = code
    try:
        fingerprint = protected_tokens(code)
        lines = []
        for index, line in enumerate(code.splitlines(), 1):
            repaired, changes = repair_line(line, index)
            lines.append(repaired)
            edits.extend(changes)
        candidate = '\n'.join(lines) + '\n'
        # There is only one possible function-body indentation for straight-line
        # statements with no nested suites. Never guess nested control flow.
        nonempty = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith('#')]
        flat_body = len(nonempty) > 1 and nonempty[0].startswith('def ') and not any(BLOCK.match(x) for x in nonempty[1:])
        if syntax_error(candidate) and flat_body:
            candidate = nonempty[0] + '\n' + '\n'.join('    ' + x for x in nonempty[1:]) + '\n'
            edits.append('normalize indentation inside a single function with no nested suites')
        if protected_tokens(candidate) != fingerprint:
            raise ValueError('Protected token stream changed')
        error = syntax_error(candidate)
        return dict(status='repaired' if error is None else 'unresolved', code=candidate,
                    edits=edits, original_error=original_error, remaining_error=error,
                    protected_tokens_preserved=True,
                    diff=''.join(difflib.unified_diff(code.splitlines(True), candidate.splitlines(True),
                                                  fromfile='original.py', tofile='syntax-interpretation.py')))
    except ValueError as exc:
        return dict(status='unresolved', code=code, edits=[], original_error=original_error,
                    remaining_error=str(exc), protected_tokens_preserved=True, diff='')
