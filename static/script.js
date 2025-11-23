let codigoEntrada = "";
let carregando = false;
let abaSelecionada = 'saida';
let dadosSaida = {
    ast: null,
    simbolos: null,
    saida: "Execute uma ação para ver os resultados",
    codigoPython: null
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
const botoesAcao = ['btnAST', 'btnSimbolos', 'btnExecutar', 'btnGerarPython'];

function inicializarTema() {
    const temaSalvo = localStorage.getItem('tema');
    const prefereEscuro = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (temaSalvo === 'dark' || (!temaSalvo && prefereEscuro)) {
        htmlElemento.classList.add('dark');
        iconeTema.setAttribute('data-lucide', 'sun');
    } else {
        htmlElemento.classList.remove('dark');
        iconeTema.setAttribute('data-lucide', 'moon');
    }
    lucide.createIcons(); 
}

function alternarTema() {
    if (htmlElemento.classList.contains('dark')) {
        htmlElemento.classList.remove('dark');
        localStorage.setItem('tema', 'light');
        iconeTema.setAttribute('data-lucide', 'moon');
    } else {
        htmlElemento.classList.add('dark');
        localStorage.setItem('tema', 'dark');
        iconeTema.setAttribute('data-lucide', 'sun');
    }
    lucide.createIcons();
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
        lucide.createIcons();

        alertaTimeout = setTimeout(() => {
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
    
    botoesAcao.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = carregando || codigoVazio;
            btn.style.opacity = (carregando || codigoVazio) ? 0.6 : 1;
        }
    });

    document.getElementById('btnLerArquivo').disabled = carregando;
}

function atualizarPainelSaida() {
    let conteudo;
    switch (abaSelecionada) {
        case 'ast':
            conteudo = dadosSaida.ast || "Nenhum AST gerado. Execute 'Mostrar AST'.";
            break;
        case 'simbolos':
            conteudo = dadosSaida.simbolos || "Nenhuma tabela de símbolos gerada. Execute 'Mostrar Símbolos'.";
            break;
        case 'python':
            conteudo = dadosSaida.codigoPython || "Nenhum código Python gerado. Execute 'Gerar Python'.";
            break;
        case 'saida':
        default:
            conteudo = dadosSaida.saida || "Execute uma ação para ver os resultados";
            break;
    }
    saidaConteudoElemento.textContent = conteudo;
}

function selecionarAba(novaAba) {
    abaSelecionada = novaAba;

    document.querySelectorAll('.aba-botao').forEach(btn => {
        btn.classList.remove('aba-ativa');
        if (btn.getAttribute('data-aba') === novaAba) {
            btn.classList.add('aba-ativa');
        }
    });

    atualizarPainelSaida();
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
    const arquivo = evento.target.files?.[0];
    if (!arquivo) return;

    definirAlerta(null);
    definirCarregando(true);

    try {
        const conteudo = await arquivo.text();
        areaCodigoElemento.value = conteudo;
        observarMudancaCodigo();
        definirAlerta(`Arquivo '${arquivo.name}' carregado com sucesso.`, 'sucesso');
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
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ codigo: codigo })
    });
    
    const dados = await resposta.json();
    
    if (resposta.ok) {
        return dados; 
    } else {
        throw new Error(dados.erro_geral || `Erro HTTP ${resposta.status}: Falha no servidor.`);
    }
}

async function executarCompilacaoGeral() {
    if (!codigoEntrada.trim()) {
        definirErro("Código vazio! Cole ou carregue um arquivo.");
        return;
    }

    definirCarregando(true);
    definirAlerta(null);
    dadosSaida = { ast: null, simbolos: null, saida: "Iniciando compilação (aguarde)...", codigoPython: null };
    atualizarPainelSaida();

    try {
        const resultados = await chamarAPICompilacao(codigoEntrada);
        
        dadosSaida.ast = resultados.ast;
        dadosSaida.simbolos = resultados.tabela_simbolos;
        dadosSaida.codigoPython = resultados.traducao_posfixa;
        
        const todosErros = [
            ...resultados.erros_lexicos.map(e => `[LEXICO]: ${e}`),
            ...resultados.erros_sintaticos.map(e => `[SINTATICO]: ${e}`),
            ...resultados.erros_semanticos.map(e => `[SEMANTICO]: ${e}`)
        ].join('\n');
        
        if (resultados.sucesso) {
            definirAlerta("Compilação concluída com sucesso!", 'sucesso');
            dadosSaida.saida = resultados.tokens + "\n" + resultados.traducao_posfixa;
        } else {
            definirAlerta("Erros encontrados durante a compilação.", 'erro');
            dadosSaida.saida = resultados.tokens + "\n\n" + "--- ERROS FINAIS ---\n" + todosErros;
        }

    } catch (erro) {
        console.error("Falha na comunicação ou erro inesperado:", erro);
        definirErro(`Falha na comunicação: ${erro.message}`);
        dadosSaida.saida = `FALHA DE COMUNICAÇÃO/SERVIDOR:\n${erro.message}`;

    } finally {
        atualizarPainelSaida();
        definirCarregando(false);
    }
}

function limparSaida() {
    dadosSaida = {
        ast: null,
        simbolos: null,
        saida: "Saída limpa. Execute uma nova compilação.",
        codigoPython: null
    };

    atualizarPainelSaida();
    selecionarAba('saida');
    definirAlerta("Painel de Saída limpo.", 'sucesso', 2000);
}

function executar() {
    executarCompilacaoGeral().then(() => selecionarAba('saida'));
}

function exibirAST() {
    executarCompilacaoGeral().then(() => selecionarAba('ast'));
}

function exibirSimbolos() {
    executarCompilacaoGeral().then(() => selecionarAba('simbolos'));
}

function gerarPython() {
    executarCompilacaoGeral().then(() => selecionarAba('python'));
}

btnAlternarTema.addEventListener('click', alternarTema);
areaCodigoElemento.addEventListener('input', observarMudancaCodigo);

window.onload = function() {
    inicializarTema();
    observarMudancaCodigo(); 
    atualizarPainelSaida();
};
