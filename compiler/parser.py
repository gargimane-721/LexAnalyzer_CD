"""
Recursive-Descent Parser for the C-like source language.
Constructs an Abstract Syntax Tree (AST), validates syntax, enforces operator precedence,
and recovers from errors to report multiple syntax issues in a single pass.
"""

from typing import List, Optional, Tuple
from .tokens import Token, TokenType
from .ast_nodes import (
    ProgramNode, StatementNode, DeclarationNode, AssignmentNode,
    PrintStatementNode, ExpressionNode, BinaryOpNode, UnaryOpNode,
    NumberLiteralNode, VariableNode
)
from .diagnostics import Diagnostic, DiagnosticPhase


class ParseError(Exception):
    """Internal exception raised during fatal parse errors to trigger synchronization."""
    pass


class Parser:
    """Hand-written recursive-descent parser with error recovery."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.diagnostics: List[Diagnostic] = []

    def parse(self) -> Tuple[Optional[ProgramNode], List[Diagnostic]]:
        """Parses the token stream into a Program AST node."""
        self.diagnostics = []
        self.current = 0
        statements: List[StatementNode] = []

        while not self.is_at_end():
            # Skip any orphan semicolons
            if self.match(TokenType.SEMICOLON):
                continue

            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParseError:
                self.synchronize()

        first_tok = self.tokens[0] if self.tokens else Token(TokenType.EOF, "", 1, 1)
        program_node = ProgramNode(
            statements=statements,
            line=first_tok.line,
            column=first_tok.column
        )
        return program_node, self.diagnostics

    # -------------------------------------------------------------
    # Statement Parsing
    # -------------------------------------------------------------

    def parse_statement(self) -> StatementNode:
        """Dispatches to the appropriate statement parser."""
        if self.match(TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT):
            return self.parse_declaration()

        if self.check(TokenType.IDENTIFIER):
            return self.parse_assignment()

        if self.match(TokenType.KEYWORD_PRINT):
            return self.parse_print_statement()

        tok = self.peek()
        self.error_at(
            tok,
            "SYN006",
            f"Unexpected token '{tok.lexeme}'. Expected variable declaration, assignment, or print statement.",
            "Start statement with 'int', 'float', a variable name, or 'print(...)';"
        )
        raise ParseError()

    def parse_declaration(self) -> DeclarationNode:
        """declaration -> TYPE IDENTIFIER '=' expression ';'"""
        type_token = self.previous()
        var_type = type_token.lexeme

        if not self.match(TokenType.IDENTIFIER):
            current_tok = self.peek()
            self.error_at(
                current_tok,
                "SYN003",
                f"Expected identifier after type '{var_type}', found '{current_tok.lexeme}'.",
                f"Provide a valid variable name: e.g. '{var_type} x = 10;'"
            )
            raise ParseError()

        name_token = self.previous()
        ident_name = name_token.lexeme

        if not self.match(TokenType.OP_ASSIGN):
            current_tok = self.peek()
            self.error_at(
                current_tok,
                "SYN004",
                f"Expected '=' after identifier '{ident_name}' in declaration, found '{current_tok.lexeme}'.",
                f"Initialize the variable with '=': e.g. '{var_type} {ident_name} = 0;'"
            )
            raise ParseError()

        expr = self.parse_expression()

        self.consume_semicolon(
            f"Expected ';' after declaration of '{ident_name}'.",
            f"Add ';' at the end of the line: e.g. '{var_type} {ident_name} = ...;'"
        )

        return DeclarationNode(
            var_type=var_type,
            identifier=ident_name,
            expression=expr,
            line=type_token.line,
            column=type_token.column
        )

    def parse_assignment(self) -> AssignmentNode:
        """assignment -> IDENTIFIER '=' expression ';'"""
        name_token = self.advance()
        ident_name = name_token.lexeme

        if not self.match(TokenType.OP_ASSIGN):
            current_tok = self.peek()
            self.error_at(
                current_tok,
                "SYN004",
                f"Expected '=' after variable '{ident_name}' in assignment, found '{current_tok.lexeme}'.",
                f"Use '=' to assign a value: e.g. '{ident_name} = 5;'"
            )
            raise ParseError()

        expr = self.parse_expression()

        self.consume_semicolon(
            f"Expected ';' after assignment to '{ident_name}'.",
            f"Add ';' at the end of the assignment statement: e.g. '{ident_name} = ...;'"
        )

        return AssignmentNode(
            identifier=ident_name,
            expression=expr,
            line=name_token.line,
            column=name_token.column
        )

    def parse_print_statement(self) -> PrintStatementNode:
        """print_statement -> 'print' '(' expression ')' ';'"""
        print_tok = self.previous()

        if not self.match(TokenType.LPAREN):
            curr = self.peek()
            self.error_at(
                curr,
                "SYN007",
                f"Expected '(' after 'print', found '{curr.lexeme}'.",
                "Format print statement as: 'print(expression);'"
            )
            raise ParseError()

        lparen_tok = self.previous()
        expr = self.parse_expression()

        if not self.match(TokenType.RPAREN):
            curr = self.peek()
            self.error_at(
                curr,
                "SYN002",
                f"Expected ')' after expression in print statement, found '{curr.lexeme}'.",
                f"Close the parenthesis opened at line {lparen_tok.line}, column {lparen_tok.column}."
            )
            raise ParseError()

        self.consume_semicolon(
            "Expected ';' after print statement.",
            "Add ';' at the end of the print statement: e.g. 'print(x);'"
        )

        return PrintStatementNode(
            expression=expr,
            line=print_tok.line,
            column=print_tok.column
        )

    # -------------------------------------------------------------
    # Expression Parsing (Precedence: () -> unary -> * / -> + -)
    # -------------------------------------------------------------

    def parse_expression(self) -> ExpressionNode:
        """expression -> term (('+' | '-') term)*"""
        expr = self.parse_term()

        while self.match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_tok = self.previous()
            right = self.parse_term()
            expr = BinaryOpNode(
                left=expr,
                operator=op_tok.lexeme,
                right=right,
                line=op_tok.line,
                column=op_tok.column
            )

        return expr

    def parse_term(self) -> ExpressionNode:
        """term -> factor (('*' | '/') factor)*"""
        term = self.parse_factor()

        while self.match(TokenType.OP_MULTIPLY, TokenType.OP_DIVIDE):
            op_tok = self.previous()
            right = self.parse_factor()
            term = BinaryOpNode(
                left=term,
                operator=op_tok.lexeme,
                right=right,
                line=op_tok.line,
                column=op_tok.column
            )

        return term

    def parse_factor(self) -> ExpressionNode:
        """factor -> NUMBER | IDENTIFIER | '(' expression ')' | unary_expression"""
        # Unary operators: + or -
        if self.match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_tok = self.previous()
            operand = self.parse_factor()
            return UnaryOpNode(
                operator=op_tok.lexeme,
                operand=operand,
                line=op_tok.line,
                column=op_tok.column
            )

        # Integer literal
        if self.match(TokenType.INT_LITERAL):
            tok = self.previous()
            return NumberLiteralNode(
                value=tok.value if tok.value is not None else int(tok.lexeme),
                raw=tok.lexeme,
                num_type="int",
                line=tok.line,
                column=tok.column
            )

        # Float literal
        if self.match(TokenType.FLOAT_LITERAL):
            tok = self.previous()
            return NumberLiteralNode(
                value=tok.value if tok.value is not None else float(tok.lexeme),
                raw=tok.lexeme,
                num_type="float",
                line=tok.line,
                column=tok.column
            )

        # Identifier
        if self.match(TokenType.IDENTIFIER):
            tok = self.previous()
            return VariableNode(
                name=tok.lexeme,
                line=tok.line,
                column=tok.column
            )

        # Grouped expression '(' expression ')'
        if self.match(TokenType.LPAREN):
            lparen_tok = self.previous()
            expr = self.parse_expression()
            if not self.match(TokenType.RPAREN):
                curr = self.peek()
                self.error_at(
                    curr,
                    "SYN002",
                    f"Expected closing ')' to match '(' from line {lparen_tok.line}, column {lparen_tok.column}.",
                    "Ensure every opened parenthesis has a matching closing parenthesis ')'."
                )
                raise ParseError()
            return expr

        # Unexpected token in expression
        curr = self.peek()
        self.error_at(
            curr,
            "SYN005",
            f"Expected expression (number, identifier, or '('), found '{curr.lexeme}'.",
            "Provide a valid value or variable name."
        )
        raise ParseError()

    # -------------------------------------------------------------
    # Helper & Recovery Methods
    # -------------------------------------------------------------

    def consume_semicolon(self, message: str, suggestion: str) -> None:
        """Checks and consumes a semicolon or logs a SYN001 error."""
        if self.check(TokenType.SEMICOLON):
            self.advance()
            return

        # Semicolon is missing
        prev = self.previous()
        self.error_at(
            prev,
            "SYN001",
            f"Syntax error at line {prev.line}, column {prev.column + len(prev.lexeme)}: {message}",
            suggestion
        )
        # Note: Do not raise ParseError here to permit smooth continuation if the next line is clear

    def match(self, *types: TokenType) -> bool:
        """Returns True and advances if current token matches any given type."""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """Checks if current token is of the specified type without consuming."""
        if self.is_at_end():
            return token_type == TokenType.EOF
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        """Consumes the current token and returns it."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """Checks if parser has reached the end of the token stream."""
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        """Returns current token without advancing."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]

    def previous(self) -> Token:
        """Returns most recently consumed token."""
        return self.tokens[self.current - 1]

    def error_at(self, token: Token, code: str, message: str, suggestion: str = "") -> None:
        """Logs a syntax diagnostic."""
        self.diagnostics.append(
            Diagnostic(
                phase=DiagnosticPhase.SYNTAX,
                error_code=code,
                message=message,
                line=token.line,
                column=token.column,
                suggestion=suggestion
            )
        )

    def synchronize(self) -> None:
        """Discards tokens until a statement boundary is found to resume parsing."""
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            if self.peek().token_type in (
                TokenType.KEYWORD_INT,
                TokenType.KEYWORD_FLOAT,
                TokenType.KEYWORD_PRINT,
            ):
                return

            self.advance()

