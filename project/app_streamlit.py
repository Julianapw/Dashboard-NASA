import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Clima Brasil 5 Anos",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# TEMAS E PALETA DE CORES
THEMES = {
    "noturno": {
        "primary": "#B366FF",
        "secondary": "#A0D8FF",
        "accent": "#FFB3D9",
        "tertiary": "#A8E6D9",
        "bg_main": "#0F0F1E",
        "bg_secondary": "#1A1A2E",
        "bg_tertiary": "#16213E",
        "text_primary": "#E8E8FF",
        "text_secondary": "#B8B8D8",
        "border": "#2A2A4E",
        "shadow": "rgba(179, 102, 255, 0.15)"
    },
    "claro": {
        "primary": "#5C13A5",
        "secondary": "#7C3AED",
        "accent": "#DC2626",
        "tertiary": "#059669",
        "bg_main": "#FFFFFF",
        "bg_secondary": "#F3F4F6",
        "bg_tertiary": "#E5E7EB",
        "text_primary": "#1F2937",
        "text_secondary": "#6B7280",
        "border": "#D1D5DB",
        "shadow": "rgba(0, 0, 0, 0.08)"
    }
}

if "theme" not in st.session_state:
    st.session_state.theme = "noturno"

if "page" not in st.session_state:
    st.session_state.page = "visão geral"

def apply_theme(theme_name):
    """Aplica tema com CSS customizado"""
    theme = THEMES[theme_name]
    css = f"""
    <style>
    :root {{
        --primary: {theme['primary']};
        --secondary: {theme['secondary']};
        --accent: {theme['accent']};
        --tertiary: {theme['tertiary']};
        --bg-main: {theme['bg_main']};
        --bg-secondary: {theme['bg_secondary']};
        --bg-tertiary: {theme['bg_tertiary']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --border: {theme['border']};
        --shadow: {theme['shadow']};
    }}
    
    .stApp {{
        background-color: {theme['bg_main']} !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {theme['bg_secondary']} !important;
        border-right: 1px solid {theme['border']} !important;
    }}
    
    .stMarkdown {{
        color: {theme['text_primary']} !important;
    }}
    
    body {{
        color: {theme['text_primary']} !important;
    }}
    
    p {{
        color: {"#5C3A8C" if theme_name == "claro" else theme['text_primary']} !important;
    }}
    
    small {{
        color: {"#5C3A8C" if theme_name == "claro" else theme['text_secondary']} !important;
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {theme['bg_secondary']}, {theme['bg_tertiary']}) !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px {theme['shadow']};
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        border-color: {theme['primary']} !important;
        box-shadow: 0 8px 30px {theme['shadow']};
        transform: translateY(-2px);
    }}
    
    h1, h2, h3 {{
        color: {theme['primary']} !important;
    }}
    
    .stButton > button {{
        background-color: {theme['primary']} !important;
        color: {theme['bg_main']} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        background-color: {theme['secondary']} !important;
        transform: scale(1.02) !important;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        border-color: {theme['border']} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {theme['text_secondary']} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {theme['primary']} !important;
        border-color: {theme['primary']} !important;
    }}
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {{
        background-color: {theme['bg_tertiary']} !important;
        color: {theme['text_primary']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 6px !important;
    }}
    
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {theme['bg_secondary']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {theme['primary']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {theme['secondary']};
    }}
    
    .stAlert {{
        background-color: {theme['bg_secondary']} !important;
        color: {theme['text_primary']} !important;
        border-left: 4px solid {theme['primary']} !important;
    }}
    
    [data-testid="stAlert"] {{
        background-color: {theme['bg_secondary']} !important;
        border-radius: 8px !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# SIDEBAR
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Clima Brasil")
        st.markdown("*Análise Climática 5 Anos*", help="2019-2024")
    
    with col2:
        new_theme = "claro" if st.session_state.theme == "noturno" else "noturno"
        theme_icon = "☀️" if st.session_state.theme == "noturno" else "🌙"
        if st.button(theme_icon, key="theme_btn", use_container_width=False):
            st.session_state.theme = new_theme
            st.rerun()
    
    st.divider()
    
    st.markdown("#### Navegação")
    
    nav_options = {
        "visão geral": "Visão Geral",
        "temperaturas": "Temperaturas",
        "precipitação": "Precipitação",
        "umidade": "Umidade",
        "comparativo": "Comparativo Regional",
        "tendências": "Tendências Aquecimento",
        "análise": "Análise Detalhada"
    }
    
    selected_page = st.radio(
        "Selecione uma seção:",
        options=list(nav_options.keys()),
        format_func=lambda x: nav_options[x],
        key="page_radio",
        label_visibility="collapsed"
    )
    
    st.session_state.page = selected_page
    
    st.divider()
    
    st.markdown("#### Filtros")
    
    try:
        df = pd.read_csv("dados_processados.csv")
        
        cidades = sorted(df['CIDADE'].unique())
        estados = sorted(df['ESTADO'].unique())
        
        selected_estado = st.multiselect(
            "Estado(s):",
            options=estados,
            default=estados[:3] if len(estados) > 3 else estados,
            max_selections=10
        )
        
        if selected_estado:
            cidades_filtradas = sorted(
                df[df['ESTADO'].isin(selected_estado)]['CIDADE'].unique()
            )
            selected_cidades = st.multiselect(
                "Cidade(s):",
                options=cidades_filtradas,
                default=cidades_filtradas[:3] if len(cidades_filtradas) > 3 else cidades_filtradas
            )
        else:
            selected_cidades = []
        
        st.markdown("**Período:**")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("De:", value=pd.to_datetime(df['DATE']).min())
        with col2:
            end_date = st.date_input("Até:", value=pd.to_datetime(df['DATE']).max())
    
    except FileNotFoundError:
        st.warning("Arquivo de dados não encontrado. Execute o pipeline primeiro.")
        selected_cidades = []
    
    st.divider()
    
    st.markdown("---")
    st.markdown(
        f"<small>**Tema:** {st.session_state.theme.capitalize()} | "
        f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y')}</small>",
        unsafe_allow_html=True
    )

# RENDERIZADOR DE PÁGINAS
def render_page():
    """Renderiza a página selecionada"""
    theme = THEMES[st.session_state.theme]
    
    if st.session_state.page == "visão geral":
        render_visao_geral()
    elif st.session_state.page == "temperaturas":
        render_temperaturas()
    elif st.session_state.page == "precipitação":
        render_precipitacao()
    elif st.session_state.page == "umidade":
        render_umidade()
    elif st.session_state.page == "comparativo":
        render_comparativo()
    elif st.session_state.page == "tendências":
        render_tendencias()
    elif st.session_state.page == "análise":
        render_analise()

def render_visao_geral():
    st.markdown("# Visão Geral")
    st.markdown("Painel de resumo dos dados climáticos de 2019-2024")
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Temp. Média", "24.5°C", "vs período"),
        ("Precipitação", "1,234mm", "5 anos"),
        ("Umidade Média", "72%", "relativa"),
        ("Aquecimento", "+0.8°C", "vs 2019")
    ]
    
    cols = [col1, col2, col3, col4]
    for col, (label, value, desc) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <small style="color: var(--text-secondary);">{label}</small>
                <h3 style="margin: 8px 0;">{value}</h3>
                <small style="color: var(--text-secondary);">{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

def render_temperaturas():
    st.markdown("# Análise de Temperaturas")
    st.markdown("Dados de temperatura mínima, máxima e média")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Série Histórica", "Distribuição", "Anomalias"])
    
    with tab1:
        st.info("Gráfico de série histórica de temperaturas")
    
    with tab2:
        st.info("Distribuição de temperaturas por período")
    
    with tab3:
        st.info("Anomalias de temperatura detectadas")

def render_precipitacao():
    st.markdown("# Análise de Precipitação")
    st.markdown("Volume de chuvas e padrões de precipitação")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Mapa de precipitação regional")
    
    with col2:
        st.info("Evolução temporal de chuvas")

def render_umidade():
    st.markdown("# Análise de Umidade")
    st.markdown("Umidade relativa do ar e padrões sazonais")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("Série histórica")
    
    with col2:
        st.info("Ciclo sazonal")
    
    with col3:
        st.info("Períodos críticos")

def render_comparativo():
    st.markdown("# Comparativo Regional")
    st.markdown("Análise comparativa entre estados e cidades")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Por Estado", "Por Cidade", "Ranking"])
    
    with tab1:
        st.info("Comparação entre estados")
    
    with tab2:
        st.info("Comparação entre cidades")
    
    with tab3:
        st.info("Ranking de indicadores")

def render_tendencias():
    st.markdown("# Tendências de Aquecimento")
    st.markdown("Análise de tendências de longo prazo e aquecimento global regional")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("Gráfico de tendência de aquecimento (média móvel 365 dias)")
    
    with col2:
        st.info("Estatísticas de tendência")

def render_analise():
    st.markdown("# Análise Detalhada")
    st.markdown("Mergulhe fundo nos dados com ferramentas avançadas")
    
    st.markdown("---")
    
    analise_type = st.selectbox(
        "Tipo de análise:",
        ["Correlações", "Sazonalidade", "Extremos Climáticos", "Previsões"]
    )
    
    if analise_type == "Correlações":
        st.info("Matriz de correlação entre variáveis")
    elif analise_type == "Sazonalidade":
        st.info("Análise de ciclos sazonais")
    elif analise_type == "Extremos Climáticos":
        st.info("Eventos extremos e anomalias")
    else:
        st.info("Previsões e projeções")

render_page()

@st.cache_data
def carregar_dados():
    df = pd.read_csv("../dados_processados.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    return df

try:
    df = carregar_dados()
    
    estados = sorted(df['ESTADO'].unique())
    selected_estado = st.multiselect(
        "Estado(s):",
        options=estados,
        default=estados[:3] if len(estados) > 3 else estados,
        max_selections=10
    )
    
    if selected_estado:
        cidades_filtradas = sorted(
            df[df['ESTADO'].isin(selected_estado)]['CIDADE'].unique()
        )
        selected_cidades = st.multiselect(
            "Cidade(s):",
            options=cidades_filtradas,
            default=cidades_filtradas[:3] if len(cidades_filtradas) > 3 else cidades_filtradas
        )
    else:
        selected_cidades = []
        
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("De:", value=df['DATE'].min().date())
    with col2:
        end_date = st.date_input("Até:", value=df['DATE'].max().date())

    mask = (
        df['ESTADO'].isin(selected_estado) & 
        df['CIDADE'].isin(selected_cidades) & 
        (df['DATE'].dt.date >= start_date) & 
        (df['DATE'].dt.date <= end_date)
    )
    df_filtrado = df[mask]

except FileNotFoundError:
    st.warning("Arquivo de dados não encontrado. Execute o pipeline primeiro.")
    df_filtrado = pd.DataFrame()

def render_visao_geral():
    st.markdown("# Visão Geral")
    st.markdown("Painel de resumo dos dados climáticos de 2019-2024")
    st.markdown("---")
    
    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros aplicados.")
        return

    temp_media = df_filtrado['T2M'].mean()
    precip_total = df_filtrado['PRECTOTCORR'].sum()
    umid_media = df_filtrado['RH2M'].mean()
    aquecimento = df_filtrado['AUMENTO_VS_2019'].mean()

    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Temp. Média", f"{temp_media:.1f}°C", "no período"),
        ("Precipitação", f"{precip_total:,.0f}mm", "acumulado"),
        ("Umidade Média", f"{umid_media:.1f}%", "relativa"),
        ("Aquecimento", f"{aquecimento:+.2f}°C", "vs 2019")
    ]
    
    cols = [col1, col2, col3, col4]
    for col, (label, value, desc) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <small style="color: var(--text-secondary);">{label}</small>
                <h3 style="margin: 8px 0;">{value}</h3>
                <small style="color: var(--text-secondary);">{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

st.markdown("---")
st.markdown(
    "<small style='text-align: center; display: block; color: var(--text-secondary);'>"
    "Dados originários da NASA POWER API | Período: 2019-2024"
    "</small>",
    unsafe_allow_html=True
)