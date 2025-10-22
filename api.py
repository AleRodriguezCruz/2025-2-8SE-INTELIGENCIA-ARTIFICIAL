from flask import Flask, request, jsonify
import pandas as pd
import filtrar_datos  # Tu módulo de IA
import investigador   # Tu módulo de análisis

app = Flask(__name__)

# Cargar datos del CSV
df = pd.read_csv('datos_ensenada.csv')

@app.route('/excel/negocio/datos', methods=['GET'])
def obtener_datos():
    try:
        limite = request.args.get('limite', default=100, type=int)
        datos = df.head(limite).to_dict('records')
        return jsonify({"datos": datos, "total": len(datos)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/excel/negocio/datos/<int:id>', methods=['GET'])
def obtener_dato_especifico(id):
    try:
        if id >= len(df) or id < 0:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        registro = df.iloc[id].to_dict()
        return jsonify({"registro": registro}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/excel/negocio/datos/<int:id>', methods=['PUT'])
def actualizar_dato(id):
    try:
        if id >= len(df) or id < 0:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        datos_actualizados = request.get_json()
        # Aquí iría la lógica para actualizar el DataFrame
        return jsonify({"mensaje": "Registro actualizado", "id": id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/excel/negocio/filtrar', methods=['GET'])
def filtrar_datos_ia():
    try:
        columna = request.args.get('columna', type=str)
        valor = request.args.get('valor', type=str)
        operador = request.args.get('operador', default='igual', type=str)
        
        # Usar tu módulo de IA para filtrar
        resultado = filtrar_datos.filtrar(df, columna, valor, operador)
        return jsonify({"datos_filtrados": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/excel/negocio/analizar', methods=['GET'])
def analizar_datos():
    try:
        tipo_analisis = request.args.get('tipo_analisis', type=str)
        
        # Usar tu módulo de investigador.py para análisis IA
        resultado = investigador.analizar(df, tipo_analisis)
        return jsonify({"analisis": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/excel/negocio/estadisticas', methods=['GET'])
def obtener_estadisticas():
    try:
        stats = {
            "total_registros": len(df),
            "columnas": list(df.columns),
            "tipos_datos": df.dtypes.to_dict(),
            "registros_nulos": df.isnull().sum().to_dict()
        }
        return jsonify({"estadisticas": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
