from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Cargar datos del CSV
try:
    df = pd.read_csv('datos_ensenada.csv')
except:
    # CSV de ejemplo si no existe el archivo
    df = pd.DataFrame({
        'id': range(100),
        'nombre': [f'Negocio {i}' for i in range(100)],
        'ventas': range(100, 200)
    })

# Simular tus módulos si no existen
try:
    import filtrar_datos
except ImportError:
    # Módulo simulado
    class filtrar_datos:
        @staticmethod
        def filtrar(df, columna, valor, operador):
            if operador == 'igual':
                return df[df[columna] == valor].to_dict('records')
            return df.head(10).to_dict('records')

try:
    import investigador
except ImportError:
    # Módulo simulado
    class investigador:
        @staticmethod
        def analizar(df, tipo_analisis):
            return f"Análisis {tipo_analisis} completado"

@app.route('/')
def home():
    return jsonify({
        "mensaje": "API Flask desplegada en Vercel",
        "rutas_available": [
            "/excel/negocio/datos",
            "/excel/negocio/datos/<id>",
            "/excel/negocio/filtrar",
            "/excel/negocio/analizar",
            "/excel/negocio/estadisticas"
        ]
    })

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
            "tipos_datos": df.dtypes.astype(str).to_dict(),
            "registros_nulos": df.isnull().sum().to_dict()
        }
        return jsonify({"estadisticas": stats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handler para Vercel
def handler(request):
    from flask import Response
    import json
    
    with app.app_context():
        path = request.path
        method = request.method
        
        # Simular el routing de Flask para Vercel
        if path == '/' and method == 'GET':
            return Response(json.dumps(home()), mimetype='application/json')
        elif path.startswith('/excel/negocio/datos') and method == 'GET':
            if '/' in path.split('/excel/negocio/datos/')[-1]:
                id_str = path.split('/')[-1]
                if id_str.isdigit():
                    return obtener_dato_especifico(int(id_str))
            return obtener_datos()
        elif path.startswith('/excel/negocio/filtrar') and method == 'GET':
            return filtrar_datos_ia()
        elif path.startswith('/excel/negocio/analizar') and method == 'GET':
            return analizar_datos()
        elif path.startswith('/excel/negocio/estadisticas') and method == 'GET':
            return obtener_estadisticas()
        else:
            return Response(json.dumps({"error": "Ruta no encontrada"}), status=404, mimetype='application/json')
