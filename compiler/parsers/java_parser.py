"""
Java Language Recursive-Descent Syntax Checker.
Validates Java class structure, methods, variable declarations, assignments,
System.out.println calls, braces, and semicolons with error recovery.
"""

from typing import List, Optional, Tuple
from compiler.tokens import Token, TokenType
from compiler.ast_nodes import (
    ProgramNode, StatementNode, DeclarationNode, AssignmentNode,
    PrintStatementNode, BlockNode, ClassDefNode, FunctionDefNode,
    ExpressionNode, BinaryOpNode, UnaryOpNode, NumberLiteralNode,
    StringLiteralNode, VariableNode, FunctionCallNode, ReturnNode, GenericNode
)
from compiler.diagnostics import Diagnostic, DiagnosticPhase
from .base_parser import BaseParser


class JavaParseError(Exception):
    pass


class JavaParser(BaseParser):
    """Recursive-descent parser for Java source code."""

    def __init__(self, tokens: List[Token], source_code: str = ""):
        super().__init__(tokens, source_code)
        self.current = 0

    def parse(self) -> Tuple[Optional[ProgramNode], List[Diagnostic]]:
        self.diagnostics = []
        self.current = 0
        statements: List[StatementNode] = []

        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].token_type == TokenType.EOF):
            return ProgramNode(statements=[], line=1, column=1), self.diagnostics

        while not self.is_at_end():
            if self.match(TokenType.SEMICOLON):
                continue

            try:
                item = self.parse_top_level_item()
                if item:
                    statements.append(item)
            except JavaParseError:
                self.synchronize()

        first_tok = self.tokens[0] if self.tokens else Token(TokenType.EOF, "", 1, 1)
        program = ProgramNode(statements=statements, line=first_tok.line, column=first_tok.column)
        return program, self.diagnostics

    def parse_top_level_item(self) -> StatementNode:
        """Parses packages, imports, class definitions, or top-level statements."""
        # 1. Package statement
        if self.match(TokenType.KEYWORD_PACKAGE):
            pkg_name = self.consume_qualified_name()
            self.consume_semicolon("Expected ';' after package declaration.")
            return GenericNode("PackageDeclaration", {"package": pkg_name}, line=self.previous().line, column=1)

        # 2. Import statement
        if self.match(TokenType.KEYWORD_IMPORT):
            imp_name = self.consume_qualified_name()
            self.consume_semicolon("Expected ';' after import statement.")
            return GenericNode("ImportDeclaration", {"import": imp_name}, line=self.previous().line, column=1)

        # 3. Class declaration
        modifiers = []
        while self.match(TokenType.KEYWORD_PUBLIC, TokenType.KEYWORD_PRIVATE, TokenType.KEYWORD_PROTECTED, TokenType.KEYWORD_STATIC):
            modifiers.append(self.previous().lexeme)

        if self.match(TokenType.KEYWORD_CLASS):
            return self.parse_class_declaration(modifiers)

        # 4. If modifiers were seen but not followed by class, could be a method or field
        if modifiers:
            return self.parse_method_or_field(modifiers)

        # 5. Direct statement (declarations, expressions, println, etc.)
        return self.parse_statement()

    def parse_class_declaration(self, modifiers: List[str]) -> ClassDefNode:
        class_tok = self.previous()
        if not self.match(TokenType.IDENTIFIER):
            self.error_at(self.peek(), "SYN_JAVA_001", "Expected class name after 'class' keyword.")
            raise JavaParseError()

        class_name = self.previous().lexeme
        super_classes = []

        if self.match(TokenType.KEYWORD_EXTENDS):
            if self.match(TokenType.IDENTIFIER):
                super_classes.append(self.previous().lexeme)

        if self.match(TokenType.KEYWORD_IMPLEMENTS):
            while True:
                if self.match(TokenType.IDENTIFIER):
                    super_classes.append(self.previous().lexeme)
                if not self.match(TokenType.COMMA):
                    break

        if not self.match(TokenType.LBRACE):
            self.error_at(self.peek(), "SYN_JAVA_002", f"Expected '{{' to open body of class '{class_name}'.")
            raise JavaParseError()

        lbrace_tok = self.previous()
        members: List[StatementNode] = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            try:
                m = self.parse_class_member()
                if m:
                    members.append(m)
            except JavaParseError:
                self.synchronize()

        if not self.match(TokenType.RBRACE):
            self.error_at(
                self.peek(),
                "SYN_JAVA_002",
                f"Expected '}}' closing class '{class_name}' opened at line {lbrace_tok.line}, column {lbrace_tok.column}."
            )
            raise JavaParseError()

        return ClassDefNode(
            name=class_name,
            modifiers=modifiers,
            super_classes=super_classes,
            members=members,
            line=class_tok.line,
            column=class_tok.column
        )

    def parse_class_member(self) -> StatementNode:
        # Check annotations like @Override
        while self.match(TokenType.ANNOTATION):
            pass

        modifiers = []
        while self.match(TokenType.KEYWORD_PUBLIC, TokenType.KEYWORD_PRIVATE, TokenType.KEYWORD_PROTECTED, TokenType.KEYWORD_STATIC):
            modifiers.append(self.previous().lexeme)

        return self.parse_method_or_field(modifiers)

    def parse_method_or_field(self, modifiers: List[str]) -> StatementNode:
        # Must have a type (void, int, String, etc.)
        type_str = self.consume_type_name()
        if not type_str:
            self.error_at(self.peek(), "SYN_JAVA_003", "Expected type in class member declaration.")
            raise JavaParseError()

        name_tok = self.advance()
        name = name_tok.lexeme

        # If next is '(', it's a method! e.g. public static void main(String[] args)
        if self.match(TokenType.LPAREN):
            params = []
            if not self.check(TokenType.RPAREN):
                while True:
                    p_type = self.consume_type_name()
                    p_name = self.advance().lexeme if self.check(TokenType.IDENTIFIER) else ""
                    params.append(f"{p_type} {p_name}".strip())
                    if not self.match(TokenType.COMMA):
                        break

            if not self.match(TokenType.RPAREN):
                self.error_at(self.peek(), "SYN_JAVA_004", f"Expected ')' closing method parameters for '{name}'.")
                raise JavaParseError()

            if self.check(TokenType.LBRACE):
                body = self.parse_block()
                return FunctionDefNode(
                    return_type=type_str,
                    name=name,
                    parameters=params,
                    body=body,
                    line=name_tok.line,
                    column=name_tok.column
                )
            else:
                self.consume_semicolon(f"Expected ';' or '{{' for method '{name}'.")
                return FunctionDefNode(
                    return_type=type_str,
                    name=name,
                    parameters=params,
                    body=None,
                    line=name_tok.line,
                    column=name_tok.column
                )

        # Otherwise, field declaration: int a = 10;
        expr = None
        if self.match(TokenType.OP_ASSIGN):
            expr = self.parse_expression()
        self.consume_semicolon(f"Expected ';' after field declaration '{name}'.")
        return DeclarationNode(
            var_type=type_str,
            identifier=name,
            expression=expr if expr else NumberLiteralNode(0, "0", "int"),
            line=name_tok.line,
            column=name_tok.column
        )

    def parse_statement(self) -> StatementNode:
        """Parses executable Java statements."""
        # Block { ... }
        if self.check(TokenType.LBRACE):
            return self.parse_block()

        # Variable declaration if starting with a type keyword
        if self.check(
            TokenType.KEYWORD_INT, TokenType.KEYWORD_DOUBLE, TokenType.KEYWORD_FLOAT,
            TokenType.KEYWORD_CHAR, TokenType.KEYWORD_BOOLEAN, TokenType.KEYWORD_STRING
        ):
            type_tok = self.advance()
            type_name = type_tok.lexeme
            # Support array brackets: String[]
            if self.match(TokenType.LBRACKET):
                self.match(TokenType.RBRACKET)
                type_name += "[]"

            if not self.match(TokenType.IDENTIFIER):
                self.error_at(self.peek(), "SYN_JAVA_005", f"Expected identifier after type '{type_name}'.")
                raise JavaParseError()

            name_tok = self.previous()
            expr = None
            if self.match(TokenType.OP_ASSIGN):
                expr = self.parse_expression()

            self.consume_semicolon(f"Expected ';' after variable declaration of '{name_tok.lexeme}'.")
            return DeclarationNode(
                var_type=type_name,
                identifier=name_tok.lexeme,
                expression=expr if expr else NumberLiteralNode(0, "0", "int"),
                line=type_tok.line,
                column=type_tok.column
            )

        # Return statement
        if self.match(TokenType.KEYWORD_RETURN):
            ret_tok = self.previous()
            expr = self.parse_expression() if not self.check(TokenType.SEMICOLON) else None
            self.consume_semicolon("Expected ';' after return statement.")
            return ReturnNode(expression=expr, line=ret_tok.line, column=ret_tok.column)

        # Print statement: System.out.println(...)
        if self.check_system_out():
            return self.parse_system_out_println()

        # Identifier: could be assignment or method call
        if self.check(TokenType.IDENTIFIER):
            # Check for qualified name: e.g. System.out.println
            if self.peek_next().token_type == TokenType.OP_ASSIGN or self.peek_next().token_type.name.endswith("_ASSIGN"):
                name_tok = self.advance()
                self.advance()  # consume assign op
                expr = self.parse_expression()
                self.consume_semicolon(f"Expected ';' after assignment to '{name_tok.lexeme}'.")
                return AssignmentNode(identifier=name_tok.lexeme, expression=expr, line=name_tok.line, column=name_tok.column)
            else:
                expr = self.parse_expression()
                self.consume_semicolon("Expected ';' after expression statement.")
                return GenericNode("ExpressionStatement", {"expression": str(expr)}, line=expr.line, column=expr.column)

        tok = self.peek()
        self.error_at(tok, "SYN_JAVA_006", f"Unexpected token '{tok.lexeme}' in Java statement.")
        raise JavaParseError()

    def check_system_out(self) -> bool:
        if self.check(TokenType.IDENTIFIER) and self.peek().lexeme == "System":
            return True
        return False

    def parse_system_out_println(self) -> PrintStatementNode:
        start_tok = self.advance()  # consume System
        while self.match(TokenType.DOT):
            if self.check(TokenType.IDENTIFIER):
                self.advance()

        if not self.match(TokenType.LPAREN):
            self.error_at(self.peek(), "SYN_JAVA_007", "Expected '(' after System.out.println.")
            raise JavaParseError()

        lparen_tok = self.previous()
        expr = self.parse_expression() if not self.check(TokenType.RPAREN) else StringLiteralNode("", line=lparen_tok.line, column=lparen_tok.column)

        if not self.match(TokenType.RPAREN):
            self.error_at(self.peek(), "SYN_JAVA_008", "Expected ')' closing System.out.println arguments.")
            raise JavaParseError()

        self.consume_semicolon("Expected ';' after System.out.println statement.")
        return PrintStatementNode(expression=expr, line=start_tok.line, column=start_tok.column)

    def parse_block(self) -> BlockNode:
        lbrace = self.advance()
        stmts: List[StatementNode] = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.SEMICOLON):
                continue
            try:
                stmts.append(self.parse_statement())
            except JavaParseError:
                self.synchronize()

        if not self.match(TokenType.RBRACE):
            self.error_at(self.peek(), "SYN_JAVA_002", f"Expected '}}' closing block opened at line {lbrace.line}, column {lbrace.column}.")
            raise JavaParseError()

        return BlockNode(statements=stmts, line=lbrace.line, column=lbrace.column)

    # -------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------

    def parse_expression(self) -> ExpressionNode:
        return self.parse_additive()

    def parse_additive(self) -> ExpressionNode:
        expr = self.parse_multiplicative()
        while self.match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op = self.previous().lexeme
            right = self.parse_multiplicative()
            expr = BinaryOpNode(left=expr, operator=op, right=right, line=expr.line, column=expr.column)
        return expr

    def parse_multiplicative(self) -> ExpressionNode:
        expr = self.parse_factor()
        while self.match(TokenType.OP_MULTIPLY, TokenType.OP_DIVIDE, TokenType.OP_MOD):
            op = self.previous().lexeme
            right = self.parse_factor()
            expr = BinaryOpNode(left=expr, operator=op, right=right, line=expr.line, column=expr.column)
        return expr

    def parse_factor(self) -> ExpressionNode:
        if self.match(TokenType.OP_PLUS, TokenType.OP_MINUS, TokenType.OP_LOGICAL_NOT):
            op_tok = self.previous()
            operand = self.parse_factor()
            return UnaryOpNode(operator=op_tok.lexeme, operand=operand, line=op_tok.line, column=op_tok.column)

        if self.match(TokenType.INT_LITERAL):
            tok = self.previous()
            return NumberLiteralNode(value=tok.value if tok.value is not None else int(tok.lexeme.rstrip("lL")), raw=tok.lexeme, num_type="int", line=tok.line, column=tok.column)

        if self.match(TokenType.FLOAT_LITERAL):
            tok = self.previous()
            return NumberLiteralNode(value=tok.value if tok.value is not None else float(tok.lexeme.rstrip("fFdD")), raw=tok.lexeme, num_type="float", line=tok.line, column=tok.column)

        if self.match(TokenType.STRING_LITERAL):
            tok = self.previous()
            return StringLiteralNode(value=tok.value or tok.lexeme, line=tok.line, column=tok.column)

        if self.match(TokenType.CHAR_LITERAL):
            tok = self.previous()
            return StringLiteralNode(value=tok.value or tok.lexeme, line=tok.line, column=tok.column)

        if self.match(TokenType.IDENTIFIER):
            name = self.previous().lexeme
            # Handle chained access: a.b.c or calls
            while self.match(TokenType.DOT):
                if self.match(TokenType.IDENTIFIER):
                    name += "." + self.previous().lexeme

            if self.match(TokenType.LPAREN):
                # Function call
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expression())
                        if not self.match(TokenType.COMMA):
                            break
                self.match(TokenType.RPAREN)
                return FunctionCallNode(callee=name, arguments=args, line=self.previous().line, column=1)

            return VariableNode(name=name, line=self.previous().line, column=self.previous().column)

        if self.match(TokenType.LPAREN):
            lparen = self.previous()
            expr = self.parse_expression()
            if not self.match(TokenType.RPAREN):
                self.error_at(self.peek(), "SYN_JAVA_008", f"Expected closing ')' to match '(' from line {lparen.line}, column {lparen.column}.")
                raise JavaParseError()
            return expr

        curr = self.peek()
        self.error_at(curr, "SYN_JAVA_009", f"Expected expression in Java code, found '{curr.lexeme}'.")
        raise JavaParseError()

    # -------------------------------------------------------------
    # Helper & Recovery Methods
    # -------------------------------------------------------------

    def consume_qualified_name(self) -> str:
        parts = []
        if self.match(TokenType.IDENTIFIER):
            parts.append(self.previous().lexeme)
            while self.match(TokenType.DOT):
                if self.match(TokenType.IDENTIFIER, TokenType.OP_MULTIPLY):
                    parts.append(self.previous().lexeme)
        return ".".join(parts)

    def consume_type_name(self) -> Optional[str]:
        if self.match(
            TokenType.KEYWORD_INT, TokenType.KEYWORD_DOUBLE, TokenType.KEYWORD_FLOAT,
            TokenType.KEYWORD_CHAR, TokenType.KEYWORD_BOOLEAN, TokenType.KEYWORD_STRING,
            TokenType.KEYWORD_VOID, TokenType.IDENTIFIER
        ):
            t = self.previous().lexeme
            while self.match(TokenType.LBRACKET):
                self.match(TokenType.RBRACKET)
                t += "[]"
            return t
        return None

    def consume_semicolon(self, message: str) -> None:
        if self.check(TokenType.SEMICOLON):
            self.advance()
            return
        prev = self.previous()
        self.error_at(prev, "SYN001", f"Syntax error at line {prev.line}, column {prev.column + len(prev.lexeme)}: {message}", "Add ';' at the end of statement.")

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, *types: TokenType) -> bool:
        if self.is_at_end():
            return TokenType.EOF in types
        return self.peek().token_type in types

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]

    def peek_next(self) -> Token:
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return self.tokens[-1]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def error_at(self, token: Token, code: str, message: str, suggestion: str = "") -> None:
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
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            if self.peek().token_type in (
                TokenType.KEYWORD_PUBLIC, TokenType.KEYWORD_PRIVATE, TokenType.KEYWORD_CLASS,
                TokenType.KEYWORD_INT, TokenType.KEYWORD_VOID, TokenType.KEYWORD_RETURN,
                TokenType.RBRACE
            ):
                return
            self.advance()

