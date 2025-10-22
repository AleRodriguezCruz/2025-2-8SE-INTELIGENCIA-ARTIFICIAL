import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import json

# --- CONFIGURACIÓN ---
st.set_page_config(
    page_title="Emprende IA", 
    page_icon="🤖", 
    layout="wide"
)

# Zonas conocidas
ZONAS_CONOCIDAS = {
    "maneadero": (31.7167, -116.5667, 3), 
    "centro": (31.8650, -116.6217, 2),
    "chapultepec": (31.8386, -116.6014, 2), 
    "sauzal": (31.8833, -116.6833, 2.5),
    "valle dorado": (31.8489, -116.5858, 2)
}

API_URL = "http://localhost:8000"

# --- FUNCIÓN PARA LA API ---
def analizar_con_api(zona, radio_km=2.0):
    try:
        st.info(f"🔍 Solicitando datos de {zona} a la API...")
        
        response = requests.get(
            f"{API_URL}/oportunidades/{zona}",
            params={"radio_km": radio_km},
            timeout=10
        )
        
        if response.status_code == 200:
            datos = response.json()
            st.success(f"✅ Datos recibidos de la API para {zona}")
            return datos
        else:
            st.error(f"❌ Error de la API: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("""
        ❌ No se puede conectar con la API. 
        
        **Solución:**
        1. Abre una terminal
        2. Ejecuta: `python api.py`  
        3. Espera a que diga: `Uvicorn running on http://0.0.0.0:8000`
        4. Recarga esta página
        """)
        return None
    except Exception as e:
        st.error(f"🚨 Error inesperado: {str(e)}")
        return None

# --- FUNCIÓN PARA CREAR MAPA ---
def crear_mapa_bonito(zona_info, oportunidades=None):
    """Crea el mapa con keys únicas"""
    lat_zona, lon_zona, _ = zona_info
    
    mapa = folium.Map(
        location=[lat_zona, lon_zona], 
        zoom_start=14,
        tiles='OpenStreetMap',
        width='100%',
        height=500
    )
    
    folium.TileLayer('OpenStreetMap').add_to(mapa)
    folium.TileLayer('CartoDB positron').add_to(mapa)
    folium.LayerControl().add_to(mapa)
    
    # Marcar el centro de la zona
    folium.Marker(
        [lat_zona, lon_zona],
        tooltip="Centro de la zona analizada",
        icon=folium.Icon(color='purple', icon='home')
    ).add_to(mapa)
    
    # Marcar oportunidades de la API
    if oportunidades:
        for i, op in enumerate(oportunidades):
            # Marcador AZUL para el negocio "ancla"
            folium.Marker(
                [op['ancla_lat'], op['ancla_lon']], 
                tooltip=f"Ancla: {op['ancla']}",
                popup=f"<b>{op['ancla']}</b><br>{op['oportunidad']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)
            
            # Marcador VERDE para la OPORTUNIDAD
            folium.Marker(
                [op['ancla_lat'] + 0.0003, op['ancla_lon'] + 0.0003],
                tooltip=f"Oportunidad: {op['oportunidad']}",
                popup=f"<b>Oportunidad:</b> {op['oportunidad']}",
                icon=folium.Icon(color='green', icon='star')
            ).add_to(mapa)
            
            # Círculo de área de influencia
            folium.Circle(
                location=[op['ancla_lat'], op['ancla_lon']],
                radius=500,
                popup=f"Área de oportunidad",
                color='green',
                fill=True,
                fillOpacity=0.1
            ).add_to(mapa)
    
    return mapa

# --- INTERFAZ PRINCIPAL ---
st.title("🤖 Emprende IA v2.0")
st.header("Tu Asistente de Negocios Inteligente para Ensenada")
st.markdown("---")

# Estado de la aplicación
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'zona_analizada' not in st.session_state:
    st.session_state.zona_analizada = None

# Panel de control
col_config, col_resultados = st.columns([1, 2])

with col_config:
    with st.container(border=True):
        st.subheader("🔧 Configuración del Análisis")
        
        zona_seleccionada = st.selectbox(
            "Selecciona una zona:",
            options=list(ZONAS_CONOCIDAS.keys()),
            format_func=lambda x: x.title(),
            key="selector_zona_principal"
        )
        
        radio_seleccionado = st.slider(
            "Radio de búsqueda (km):", 
            0.5, 5.0, 2.0, 0.5,
            key="slider_radio_principal"
        )
        
        if st.button("🎯 Analizar con API", type="primary", use_container_width=True, key="boton_analizar_principal"):
            with st.spinner(f'Consultando API para {zona_seleccionada.title()}...'):
                resultados = analizar_con_api(zona_seleccionada, radio_seleccionado)
                
                if resultados:
                    st.session_state.resultados = resultados
                    st.session_state.zona_analizada = zona_seleccionada
                    st.success("✅ ¡Análisis desde API completado!")
                else:
                    st.error("❌ No se pudieron obtener datos de la API")

with col_resultados:
    if st.session_state.resultados and st.session_state.zona_analizada:
        datos = st.session_state.resultados
        zona_nombre = st.session_state.zona_analizada
        
        if datos.get('zona') != zona_nombre:
            st.warning(f"⚠️ Los datos no coinciden. Esperado: {zona_nombre}, Recibido: {datos.get('zona')}")
        else:
            st.success(f"✅ **{zona_nombre.title()}** - Datos desde API")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Negocios en zona", datos.get('total_negocios_zona', 0))
            with col2:
                st.metric("Oportunidades", datos.get('total_oportunidades', 0))
            with col3:
                total = datos.get('total_negocios_zona', 1)
                opor = datos.get('total_oportunidades', 0)
                tasa = (opor / total) * 100 if total > 0 else 0
                st.metric("Tasa", f"{tasa:.1f}%")
            
            st.info(f"📍 **Zona:** {zona_nombre.title()} | 📏 **Radio:** {radio_seleccionado}km")
            
            # Mostrar información de la IA
            if datos.get('nota'):
                st.info(f"🔍 **{datos.get('nota')}**")
            
            if datos.get('oportunidades'):
                st.subheader(f"💡 Oportunidades Detectadas ({len(datos['oportunidades'])})")
                
                # Mostrar cada oportunidad SIN KEY en el expander
                for i, op in enumerate(datos['oportunidades']):
                    # EXPANDER SIN PARÁMETRO KEY
                    with st.expander(f"🏪 {op['oportunidad']} - Cerca de {op['ancla']}", expanded=True):
                        
                        col_info, col_mapa = st.columns([2, 1])
                        
                        with col_info:
                            st.write(f"**Tipo:** {op.get('categoria_sinergia', 'N/A').title()}")
                            st.write(f"**Ancla:** {op['ancla']}")
                            st.write(f"**Dirección:** {op.get('ancla_direccion', 'Coordenadas disponibles')}")
                            st.write(f"**Confianza:** {op.get('confianza', 'alta')}")
                            
                            if 'educacion' in op.get('categoria_sinergia', ''):
                                st.info("💡 **Recomendación:** Papelería, útiles escolares, copias")
                            elif 'salud' in op.get('categoria_sinergia', ''):
                                st.info("💡 **Recomendación:** Farmacia, productos médicos")
                            elif 'deporte' in op.get('categoria_sinergia', ''):
                                st.info("💡 **Recomendación:** Suplementos, ropa deportiva")
                        
                        with col_mapa:
                            # Mapa mini con KEY ÚNICA
                            mapa_mini = folium.Map(
                                location=[op['ancla_lat'], op['ancla_lon']], 
                                zoom_start=16,
                                width=200,
                                height=150
                            )
                            folium.Marker(
                                [op['ancla_lat'], op['ancla_lon']],
                                tooltip=op['ancla'],
                                icon=folium.Icon(color='red', icon='info-sign')
                            ).add_to(mapa_mini)
                            
                            # KEY ÚNICA para cada st_folium
                            st_folium(mapa_mini, 
                                    height=150, 
                                    width=200, 
                                    key=f"mapa_mini_{zona_nombre}_{i}")
                
                # --- MAPA PRINCIPAL ---
                st.subheader("🗺️ Mapa de Oportunidades")
                
                oportunidades_para_mapa = []
                for op in datos['oportunidades']:
                    oportunidades_para_mapa.append({
                        'ancla': op['ancla'],
                        'ancla_lat': op['ancla_lat'],
                        'ancla_lon': op['ancla_lon'],
                        'oportunidad': op['oportunidad'],
                        'categoria_sinergia': op['categoria_sinergia']
                    })
                
                zona_info = ZONAS_CONOCIDAS[zona_nombre]
                mapa_principal = crear_mapa_bonito(zona_info, oportunidades_para_mapa)
                
                # KEY ÚNICA para el mapa principal
                st_folium(mapa_principal, 
                         height=500, 
                         use_container_width=True, 
                         key=f"mapa_principal_{zona_nombre}")
                
            else:
                st.warning("No se encontraron oportunidades en la API para esta zona")
                
                # Mapa de la zona sin oportunidades
                zona_info = ZONAS_CONOCIDAS[zona_nombre]
                mapa_vacio = crear_mapa_bonito(zona_info)
                st_folium(mapa_vacio, 
                         height=400, 
                         use_container_width=True, 
                         key=f"mapa_vacio_{zona_nombre}")
    
    else:
        st.info("👋 ¡Bienvenido! Usa el panel de configuración para analizar una zona con la API")
        
        # Mapa de bienvenida
        st.subheader("📍 Zonas Disponibles para Análisis")
        mapa_bienvenida = folium.Map(
            location=[31.8650, -116.6217],
            zoom_start=11
        )
        
        for zona_nombre, zona_info in ZONAS_CONOCIDAS.items():
            folium.Marker(
                [zona_info[0], zona_info[1]],
                tooltip=zona_nombre.title(),
                popup=f"Analizar {zona_nombre.title()}"
            ).add_to(mapa_bienvenida)
        
        st_folium(mapa_bienvenida, 
                 height=400, 
                 use_container_width=True, 
                 key="mapa_bienvenida")

# --- DEBUG Y MODO EMERGENCIA ---
with st.sidebar:
    st.subheader("🔍 Verificación API")
    
    if st.button("Probar Conexión API", key="boton_test_api"):
        try:
            response = requests.get(f"{API_URL}/test", timeout=5)
            if response.status_code == 200:
                st.success("✅ API conectada correctamente")
                st.json(response.json())
            else:
                st.error("❌ API no responde")
        except:
            st.error("❌ No se puede conectar a la API")
    
    if st.session_state.resultados:
        st.write("**Última respuesta API:**")
        st.write(f"- Zona: {st.session_state.resultados.get('zona')}")
        st.write(f"- Oportunidades: {st.session_state.resultados.get('total_oportunidades')}")
        st.write(f"- Datos reales: {len(st.session_state.resultados.get('oportunidades', []))}")
    
    # Modo emergencia
    with st.expander("🆕 Modo Emergencia", expanded=False):
        st.warning("Usa solo si la API falla")
        
        zona_emergencia = st.selectbox(
            "Zona para análisis rápido:",
            options=list(ZONAS_CONOCIDAS.keys()),
            format_func=lambda x: x.title(),
            key="selector_emergencia"
        )
        
        if st.button("Ejecutar Análisis Rápido", key="boton_emergencia"):
            # Datos mínimos de ejemplo
            datos_ejemplo = {
                "zona": zona_emergencia,
                "total_negocios_zona": 100,
                "total_oportunidades": 2,
                "oportunidades": [
                    {
                        "categoria_sinergia": "educacion",
                        "oportunidad": "Papelería / Tienda de útiles",
                        "ancla": f"Escuela en {zona_emergencia.title()}",
                        "ancla_direccion": "Dirección ejemplo",
                        "ancla_lat": ZONAS_CONOCIDAS[zona_emergencia][0],
                        "ancla_lon": ZONAS_CONOCIDAS[zona_emergencia][1],
                        "confianza": "media"
                    }
                ],
                "nota": "⚠️ Modo emergencia - Datos de ejemplo"
            }
            
            st.session_state.resultados = datos_ejemplo
            st.session_state.zona_analizada = zona_emergencia
            st.rerun()

# --- BOTÓN PARA LIMPIAR ---
with st.sidebar:
    if st.session_state.resultados:
        if st.button("🧹 Limpiar Resultados", key="boton_limpiar"):
            st.session_state.resultados = None
            st.session_state.zona_analizada = None
            st.rerun()