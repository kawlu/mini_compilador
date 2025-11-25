let codigoEntrada = "";
let carregando = false;
let abaSelecionada = 'saida';

// Variável de estado para alternar entre gráfico e texto
let astModoVisual = true; 

let dadosSaida = {
    ast: null,
    astJson: null, // JSON para o gráfico D3
    simbolos: null,
    saida: "Execute uma ação para ver os resultados",
    codigoPython: null
};

// Cores para o Gráfico D3
const COLORS = {
    op: "#c678dd",
    pow: "#d19a66",
    number: "#d19a66",
    id: "#61afef",
    if: "#e06c75",
    loop: "#e5c07b",
    block: "#56b6c2",
    default: "#abb2bf"
};

const htmlElemento = document.documentElement;
const btnAlternarTema = document.getElementById('alternarTemaBtn');
const iconeTema = document.getElementById('iconeTema');
const areaCodigoElemento = document.getElementById('areaCodigo');

const alertaGeralElemento = document.getElementById('alertaGeral');
const descricaoAlertaElemento = document.getElementById('descricaoAlerta');
const iconeAlertaElemento = document.getElementById('iconeAlerta');
let alertaTimeout; 

const entradaArquivoElemento = document.getElementById('entradaArquivo');
const saidaConteudoElemento = document.getElementById('saidaConteudo');
const areaGraficaElemento = document.getElementById('areaGrafica'); // Área do D3

const botoesAcao = ['btnAST', 'btnSimbolos', 'btnExecutar', 'btnGerarPython'];

// --- NOVA FUNÇÃO CIRÚRGICA: Converte códigos ANSI para HTML ---
function converterAnsiParaHtml(texto) {
    if (!texto) return "";
    // Substitui código de cor Vermelha (\033[31m) por span vermelho
    let html = texto.replace(/\u001b\[31m/g, '<span style="color: #ef4444; font-weight: bold;">');
    // Substitui o Reset (\033[0m) pelo fechamento do span
    html = html.replace(/\u001b\[0m/g, '</span>');
    return html;
}
// --------------------------------------------------------------

function inicializarTema() {
    const temaSalvo = localStorage.getItem('tema');
    const prefereEscuro = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Limpa ícone anterior
    if (iconeTema) iconeTema.innerHTML = "";

    if (temaSalvo === 'dark' || (!temaSalvo && prefereEscuro)) {
        htmlElemento.classList.add('dark');
        iconeTema.setAttribute('data-lucide', 'sun');
    } else {
        htmlElemento.classList.remove('dark');
        iconeTema.setAttribute('data-lucide', 'moon');
    }
    if (window.lucide) lucide.createIcons(); 
}

function alternarTema() {
    if (iconeTema) iconeTema.innerHTML = "";

    if (htmlElemento.classList.contains('dark')) {
        htmlElemento.classList.remove('dark');
        localStorage.setItem('tema', 'light');
        iconeTema.setAttribute('data-lucide', 'moon');
    } else {
        htmlElemento.classList.add('dark');
        localStorage.setItem('tema', 'dark');
        iconeTema.setAttribute('data-lucide', 'sun');
    }
    if (window.lucide) lucide.createIcons();
}

function definirAlerta(mensagem, tipo = 'erro', duracao = 5000) {
    if (alertaTimeout) {
        clearTimeout(alertaTimeout);
    }
    alertaGeralElemento.classList.add('hidden');
    alertaGeralElemento.classList.remove('alerta-erro', 'alerta-sucesso');
    
    if (mensagem) {
        descricaoAlertaElemento.textContent = mensagem;

        if (tipo === 'sucesso') {
            alertaGeralElemento.classList.add('alerta-sucesso');
            iconeAlertaElemento.setAttribute('data-lucide', 'check-circle');
        } else {
            alertaGeralElemento.classList.add('alerta-erro');
            iconeAlertaElemento.setAttribute('data-lucide', 'alert-circle');
        }
        
        alertaGeralElemento.classList.remove('hidden');
        if (window.lucide) lucide.createIcons();

        alertaTimeout = setTimeout(function() {
            alertaGeralElemento.classList.add('hidden');
        }, duracao);
    }
}

function definirErro(mensagem) {
     definirAlerta(mensagem, 'erro');
}

function definirCarregando(status) {
    carregando = status;
    const codigoVazio = !codigoEntrada.trim();
    
    botoesAcao.forEach(function(id) {
        const btn = document.getElementById(id);
        if (btn) {
            if (carregando || codigoVazio) {
                btn.disabled = true;
                btn.style.opacity = 0.6;
            } else {
                btn.disabled = false;
                btn.style.opacity = 1;
            }
        }
    });

    const btnLer = document.getElementById('btnLerArquivo');
    if (btnLer) {
        btnLer.disabled = carregando;
    }
}

function alternarVisualizacaoAST() {
    if (astModoVisual) {
        astModoVisual = false;
    } else {
        astModoVisual = true;
    }
    atualizarPainelSaida();
}

function atualizarPainelSaida() {
    // Reset visual padrão
    saidaConteudoElemento.style.display = 'block';
    areaGraficaElemento.style.display = 'none';
    areaGraficaElemento.innerHTML = '';

    const btnToggle = document.getElementById('btnAlternarAST');
    if (btnToggle) {
        btnToggle.classList.add('hidden');
    }

    let conteudo;

    switch (abaSelecionada) {
        case 'ast':
            if (btnToggle) {
                btnToggle.classList.remove('hidden');
                const spanTexto = document.getElementById('textoToggleAST');
                if (spanTexto) {
                    if (astModoVisual) {
                        spanTexto.textContent = "Ver Texto";
                    } else {
                        spanTexto.textContent = "Ver Gráfico";
                    }
                }
            }

            if (astModoVisual && dadosSaida.astJson) {
                saidaConteudoElemento.style.display = 'none';
                areaGraficaElemento.style.display = 'block';
                desenharArvoreD3(dadosSaida.astJson);
                return;
            } else {
                conteudo = dadosSaida.ast;
                if (!conteudo) conteudo = "Nenhum AST gerado. Execute 'Mostrar AST'.";
            }
            break;

        case 'simbolos':
            conteudo = dadosSaida.simbolos;
            if (!conteudo) conteudo = "Nenhuma tabela de símbolos gerada. Execute 'Mostrar Símbolos'.";
            break;

        case 'python':
            conteudo = dadosSaida.codigoPython;
            if (!conteudo) conteudo = "Nenhum código Python gerado. Execute 'Gerar Python'.";
            break;

        case 'saida':
        default:
            conteudo = dadosSaida.saida;
            if (!conteudo) conteudo = "Execute uma ação para ver os resultados";
            break;
    }

    // --- ALTERAÇÃO CIRÚRGICA AQUI ---
    // Usamos innerHTML + função de conversão para colorir o erro
    saidaConteudoElemento.innerHTML = converterAnsiParaHtml(conteudo);
}

function selecionarAba(novaAba) {
    abaSelecionada = novaAba;

    const botoes = document.querySelectorAll('.aba-botao');
    for (let i = 0; i < botoes.length; i++) {
        const btn = botoes[i];
        btn.classList.remove('aba-ativa');
        if (btn.getAttribute('data-aba') === novaAba) {
            btn.classList.add('aba-ativa');
        }
    }

    atualizarPainelSaida();
}

// --- Função D3.js (Mantida) ---
function desenharArvoreD3(data) {
    if (!data) return;

    const width = areaGraficaElemento.clientWidth || 800;
    const height = areaGraficaElemento.clientHeight || 600;

    const svg = d3.select("#areaGrafica").append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .call(d3.zoom().scaleExtent([0.1, 3]).on("zoom", function(event) {
            g.attr("transform", event.transform);
        }));

    const g = svg.append("g")
        .attr("transform", "translate(" + (width / 2) + ", 50)");

    const root = d3.hierarchy(data);
    const treeLayout = d3.tree().nodeSize([70, 90]);
    treeLayout(root);

    g.selectAll(".link")
        .data(root.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("d", d3.linkVertical()
            .x(function(d) { return d.x; })
            .y(function(d) { return d.y; }))
        .attr("fill", "none")
        .attr("stroke", "#9ca3af")
        .attr("stroke-width", 2);

    const node = g.selectAll(".node")
        .data(root.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { 
            return "translate(" + d.x + "," + d.y + ")"; 
        });

    node.append("circle")
        .attr("r", 20)
        .attr("fill", function(d) { return COLORS[d.data.type] || COLORS.default; })
        .attr("stroke", "#333")
        .attr("stroke-width", 2)
        .on("mouseover", function() { d3.select(this).attr("stroke", "#fff").attr("stroke-width", 3); })
        .on("mouseout", function() { d3.select(this).attr("stroke", "#333").attr("stroke-width", 2); });

    node.append("text")
        .attr("dy", 5)
        .attr("text-anchor", "middle")
        .text(function(d) { 
            if (d.data.name.length > 7) return d.data.name.substring(0, 5) + "..";
            return d.data.name;
        })
        .style("fill", "white")
        .style("font-family", "monospace")
        .style("font-size", "10px")
        .style("pointer-events", "none");
        
    node.append("title").text(function(d) { return d.data.name; });
}

function observarMudancaCodigo() {
    codigoEntrada = areaCodigoElemento.value;
    definirCarregando(false); 
}

function acionarLeituraBotao() {
    if (!carregando) {
        entradaArquivoElemento.click();
    }
}

async function processarUploadArquivo(evento) {
    const arquivo = evento.target.files ? evento.target.files[0] : null;
    if (!arquivo) return;

    definirAlerta(null);
    definirCarregando(true);

    try {
        const conteudo = await arquivo.text();
        areaCodigoElemento.value = conteudo;
        observarMudancaCodigo();
        definirAlerta("Arquivo '" + arquivo.name + "' carregado com sucesso.", 'sucesso');
    } catch (err) {
        definirErro("Erro ao ler arquivo: " + (err.message || "Desconhecido"));
    } finally {
        evento.target.value = null; 
        definirCarregando(false);
    }
}

async function chamarAPICompilacao(codigo) {
    const url = '/api/compilar';
    const resposta = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo: codigo })
    });
    
    const dados = await resposta.json();
    if (resposta.ok) {
        return dados; 
    } else {
        throw new Error(dados.erro_geral || "Erro HTTP " + resposta.status + ": Falha no servidor.");
    }
}

async function executarCompilacaoGeral() {
    if (!codigoEntrada.trim()) {
        definirErro("Código vazio! Cole ou carregue um arquivo.");
        return;
    }

    definirCarregando(true);
    definirAlerta(null);
    
    dadosSaida = { ast: null, astJson: null, simbolos: null, saida: "Iniciando compilação (aguarde)...", codigoPython: null };
    atualizarPainelSaida();

    try {
        const resultados = await chamarAPICompilacao(codigoEntrada);
        
        dadosSaida.ast = resultados.ast;
        dadosSaida.astJson = resultados.ast_json;
        dadosSaida.simbolos = resultados.tabela_simbolos;
        dadosSaida.codigoPython = resultados.codigo_python;
        
        let listaErros = "";
        if (resultados.erros_lexicos.length > 0) {
            listaErros += resultados.erros_lexicos.map(function(e) { return "[LEXICO]: " + e; }).join('\n') + "\n";
        }
        if (resultados.erros_sintaticos.length > 0) {
            listaErros += resultados.erros_sintaticos.map(function(e) { return "[SINTATICO]: " + e; }).join('\n') + "\n";
        }
        if (resultados.erros_semanticos.length > 0) {
            listaErros += resultados.erros_semanticos.map(function(e) { return "[SEMANTICO]: " + e; }).join('\n');
        }
        
        if (resultados.sucesso) {
            definirAlerta("Compilação concluída com sucesso!", 'sucesso');
            dadosSaida.saida = resultados.tokens + "\n\n--- TRADUÇÃO PÓS-FIXA ---\n" + resultados.traducao_posfixa;
        } else {
            definirAlerta("Erros encontrados durante a compilação.", 'erro');
            dadosSaida.saida = resultados.tokens + "\n\n" + "--- ERROS FINAIS ---\n" + listaErros;
        }

    } catch (erro) {
        console.error("Falha na comunicação ou erro inesperado:", erro);
        definirErro("Falha na comunicação: " + erro.message);
        dadosSaida.saida = "FALHA DE COMUNICAÇÃO/SERVIDOR:\n" + erro.message;

    } finally {
        atualizarPainelSaida();
        definirCarregando(false);
    }
}

function limparSaida() {
    dadosSaida = { ast: null, astJson: null, simbolos: null, saida: "Saída limpa. Execute uma nova compilação.", codigoPython: null };
    areaGraficaElemento.innerHTML = '';
    atualizarPainelSaida();
    selecionarAba('saida');
    definirAlerta("Painel de Saída limpo.", 'sucesso', 2000);
}

function executar() {
    executarCompilacaoGeral().then(function() { selecionarAba('saida'); });
}

function exibirAST() {
    executarCompilacaoGeral().then(function() { selecionarAba('ast'); });
}

function exibirSimbolos() {
    executarCompilacaoGeral().then(function() { selecionarAba('simbolos'); });
}

function gerarPython() {
    executarCompilacaoGeral().then(function() { selecionarAba('python'); });
}

btnAlternarTema.addEventListener('click', alternarTema);
areaCodigoElemento.addEventListener('input', observarMudancaCodigo);

window.onload = function() {
    inicializarTema();
    observarMudancaCodigo(); 
    atualizarPainelSaida();
};