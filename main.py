import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt

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
2. **Optimización de Distribución** con Caminos Mínimos (Algoritmo de Dijkstra).  
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

    # Variables de decisión
    x1 = pulp.LpVariable("Deportivas", lowBound=0, cat="Integer")
    x2 = pulp.LpVariable("Casuales", lowBound=0, cat="Integer")

    # Función objetivo
    modelo += 15000*x1 + 10000*x2

    # Restricciones
    modelo += 2*x1 + 1*x2 <= tela
    modelo += 1*x1 + 1.5*x2 <= confeccion
    modelo += 0.5*x1 + 0.25*x2 <= estampado

    modelo.solve()

    st.success("✅ Producción Óptima Calculada")

    # Resultados dentro de expander
    with st.expander("📊 Resultados de Producción"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Camisetas Deportivas", f"{x1.varValue:.0f}")
        col2.metric("Camisetas Casuales", f"{x2.varValue:.0f}")
        col3.metric("Utilidad Máxima", f"${pulp.value(modelo.objective):,.0f}")

# =====================
# Sección 2: Distribución
# =====================
st.header("🚚 Distribución con Caminos Mínimos (Dijkstra)")
st.markdown("Se consideran los nodos: **Planta, Bodega, Cliente1, Cliente2, Cliente3**.")

# Definimos las aristas con costos/distancias
edges = [
    ("Planta", "Bodega", 10),
    ("Planta", "Cliente1", 20),
    ("Bodega", "Cliente1", 5),
    ("Bodega", "Cliente2", 8),
    ("Cliente1", "Cliente2", 12),
    ("Planta", "Cliente3", 25),
    ("Cliente2", "Cliente3", 7),
]

if st.button("Calcular Caminos Óptimos"):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)

    destinos = ["Cliente1", "Cliente2", "Cliente3"]

    st.success("✅ Caminos Óptimos Calculados")

    # Resultados dentro de expander
    with st.expander("🚚 Resultados de Rutas Óptimas"):
        for d in destinos:
            dist = nx.dijkstra_path_length(G, "Planta", d)
            path = nx.dijkstra_path(G, "Planta", d)
            st.info(f"📍 {d}: camino {path} con costo {dist}")

    # Grafo dentro de expander
    with st.expander("📍 Visualización del Grafo de Distribución"):
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(7, 5))
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="#90caf9", font_size=10, font_weight="bold")
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        st.pyplot(plt)
