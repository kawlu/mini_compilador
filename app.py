from flask import Flask, render_template, request, jsonify
from src.compilador_api import compilar_para_web

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/compilar', methods=['POST'])
def compilar():
    data = request.get_json()
    codigo_fonte = data.get('codigo', '')

    if not codigo_fonte:
        return jsonify({
            'sucesso': False,
            'erro_geral': "Nenhum código fonte fornecido."
        }), 400

    try:
        resultados = compilar_para_web(codigo_fonte)
        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro_geral': f"Erro interno do servidor ao compilar: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
