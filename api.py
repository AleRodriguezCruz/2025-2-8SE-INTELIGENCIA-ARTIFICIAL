# api.py - VERSIÓN CON IA REAL QUE ANALIZA DATOS
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
import numpy as np
from typing import List, Dict

app = FastAPI(
    title="Emprende IA API",
    description="API para encontrar oportunidades de negocio por sinergia en Ensenada.",
    version="3.0 - IA REAL"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zonas conocidas
ZONAS_CONOCIDAS = {
    "maneadero": (31.7167, -116.5667, 3), 
    "centro": (31.8650, -116.6217, 2),
    "chapultepec": (31.8386, -116.6014, 2), 
    "sauzal": (31.8833, -116.6833, 2.5),
    "valle dorado": (31.8489, -116.5858, 2)
}

# --- REGLAS DE SINERGIA DE LA IA ---
SINERGIAS_IA = {
    "educacion": {
        "anclas": ["escuela", "colegio", "instituto", "universidad", "preparatoria", "cbtis", "conalep", "secundaria", "primaria"],
        "oportunidades": ["papeleria", "copias", "utiles escolares", "libretas", "lapices", "cyber", "internet"],
        "nombre_oportunidad": "Papelería / Tienda de útiles"
    },
    "salud": {
        "anclas": ["hospital", "clinica", "consultorio", "imss", "issste", "centro de salud", "medico", "doctor"],
        "oportunidades": ["farmacia", "drogueria", "botica", "medicina", "farmaceutico"],
        "nombre_oportunidad": "Farmacia"
    },
    "deporte": {
        "anclas": ["gym", "gimnasio", "deportivo", "fitness", "crossfit", "ejercicio"],
        "oportunidades": ["suplementos", "proteina", "vitaminas", "nutricion", "deportiva", "tenis", "zapatos deportivos"],
        "nombre_oportunidad": "Tienda de suplementos / Nutrición"
    }
}

def load_data():
    """Carga y limpia los datos reales del CSV"""
    try:
        df = pd.read_csv('datos_ensenada.csv', encoding='latin1')
        
        # Limpiar y convertir datos
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df['categoria_negocio'] = df['categoria_negocio'].astype(str).str.lower()
        
        # Eliminar filas con datos faltantes
        df.dropna(subset=['latitud', 'longitud', 'categoria_negocio'], inplace=True)
        
        print(f"✅ Datos cargados correctamente. {len(df)} negocios registrados.")
        print(f"📊 Categorías únicas: {df['categoria_negocio'].nunique()}")
        
        return df
    except FileNotFoundError:
        print("❌ ERROR: No se encontró 'datos_ensenada.csv'")
        return None
    except Exception as e:
        print(f"❌ ERROR cargando datos: {e}")
        return None

def filtrar_por_zona(df, zona_info, radio_km):
    """Filtra negocios dentro de una zona y radio específicos"""
    lat_zona, lon_zona, _ = zona_info
    radio_grados = radio_km / 111.0  # Aproximación de km a grados
    
    lat_min, lat_max = lat_zona - radio_grados, lat_zona + radio_grados
    lon_min, lon_max = lon_zona - radio_grados, lon_zona + radio_grados
    
    df_zona = df[
        (df['latitud'].between(lat_min, lat_max)) & 
        (df['longitud'].between(lon_min, lon_max))
    ]
    
    return df_zona

def buscar_cerca(df, lat_centro, lon_centro, radio_km):
    """Busca negocios cerca de un punto específico"""
    radio_grados = radio_km / 111.0
    
    lat_min, lat_max = lat_centro - radio_grados, lat_centro + radio_grados
    lon_min, lon_max = lon_centro - radio_grados, lon_centro + radio_grados
    
    return df[
        (df['latitud'].between(lat_min, lat_max)) & 
        (df['longitud'].between(lon_min, lon_max))
    ]

def analizar_sinergias_ia(df_zona):
    """IA REAL que analiza sinergias en los datos"""
    oportunidades_encontradas = []
    
    print(f"🔍 IA analizando {len(df_zona)} negocios en la zona...")
    
    for categoria, reglas in SINERGIAS_IA.items():
        print(f"  - Buscando sinergias para: {categoria}")
        
        # Buscar negocios ancla
        anclas_encontradas = []
        for palabra_clave in reglas["anclas"]:
            anclas = df_zona[df_zona['categoria_negocio'].str.contains(palabra_clave, na=False)]
            anclas_encontradas.extend(anclas.to_dict('records'))
        
        print(f"    ✅ Encontradas {len(anclas_encontradas)} anclas de {categoria}")
        
        # Para cada ancla, buscar oportunidades faltantes
        for ancla in anclas_encontradas:
            # Buscar negocios cercanos al ancla (500 metros)
            negocios_cercanos = buscar_cerca(df_zona, ancla['latitud'], ancla['longitud'], 0.5)
            
            # Verificar si ya existe la oportunidad cerca
            oportunidad_existe = False
            for palabra_oportunidad in reglas["oportunidades"]:
                if any(negocios_cercanos['categoria_negocio'].str.contains(palabra_oportunidad, na=False)):
                    oportunidad_existe = True
                    break
            
            # Si NO existe la oportunidad, la agregamos
            if not oportunidad_existe:
                oportunidades_encontradas.append({
                    "categoria_sinergia": categoria,
                    "oportunidad": reglas["nombre_oportunidad"],
                    "ancla": ancla['categoria_negocio'].title(),
                    "ancla_direccion": ancla.get('direccion', 'Dirección no disponible'),
                    "ancla_lat": ancla['latitud'],
                    "ancla_lon": ancla['longitud'],
                    "confianza": "alta",
                    "radio_analizado": 0.5
                })
    
    print(f"🎯 IA encontró {len(oportunidades_encontradas)} oportunidades")
    return oportunidades_encontradas

# Cargar datos al iniciar
df_completo = load_data()

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Emprende IA con IA REAL", 
        "version": "3.0 - Análisis de datos reales",
        "datos_cargados": df_completo is not None,
        "total_negocios": len(df_completo) if df_completo is not None else 0
    }

@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba"""
    if df_completo is None:
        return {
            "status": "error", 
            "message": "❌ No hay datos cargados",
            "datos_cargados": False
        }
    
    return {
        "status": "success", 
        "message": "✅ API con IA REAL funcionando",
        "datos_cargados": True,
        "total_negocios": len(df_completo),
        "categorias_unicas": df_completo['categoria_negocio'].nunique(),
        "zonas_disponibles": list(ZONAS_CONOCIDAS.keys())
    }

@app.get("/estadisticas")
async def obtener_estadisticas():
    """Estadísticas reales de los datos"""
    if df_completo is None:
        raise HTTPException(status_code=500, detail="No hay datos cargados")
    
    stats = {
        "total_negocios": len(df_completo),
        "categorias_unicas": int(df_completo['categoria_negocio'].nunique()),
        "cobertura_geografica": {
            "lat_min": float(df_completo['latitud'].min()),
            "lat_max": float(df_completo['latitud'].max()),
            "lon_min": float(df_completo['longitud'].min()),
            "lon_max": float(df_completo['longitud'].max())
        },
        "categorias_mas_comunes": df_completo['categoria_negocio'].value_counts().head(10).to_dict()
    }
    
    return stats

@app.get("/oportunidades/{zona}")
async def obtener_oportunidades(zona: str, radio_km: float = 2.0):
    """
    IA REAL que analiza oportunidades basadas en datos reales del CSV
    """
    # Verificar si la zona existe
    zona_lower = zona.lower()
    if zona_lower not in ZONAS_CONOCIDAS:
        raise HTTPException(
            status_code=404, 
            detail=f"Zona '{zona}' no encontrada. Zonas disponibles: {list(ZONAS_CONOCIDAS.keys())}"
        )
    
    # Verificar que hay datos
    if df_completo is None:
        raise HTTPException(
            status_code=500, 
            detail="No se pudieron cargar los datos. Verifica que 'datos_ensenada.csv' exista."
        )
    
    print(f"🎯 IA analizando zona: {zona_lower} (radio: {radio_km}km)")
    
    # Filtrar negocios en la zona
    zona_info = ZONAS_CONOCIDAS[zona_lower]
    df_zona = filtrar_por_zona(df_completo, zona_info, radio_km)
    
    print(f"📊 Negocios en {zona_lower}: {len(df_zona)}")
    
    # Ejecutar IA de análisis de sinergias
    oportunidades = analizar_sinergias_ia(df_zona)
    
    # Devolver resultados del análisis real
    return {
        "zona": zona_lower,
        "radio_analizado_km": radio_km,
        "total_negocios_zona": len(df_zona),
        "total_oportunidades": len(oportunidades),
        "oportunidades": oportunidades,
        "nota": "✅ Análisis realizado con IA REAL sobre datos del CSV",
        "estadisticas_analisis": {
            "categorias_analizadas": list(SINERGIAS_IA.keys()),
            "radio_busqueda_anclas": "0.5 km",
            "metodologia": "Búsqueda de sinergias por proximidad geográfica"
        }
    }

@app.get("/debug/zona/{zona}")
async def debug_zona(zona: str):
    """Endpoint para debug: muestra qué negocios hay en una zona"""
    if df_completo is None:
        raise HTTPException(status_code=500, detail="No hay datos cargados")
    
    zona_lower = zona.lower()
    if zona_lower not in ZONAS_CONOCIDAS:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    zona_info = ZONAS_CONOCIDAS[zona_lower]
    df_zona = filtrar_por_zona(df_completo, zona_info, 2.0)
    
    return {
        "zona": zona_lower,
        "total_negocios": len(df_zona),
        "negocios": df_zona[['categoria_negocio', 'latitud', 'longitud']].head(20).to_dict('records'),
        "categorias_unicas": df_zona['categoria_negocio'].unique().tolist()
    }

if __name__ == "__main__":
    print("🚀 Iniciando API de Emprende IA con IA REAL...")
    print("📈 Esta versión ANALIZA DATOS REALES del CSV")
    print("🔍 Reglas de sinergia configuradas:")
    for categoria, reglas in SINERGIAS_IA.items():
        print(f"   - {categoria}: {reglas['nombre_oportunidad']}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)