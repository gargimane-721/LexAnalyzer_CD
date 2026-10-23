"""
C Language Recursive-Descent Parser.
Parses C statements, functions (main), preprocessor directives, blocks, expressions,
and control structures with panic-mode error recovery.
"""

from typing import List, Optional, Tuple, Union
from compiler.tokens import Token, TokenType
from compiler.ast_nodes import (
    ProgramNode, StatementNode, DeclarationNode, AssignmentNode,
    PrintStatementNode, ExpressionNode, BinaryOpNode, UnaryOpNode,
    NumberLiteralNode, StringLiteralNode, VariableNode, FunctionCallNode,
    ReturnNode, BlockNode, IfNode, WhileNode, FunctionDefNode, PreprocessorNode
)
from compiler.diagnostics import Diagnostic, DiagnosticPhase
from .base_parser import BaseParser


class ParseError(Exception):
    """Raised to trigger panic-mode synchronization upon syntax error."""
    pass


class CParser(BaseParser):
    """Recursive-descent parser for C syntax."""

    def __init__(self, tokens: List[Token], source_code: str = ""):
        super().__init__(tokens, source_code)
        self.current = 0

    def parse(self) -> Tuple[Optional[ProgramNode], List[Diagnostic]]:
        self.diagnostics = []
        self.current = 0
        statements: List[StatementNode] = []

        while not self.is_at_end():
            # Skip lone semicolons
            if self.match(TokenType.SEMICOLON):
                continue

            try:
                stmt = self.parse_item()
                if stmt:
                    statements.append(stmt)
            except ParseError:
                self.synchronize()

        first_tok = self.tokens[0] if self.tokens else Token(TokenType.EOF, "", 1, 1)
        program = ProgramNode(
            statements=statements,
            line=first_tok.line,
            column=first_tok.column
        )
        return program, self.diagnostics

    def parse_item(self) -> StatementNode:
        """Parses a top-level item or statement in C."""
        # 1. Preprocessor directive (#include, #define)
        if self.match(TokenType.PREPROCESSOR):
            tok = self.previous()
            return PreprocessorNode(directive=tok.lexeme, line=tok.line, column=tok.column)

        # 2. Block statement { ... }
        if self.check(TokenType.LBRACE):
            return self.parse_block()

        # 3. Type keywords: may start a variable declaration or a function definition!
        if self.check(
            TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT, TokenType.KEYWORD_CHAR,
            TokenType.KEYWORD_DOUBLE, TokenType.KEYWORD_VOID
        ):
            return self.parse_declaration_or_function()

        # 4. Return statement
        if self.match(TokenType.KEYWORD_RETURN):
            return self.parse_return()

        # 5. Control structures
        if self.match(TokenType.KEYWORD_IF):
            return self.parse_if()
        if self.match(TokenType.KEYWORD_WHILE):
            return self.parse_while()

        # 6. Print statement (educational keyword or function call)
        if self.match(TokenType.KEYWORD_PRINT):
            return self.parse_print_statement()

        # 7. Identifier: assignment or function call statement (e.g. printf(...); or x = 5;)
        if self.check(TokenType.IDENTIFIER):
            # Check lookahead: if next token is '(', it's a call statement; if '=', it's assignment
            if self.peek_next().token_type == TokenType.LPAREN:
                call_expr = self.parse_function_call()
                self.consume_semicolon("Expected ';' after function call statement.")
                return call_expr
            return self.parse_assignment()

        tok = self.peek()
        self.error_at(
            tok,
            "SYN006",
            f"Unexpected token '{tok.lexeme}'. Expected declaration, statement, or function.",
            "Check syntax: e.g. 'int x = 10;', 'int main() { ... }', or 'return 0;'"
        )
        raise ParseError()

    def parse_declaration_or_function(self) -> StatementNode:
        """Dispatches between variable declaration and function definition."""
        type_tok = self.advance()
        var_type = type_tok.lexeme

        if not self.match(TokenType.IDENTIFIER):
            curr = self.peek()
            self.error_at(
                curr,
                "SYN003",
                f"Expected identifier after type '{var_type}', found '{curr.lexeme}'.",
                f"Provide a name: e.g. '{var_type} x = 10;' or '{var_type} main()'"
            )
            raise ParseError()

        name_tok = self.previous()
        ident_name = name_tok.lexeme

        # If next is '(', this is a function definition! e.g. int main() { ... }
        if self.match(TokenType.LPAREN):
            params = []
            if not self.check(TokenType.RPAREN):
                while True:
                    if self.match(
                        TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT, TokenType.KEYWORD_CHAR,
                        TokenType.KEYWORD_DOUBLE, TokenType.KEYWORD_VOID
                    ):
                        p_type = self.previous().lexeme
                        p_name = self.advance().lexeme if self.check(TokenType.IDENTIFIER) else ""
                        params.append(f"{p_type} {p_name}".strip())
                    elif self.match(TokenType.IDENTIFIER):
                        params.append(self.previous().lexeme)
                    if not self.match(TokenType.COMMA):
                        break

            if not self.match(TokenType.RPAREN):
                curr = self.peek()
                self.error_at(
                    curr,
                    "SYN002",
                    f"Expected ')' closing parameter list of '{ident_name}'.",
                    "Close parameter list with ')'."
                )
                raise ParseError()

            # Function body must be a block { ... }
            if self.check(TokenType.LBRACE):
                body = self.parse_block()
                return FunctionDefNode(
                    return_type=var_type,
                    name=ident_name,
                    parameters=params,
                    body=body,
                    line=type_tok.line,
                    column=type_tok.column
                )
            else:
                self.consume_semicolon(f"Expected ';' or '{{' for function '{ident_name}'.")
                return FunctionDefNode(
                    return_type=var_type,
                    name=ident_name,
                    parameters=params,
                    body=None,
                    line=type_tok.line,
                    column=type_tok.column
                )

        # Otherwise, this is a variable declaration: e.g. int a = 10; or int a;
        expr = None
        if self.match(TokenType.OP_ASSIGN):
            expr = self.parse_expression()
        elif not self.check(TokenType.SEMICOLON):
            curr = self.peek()
            self.error_at(
                curr,
                "SYN004",
                f"Expected '=' after identifier '{ident_name}' in declaration, found '{curr.lexeme}'.",
                f"Initialize the variable with '=': e.g. '{var_type} {ident_name} = 0;'"
            )
            raise ParseError()

        self.consume_semicolon(
            f"Expected ';' after declaration of '{ident_name}'.",
            f"Add ';' at the end: e.g. '{var_type} {ident_name} = ...;'"
        )

        return DeclarationNode(
            var_type=var_type,
            identifier=ident_name,
            expression=expr if expr else NumberLiteralNode(0, "0", "int", line=name_tok.line, column=name_tok.column),
            line=type_tok.line,
            column=type_tok.column
        )

    def parse_assignment(self) -> AssignmentNode:
        """assignment -> IDENTIFIER '=' expression ';'"""
        name_token = self.advance()
        ident_name = name_token.lexeme

        if not self.match(TokenType.OP_ASSIGN, TokenType.OP_PLUS_ASSIGN, TokenType.OP_MINUS_ASSIGN, TokenType.OP_MUL_ASSIGN, TokenType.OP_DIV_ASSIGN):
            curr = self.peek()
            self.error_at(
                curr,
                "SYN004",
                f"Expected '=' after variable '{ident_name}' in assignment, found '{curr.lexeme}'.",
                f"Use '=' to assign a value: e.g. '{ident_name} = 5;'"
            )
            raise ParseError()

        expr = self.parse_expression()
        self.consume_semicolon(
            f"Expected ';' after assignment to '{ident_name}'.",
            f"Add ';' at the end: e.g. '{ident_name} = ...;'"
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
                f"Close parenthesis opened at line {lparen_tok.line}, column {lparen_tok.column}."
            )
            raise ParseError()

        self.consume_semicolon(
            "Expected ';' after print statement.",
            "Add ';' at the end: e.g. 'print(x);'"
        )

        return PrintStatementNode(
            expression=expr,
            line=print_tok.line,
            column=print_tok.column
        )

    def parse_return(self) -> ReturnNode:
        ret_tok = self.previous()
        expr = None
        if not self.check(TokenType.SEMICOLON):
            expr = self.parse_expression()

        self.consume_semicolon("Expected ';' after return statement.")
        return ReturnNode(expression=expr, line=ret_tok.line, column=ret_tok.column)

    def parse_block(self) -> BlockNode:
        lbrace_tok = self.advance()
        stmts: List[StatementNode] = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.SEMICOLON):
                continue
            try:
                st = self.parse_item()
                if st:
                    stmts.append(st)
            except ParseError:
                self.synchronize()

        if not self.match(TokenType.RBRACE):
            curr = self.peek()
            self.error_at(
                curr,
                "SYN002",
                f"Expected '}}' closing block opened at line {lbrace_tok.line}, column {lbrace_tok.column}.",
                "Close block with '}'."
            )
            raise ParseError()

        return BlockNode(statements=stmts, line=lbrace_tok.line, column=lbrace_tok.column)

    def parse_if(self) -> IfNode:
        if_tok = self.previous()
        if not self.match(TokenType.LPAREN):
            self.error_at(self.peek(), "SYN002", "Expected '(' after 'if'.")
            raise ParseError()
        cond = self.parse_expression()
        if not self.match(TokenType.RPAREN):
            self.error_at(self.peek(), "SYN002", "Expected ')' closing if condition.")
            raise ParseError()

        then_branch = self.parse_item()
        else_branch = None
        if self.match(TokenType.KEYWORD_ELSE):
            else_branch = self.parse_item()

        return IfNode(condition=cond, then_branch=then_branch, else_branch=else_branch, line=if_tok.line, column=if_tok.column)

    def parse_while(self) -> WhileNode:
        while_tok = self.previous()
        if not self.match(TokenType.LPAREN):
            self.error_at(self.peek(), "SYN002", "Expected '(' after 'while'.")
            raise ParseError()
        cond = self.parse_expression()
        if not self.match(TokenType.RPAREN):
            self.error_at(self.peek(), "SYN002", "Expected ')' closing while condition.")
            raise ParseError()

        body = self.parse_item()
        return WhileNode(condition=cond, body=body, line=while_tok.line, column=while_tok.column)

    def parse_function_call(self) -> FunctionCallNode:
        name_tok = self.advance()
        callee_name = name_tok.lexeme
        self.match(TokenType.LPAREN)
        args: List[ExpressionNode] = []

        if not self.check(TokenType.RPAREN):
            while True:
                args.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break

        if not self.match(TokenType.RPAREN):
            curr = self.peek()
            self.error_at(curr, "SYN002", f"Expected ')' closing arguments for '{callee_name}'.")
            raise ParseError()

        return FunctionCallNode(callee=callee_name, arguments=args, line=name_tok.line, column=name_tok.column)

    # -------------------------------------------------------------
    # Expression Parsing with Precedence:
    # logical or -> logical and -> equality -> relational -> additive -> multiplicative -> unary -> factor
    # -------------------------------------------------------------

    def parse_expression(self) -> ExpressionNode:
        return self.parse_logical_or()

    def parse_logical_or(self) -> ExpressionNode:
        expr = self.parse_logical_and()
        while self.match(TokenType.OP_LOGICAL_OR):
            op = self.previous().lexeme
            right = self.parse_logical_and()
            expr = BinaryOpNode(left=expr, operator=op, right=right, line=expr.line, column=expr.column)
        return expr

    def parse_logical_and(self) -> ExpressionNode:
        expr = self.parse_equality()
        while self.match(TokenType.OP_LOGICAL_AND):
            op = self.previous().lexeme
            right = self.parse_equality()
            expr = BinaryOpNode(left=expr, operator=op, right=right, line=expr.line, column=expr.column)
        return expr

    def parse_equality(self) -> ExpressionNode:
        expr = self.parse_relational()
        while self.match(TokenType.OP_EQ, TokenType.OP_NE):
            op = self.previous().lexeme
            right = self.parse_relational()
            expr = BinaryOpNode(left=expr, operator=op, right=right, line=expr.line, column=expr.column)
        return expr

    def parse_relational(self) -> ExpressionNode:
        expr = self.parse_additive()
        while self.match(TokenType.OP_LT, TokenType.OP_LE, TokenType.OP_GT, TokenType.OP_GE):
            op = self.previous().lexeme
            right = self.parse_additive()
            expr = BinaryOpNode(left=expr, operator=op, right=right, line=expr.line, column=expr.column)
        return expr

    def parse_additive(self) -> ExpressionNode:
        expr = self.parse_term()
        while self.match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            op_tok = self.previous()
            right = self.parse_term()
            expr = BinaryOpNode(left=expr, operator=op_tok.lexeme, right=right, line=op_tok.line, column=op_tok.column)
        return expr

    def parse_term(self) -> ExpressionNode:
        term = self.parse_factor()
        while self.match(TokenType.OP_MULTIPLY, TokenType.OP_DIVIDE, TokenType.OP_MOD):
            op_tok = self.previous()
            right = self.parse_factor()
            term = BinaryOpNode(left=term, operator=op_tok.lexeme, right=right, line=op_tok.line, column=op_tok.column)
        return term

    def parse_factor(self) -> ExpressionNode:
        # Unary operators: +, -, !
        if self.match(TokenType.OP_PLUS, TokenType.OP_MINUS, TokenType.OP_LOGICAL_NOT):
            op_tok = self.previous()
            operand = self.parse_factor()
            return UnaryOpNode(operator=op_tok.lexeme, operand=operand, line=op_tok.line, column=op_tok.column)

        # Numbers
        if self.match(TokenType.INT_LITERAL):
            tok = self.previous()
            return NumberLiteralNode(
                value=tok.value if tok.value is not None else int(tok.lexeme),
                raw=tok.lexeme,
                num_type="int",
                line=tok.line,
                column=tok.column
            )
        if self.match(TokenType.FLOAT_LITERAL):
            tok = self.previous()
            return NumberLiteralNode(
                value=tok.value if tok.value is not None else float(tok.lexeme),
                raw=tok.lexeme,
                num_type="float",
                line=tok.line,
                column=tok.column
            )

        # Strings & Chars
        if self.match(TokenType.STRING_LITERAL):
            tok = self.previous()
            return StringLiteralNode(value=tok.value or tok.lexeme, line=tok.line, column=tok.column)
        if self.match(TokenType.CHAR_LITERAL):
            tok = self.previous()
            return StringLiteralNode(value=tok.value or tok.lexeme, line=tok.line, column=tok.column)

        # Identifiers or function calls
        if self.check(TokenType.IDENTIFIER):
            if self.peek_next().token_type == TokenType.LPAREN:
                return self.parse_function_call()
            tok = self.advance()
            return VariableNode(name=tok.lexeme, line=tok.line, column=tok.column)

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
                    "Ensure parentheses are properly closed."
                )
                raise ParseError()
            return expr

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

    def consume_semicolon(self, message: str, suggestion: str = "") -> None:
        if self.check(TokenType.SEMICOLON):
            self.advance()
            return
        prev = self.previous()
        self.error_at(
            prev,
            "SYN001",
            f"Syntax error at line {prev.line}, column {prev.column + len(prev.lexeme)}: {message}",
            suggestion or "Add ';' at the end of statement."
        )

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
                TokenType.KEYWORD_INT, TokenType.KEYWORD_FLOAT, TokenType.KEYWORD_CHAR,
                TokenType.KEYWORD_DOUBLE, TokenType.KEYWORD_VOID, TokenType.KEYWORD_PRINT,
                TokenType.KEYWORD_IF, TokenType.KEYWORD_WHILE, TokenType.KEYWORD_RETURN,
                TokenType.RBRACE
            ):
                return
            self.advance()

