## mini_lang — Gramática (EBNF)

A gramática abaixo descreve a linguagem suportada pelo analisador sintático atual (`sintatico.py`).

- **Operandos:** `ID`, `NUMERO`, expressões entre parênteses
- **Operadores unários:** `-` e `NOT`
- **Operadores binários (com precedência):**
  1. `*`, `/` (mais alta)
  2. `+`, `-`
  3. `<`, `<=`, `>`, `>=`
  4. `==`, `!=`
  5. `E` (`&&`)
  6. `OU` (`||`)
  7. `=` (atribuição) — associativa à direita

### Gramática (EBNF)
```ebnf
programa       ::= { comando } ;

comando        ::= atribuicao ";" ;

atribucao      ::= ID "=" atribuicao
                | expressao ;

expressao      ::= log_or ;

log_or         ::= log_and { ("OU" | "||") log_and } ;

log_and        ::= igualdade { ("E" | "&&") igualdade } ;

igualdade      ::= rel { ("==" | "!=") rel } ;

rel            ::= soma { ("<" | "<=" | ">" | ">=") soma } ;

soma           ::= termo { ("+" | "-") termo } ;

termo          ::= unario { ("*" | "/") unario } ;

unario         ::= ("-" | "NOT" | "!") unario
                | fator ;

fator          ::= ID
                | NUMERO
                | "(" expressao ")" ;
```

### Exemplos válidos
- `a = b + 3 * 2;`  &nbsp;&nbsp;→  `b 3 2 * + =` (pós-fixa esperada)
- `x = -a + NOT b;`
- `ok = (a < b) E (c == d);`

### Observações e mapeamento para o lexer
- Mapeie os símbolos para os nomes de token que o parser espera. Exemplo:
  - `+` -> `SOMA`, `-` -> `SUB`, `*` -> `MULT`, `/` -> `DIV`
  - `==` -> `IGUAL`, `!=` -> `DIF`
  - `&&` ou `E` -> `E`, `||` ou `OU` -> `OU`
  - `NOT` ou `!` -> `NOT`
  - `=` -> `ATRIBUICAO`, `;` -> `FIM`

### Precedência e associatividade (resumido)
| Nível | Operadores                          | Associatividade |
|-------|-------------------------------------|-----------------|
| 1     | `=`                                 | Direita         |
| 2     | `OU`, `||`                          | Esquerda        |
| 3     | `E`, `&&`                           | Esquerda        |
| 4     | `==`, `!=`                          | Esquerda        |
| 5     | `<`, `<=`, `>`, `>=`                | Esquerda        |
| 6     | `+`, `-`                            | Esquerda        |
| 7     | `*`, `/`                            | Esquerda        |
| 8     | `-` (unário), `NOT`, `!`           | (unário)        |