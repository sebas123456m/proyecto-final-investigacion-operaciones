import streamlit as st
import pulp
import googlemaps
import folium
from streamlit.components.v1 import html
from folium import plugins
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# =====================
# API Key de Google Maps
# =====================
API_KEY = "AIzaSyC-idabcGJZP7G8JT-AxvWA4IpHmmXU-9Q"  # Reemplaza con tu API Key
gmaps = googlemaps.Client(key=API_KEY)

# =====================
# Estilos con CSS
# =====================
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    h1, h2, h3 { color: #1e3d59; font-family: 'Segoe UI', sans-serif; }
    .stMetric {
        background: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    div.stButton > button {
        background-color: #1e88e5;
        color: white;
        border-radius: 12px;
        font-size: 16px;
        padding: 8px 20px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #1565c0;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# =====================
# Configuración de la página
# =====================
st.set_page_config(page_title="Optimización Deportivos Alba", layout="wide")
st.title("⚡ Optimización Integral - Deportivos Alba")
st.markdown("""
Aplicación para apoyar la toma de decisiones en la microempresa **Deportivos Alba**:

1. **Optimización de Producción** con Programación Lineal (Método Simplex).  
2. **Optimización de Distribución** con Caminos Mínimos.  
""")

# =====================
# Sección 1: Producción
# =====================
st.header("📊 Producción Óptima")
with st.container():
    colA, colB, colC = st.columns(3)
    tela = colA.number_input("Tela disponible (m)", value=400)
    confeccion = colB.number_input("Horas de confección disponibles", value=300)
    estampado = colC.number_input("Horas de estampado disponibles", value=100)

if st.button("Calcular Producción Óptima"):
    modelo = pulp.LpProblem("Producción_Camisetas", pulp.LpMaximize)
    x1 = pulp.LpVariable("Deportivas", lowBound=0, cat="Integer")
    x2 = pulp.LpVariable("Casuales", lowBound=0, cat="Integer")
    modelo += 15000*x1 + 10000*x2
    modelo += 2*x1 + 1*x2 <= tela
    modelo += 1*x1 + 1.5*x2 <= confeccion
    modelo += 0.5*x1 + 0.25*x2 <= estampado
    modelo.solve()

    st.success("✅ Producción Óptima Calculada")
    with st.expander("📊 Resultados de Producción"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Camisetas Deportivas", f"{x1.varValue:.0f}")
        col2.metric("Camisetas Casuales", f"{x2.varValue:.0f}")
        col3.metric("Utilidad Máxima", f"${pulp.value(modelo.objective):,.0f}")

# =====================
# Sección 2: Caminos Mínimos con Google Maps
# =====================
st.header("🚚 Distribución con  caminos minimos")
origen = st.text_input("Dirección de Origen", "Calle 26 # 13-45, Bogotá, Colombia")
destinos = st.text_area(
    "Destinos (una línea por destino)",
    "Éxito Calle 80\nÉxito Av 68\nÉxito Suba"
).splitlines()

def obtener_url_foto(lugar, api_key, maxwidth=250):
    try:
        result = gmaps.find_place(lugar, input_type="textquery", fields=["photos"])
        if "candidates" in result and result["candidates"]:
            fotos = result["candidates"][0].get("photos", [])
            if fotos:
                photo_ref = fotos[0]["photo_reference"]
                url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={photo_ref}&key={api_key}"
                return url
    except:
        return None
    return None

if st.button("Calcular Ruta"):
    lugares = [origen] + destinos
    coordenadas = {}
    for lugar in lugares:
        try:
            geocode_result = gmaps.geocode(lugar)
            if geocode_result:
                loc = geocode_result[0]['geometry']['location']
                coordenadas[lugar] = (loc['lat'], loc['lng'])
            else:
                st.warning(f"⚠️ No se pudo geolocalizar: {lugar}")
        except Exception as e:
            st.error(f"Error geolocalizando {lugar}: {e}")

    mapa = folium.Map(location=coordenadas[origen], zoom_start=13)
    cmap = cm.get_cmap("tab10")
    norm = mcolors.Normalize(vmin=0, vmax=len(destinos)-1)

    for i, destino in enumerate(destinos):
        try:
            directions_result = gmaps.directions(origen, destino, mode="driving")
            leg = directions_result[0]['legs'][0]
            distance_km = leg['distance']['value'] / 1000
            duration_min = leg['duration']['value'] / 60
            polyline_points = directions_result[0]['overview_polyline']['points']
            coords = googlemaps.convert.decode_polyline(polyline_points)
            coords_list = [(p['lat'], p['lng']) for p in coords]
            color_hex = mcolors.to_hex(cmap(norm(i)))

            polyline = folium.PolyLine(locations=coords_list, color=color_hex, weight=5, opacity=0.8)
            mapa.add_child(polyline)
            plugins.PolyLineTextPath(polyline, "➤➤➤", repeat=True, offset=8,
                                     attributes={"fill": color_hex, "font-weight": "bold", "font-size": "14"}).add_to(mapa)

            url_foto = obtener_url_foto(destino, API_KEY)
            foto_html = f"<br><img src='{url_foto}' width='250'>" if url_foto else "<br>⚠️ No hay foto disponible"

            popup_html = f"""
            <div style="
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                color: #1e3d59;
                background-color: #f0f8ff;
                padding: 6px 10px;
                border-radius: 6px;
                border: 2px solid #1e90ff;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.4);
                text-align: center;
            ">
                <b>Destino:</b> {destino}<br>
                <b>Distancia:</b> {distance_km:.2f} km<br>
                <b>Duración:</b> {duration_min:.0f} min
                {foto_html}
            </div>
            """

            folium.Marker(location=coordenadas[destino], popup=folium.Popup(popup_html, max_width=300),
                          icon=folium.Icon(color="blue", icon="info-sign")).add_to(mapa)

        except Exception as e:
            st.error(f"Error calculando ruta a {destino}: {e}")

    folium.Marker(location=coordenadas[origen],
                  popup=f"<b>Origen:</b> {origen}",
                  icon=folium.Icon(color="green", icon="home")).add_to(mapa)

    # Mostrar mapa en Streamlit usando HTML incrustado
    html(mapa._repr_html_(), height=600)
