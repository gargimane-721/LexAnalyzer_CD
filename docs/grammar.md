# Grammar Specification (EBNF)

## 1. Overview
This document specifies the formal grammar for the **Smart Lexical Analyzer and Syntax Checker** educational compiler. The target source language is a deterministic subset of C-like syntax designed for clarity, rigorous precedence enforcement, and unambiguous parsing.

---

## 2. Lexical Terminals (Tokens)

```ebnf
LETTER          = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z" | "_" ;
DIGIT           = "0" | "1" | ... | "9" ;

IDENTIFIER      = LETTER , { LETTER | DIGIT } ;
INT_LITERAL     = DIGIT , { DIGIT } ;
FLOAT_LITERAL   = DIGIT , { DIGIT } , "." , DIGIT , { DIGIT } ;

KEYWORD_INT     = "int" ;
KEYWORD_FLOAT   = "float" ;
KEYWORD_PRINT   = "print" ;

OP_ASSIGN       = "=" ;
OP_PLUS         = "+" ;
OP_MINUS        = "-" ;
OP_MULTIPLY     = "*" ;
OP_DIVIDE       = "/" ;

SEMICOLON       = ";" ;
LPAREN          = "(" ;
RPAREN          = ")" ;

COMMENT         = "//" , { any_character_except_newline } ;
WHITESPACE      = " " | "\t" | "\r" | "\n" ;
```

---

## 3. Syntactic Grammar (EBNF)

```ebnf
program         = { statement } , EOF ;

statement       = declaration
                | assignment
                | print_statement ;

declaration     = TYPE , IDENTIFIER , OP_ASSIGN , expression , SEMICOLON ;

assignment      = IDENTIFIER , OP_ASSIGN , expression , SEMICOLON ;

print_statement = KEYWORD_PRINT , LPAREN , expression , RPAREN , SEMICOLON ;

expression      = term , { ( OP_PLUS | OP_MINUS ) , term } ;

term            = factor , { ( OP_MULTIPLY | OP_DIVIDE ) , factor } ;

factor          = NUMBER
                | IDENTIFIER
                | LPAREN , expression , RPAREN
                | unary_expression ;

unary_expression = ( OP_PLUS | OP_MINUS ) , factor ;

TYPE            = KEYWORD_INT | KEYWORD_FLOAT ;

NUMBER          = INT_LITERAL | FLOAT_LITERAL ;
```

---

## 4. Operator Precedence and Associativity Table

| Precedence Level | Category | Operator | Associativity | Description |
| :---: | :---: | :---: | :---: | :--- |
| **1 (Highest)** | Primary & Grouping | `( )` | N/A | Sub-expressions enclosed in parentheses |
| **2** | Unary | `+`, `-` | Right-to-Left | Unary sign negation or affirmation |
| **3** | Multiplicative | `*`, `/` | Left-to-Right | Multiplication and Floating/Integer division |
| **4** | Additive | `+`, `-` | Left-to-Right | Addition and Subtraction |
| **5 (Lowest)** | Assignment | `=` | Right-to-Left | Variable assignment in declarations / statements |

---

## 5. Disambiguation Rules
1. **Keyword Priority:** The tokenizer prioritizes reserved keywords (`int`, `float`, `print`) over general identifiers. For instance, `int` matches `KEYWORD_INT`, whereas `integerValue` matches `IDENTIFIER`.
2. **Left-Factoring & Elimination of Left-Recursion:** The expression grammar uses iteration (`term { ("+" | "-") term }`) rather than direct left-recursion (`expression -> expression + term`), allowing straightforward deterministic recursive-descent parsing with lookahead $k=1$.
3. **Semicolon Termination:** Every statement must explicitly terminate with a semicolon (`;`).

