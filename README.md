# Mini Compilador Web

Este é um projeto de compilador completo desenvolvido em Python com uma interface web moderna construída em Flask, JavaScript e D3.js.

O compilador processa uma linguagem personalizada (com sintaxe em português), realiza todas as etapas de compilação (Léxica, Sintática e Semântica) e oferece visualização gráfica da Árvore Sintática Abstrata (AST), além de gerar código executável em Python.

## Funcionalidades

Análise Léxica: Identificação de tokens, palavras reservadas e operadores.
Análise Sintática: Construção da árvore de análise (AST) com suporte a precedência matemática.
Análise Semântica:
Verificação de tipos (Int vs Float).
Verificação de declaração de variáveis.
Bounds Check: Proteção contra acesso a índices inválidos em arrays.
Curto-Circuito: Otimização lógica nos operadores e / ou.
Visualização AST: Gráfico interativo (Zoom/Pan) gerado com D3.js.
Tabela de Símbolos: Visualização dos valores e tipos das variáveis em tempo de execução.
Transpilação: Tradução automática do código fonte para Python.
Interface Web: Editor de código com numeração de linhas, upload de arquivos e Dark Mode.

## Tecnologias Utilizadas:

Backend: Python 3, Flask.
Frontend: HTML5, CSS3 (Tailwind), JavaScript.
Visualização: D3.js (Data-Driven Documents).
Ícones: Lucide Icons.

## Pré-requisitos:

Você precisa ter o Python 3.x instalado em sua máquina.

## Instalação e Execução:

Clone o repositório (ou baixe os arquivos): Certifique-se de que a estrutura de pastas esteja correta (src/, static/, templates/, app.py).

## Dependências:

O projeto requer apenas o Flask.
use pip install flask

## Como Executar:

Na pasta raiz do projeto, rode:
python app.py
Acesse no navegador: Abra o link que aparecerá no terminal (geralmente http://127.0.0.1:5000).
