import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import os

THEMES = {
    "noturno": {
        "primary": "#B366FF",
        "secondary": "#A0D8FF",
        "accent": "#FFB3D9",
        "tertiary": "#A8E6D9",
        "bg_main": "#0F0F1E",
        "bg_secondary": "#1A1A2E",
        "bg_tertiary": "#16213E",
        "text_primary": "#5C13A5",
        "text_secondary": "#B8B8D8",
        "border": "#2A2A4E",
        "shadow": "rgba(179, 102, 255, 0.15)",
        "card_bg": "linear-gradient(135deg, #1A1A2E, #16213E)"
    },
    "claro": {
        "primary": "#5C13A5",
        "secondary": "#6A2BD6",
        "accent": "#DC2626",
        "tertiary": "#059669",
        "bg_main": "#FFFFFF",
        "bg_secondary": "#F3F4F6",
        "bg_tertiary": "#E5E7EB",
        "text_primary": "#5C13A5",
        "text_secondary": "#6B7280",
        "border": "#D1D5DB",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "card_bg": "linear-gradient(135deg, #F3F4F6, #E5E7EB)"
    }
}

try:
    caminho_app = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(caminho_app, "..", "dados_processados.csv")
    
    df = pd.read_csv(caminho_csv)
    df['DATE'] = pd.to_datetime(df['DATE'])
    estados_disponiveis = sorted(df['ESTADO'].unique())
    data_min = df['DATE'].min().date()
    data_max = df['DATE'].max().date()
    dados_carregados = True
except FileNotFoundError:
    df = pd.DataFrame()
    estados_disponiveis = []
    data_min = datetime(2019, 1, 1).date()
    data_max = datetime(2024, 12, 31).date()
    dados_carregados = False

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Clima Brasil 5 Anos"

app.layout = html.Div([
    dcc.Store(id="theme-store", data="noturno"),
    
    html.Div(id="main-container", style={"minHeight": "100vh", "display": "flex"}, children=[
        html.Div(
            id="sidebar",
            style={"width": "20%", "padding": "2rem", "borderRight": "1px solid", "minHeight": "100vh", "display": "flex", "flexDirection": "column"},
            children=[
                dbc.Row([
                    dbc.Col([
                        html.H3("Clima Brasil", style={"margin": "0", "fontWeight": "bold"}),
                        html.H6("Análise Climática 5 Anos", title="2019-2024")
                    ], width=9),
                    dbc.Col(
                        dbc.Button("☀️", id="theme-toggle-btn", color="link", style={"textDecoration": "none", "fontSize": "1.2rem", "padding": "0"}),
                        width=3, className="text-end"
                    )
                ], className="mb-4 align-items-center"),
                
                html.Hr(),
                html.H4("Navegação", className="mb-3", style={"fontWeight": "bold"}),
                dcc.RadioItems(
                    id="nav-radio",
                    options=[
                        {"label": " Visão Geral", "value": "visão geral"},
                        {"label": " Temperaturas", "value": "temperaturas"},
                        {"label": " Precipitação", "value": "precipitação"},
                        {"label": " Umidade", "value": "umidade"},
                        {"label": " Comparativo", "value": "comparativo"},
                        {"label": " Tendências", "value": "tendências"},
                        {"label": " Análise", "value": "análise"}
                    ],
                    value="visão geral",
                    labelStyle={"display": "block", "marginBottom": "12px", "cursor": "pointer", "color": "#9D4EDD", "fontWeight": "bold", "fontSize": "1rem", "marginLeft": "5px"},
                    inputStyle={"display": "none"}
                ),
                
                html.Hr(),
                html.H4("Filtros", className="mb-3", style={"fontWeight": "bold"}),
                
                html.Div([
                    dbc.Alert("Arquivo de dados não encontrado. Execute o pipeline primeiro.", color="warning", is_open=not dados_carregados),
                ], style={"paddingLeft": "5px"}),

                html.Div([
                    html.Label("Estado(s):", className="mb-1", style={"color": "#9D4EDD", "fontWeight": "bold", "fontSize": "1rem"}),
                    dcc.Dropdown(
                        id="estado-dropdown",
                        options=[{"label": e, "value": e} for e in estados_disponiveis],
                        multi=True,
                        value=estados_disponiveis[:3] if len(estados_disponiveis) > 3 else estados_disponiveis,
                        className="mb-1",
                        style={"color": "#1F2937"}
                    ),
                    
                    html.Label("Cidade(s):", className="mb-1", style={"color": "#9D4EDD", "fontWeight": "bold", "fontSize": "1rem"}),
                    dcc.Dropdown(
                        id="cidade-dropdown",
                        multi=True,
                        className="mb-1",
                        style={"color": "#1F2937"}
                    ),
                    
                    html.Label("Período:", className="mb-1", style={"color": "#9D4EDD", "fontWeight": "bold", "fontSize": "1rem"}),
                    dcc.DatePickerRange(
                        id="date-picker",
                        min_date_allowed=data_min,
                        max_date_allowed=data_max,
                        start_date=data_min,
                        end_date=data_max,
                        display_format="DD/MM/YYYY",
                        style={"width": "100%", "color": "#1F2937"},
                        className="mb-1"
                    )
                ], style={"display": "block" if dados_carregados else "none", "paddingLeft": "5px"}),
                
                html.Div(style={"flexGrow": "1"}),
                html.Hr()
            ]
        ),
        
        html.Div(
            id="page-content",
            style={"width": "80%", "padding": "3rem"}
        )
    ])
])

@app.callback(
    Output("cidade-dropdown", "options"),
    Output("cidade-dropdown", "value"),
    Input("estado-dropdown", "value")
)
def update_cities(selected_estados):
    if not selected_estados or not dados_carregados:
        return [], []
    cidades_filtradas = sorted(df[df['ESTADO'].isin(selected_estados)]['CIDADE'].unique())
    valor_padrao = cidades_filtradas[:3] if len(cidades_filtradas) > 3 else cidades_filtradas
    return [{"label": c, "value": c} for c in cidades_filtradas], valor_padrao

@app.callback(
    Output("main-container", "style"),
    Output("sidebar", "style"),
    Output("theme-store", "data"),
    Output("theme-toggle-btn", "children"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    State("main-container", "style"),
    State("sidebar", "style")
)
def toggle_theme(n_clicks, current_theme, main_style, sidebar_style):
    new_theme = "claro" if current_theme == "noturno" and n_clicks else ("noturno" if n_clicks else current_theme)
    theme = THEMES[new_theme]
    
    icon = "🌙" if new_theme == "claro" else "☀️"

    main_style = main_style or {}
    sidebar_style = sidebar_style or {}

    main_style.update({
        "backgroundColor": theme["bg_main"],
        "color": theme["text_primary"]
    })
    
    sidebar_style.update({
        "backgroundColor": theme["bg_secondary"],
        "borderColor": theme["border"]
    })
    
    return main_style, sidebar_style, new_theme, icon

@app.callback(
    Output("page-content", "children"),
    Input("nav-radio", "value"),
    Input("estado-dropdown", "value"),
    Input("cidade-dropdown", "value"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
    State("theme-store", "data")
)
def render_page(page, estados, cidades, start_date, end_date, current_theme):
    theme = THEMES[current_theme]
    
    content = [
        html.H1(page.title(), style={"marginBottom": "10px"}),
        html.Hr(style={"borderColor": theme["border"], "marginBottom": "30px"})
    ]

    if not dados_carregados:
        content.append(dbc.Alert("Dados indisponíveis para análise.", color="warning"))
        return content

    mask = (
        df['ESTADO'].isin(estados if estados else []) & 
        df['CIDADE'].isin(cidades if cidades else []) & 
        (df['DATE'] >= pd.to_datetime(start_date)) & 
        (df['DATE'] <= pd.to_datetime(end_date))
    )
    df_filtrado = df[mask]

    if page == "visão geral":
        content.append(html.P("Painel de resumo dos dados climáticos de 2019-2024", style={"color": theme['text_secondary'], "marginBottom": "30px"}))
        
        if df_filtrado.empty:
            content.append(dbc.Alert("Nenhum dado encontrado para os filtros aplicados.", color="warning"))
        else:
            temp_media = df_filtrado['T2M'].mean()
            precip_total = df_filtrado['PRECTOTCORR'].sum()
            umid_media = df_filtrado['RH2M'].mean()
            aquecimento = df_filtrado.get('AUMENTO_VS_2019', pd.Series([0])).mean()

            metrics = [
                ("Temp. Média", f"{temp_media:.1f}°C", "no período"),
                ("Precipitação", f"{precip_total:,.0f} mm", "acumulado"),
                ("Umidade Média", f"{umid_media:.1f}%", "relativa"),
                ("Aquecimento", f"{aquecimento:+.2f}°C", "vs 2019")
            ]

            cards = []
            for label, value, desc in metrics:
                card = html.Div(style={
                    "background": theme['card_bg'],
                    "border": f"1px solid {theme['border']}",
                    "borderRadius": "12px",
                    "padding": "20px",
                    "boxShadow": f"0 4px 20px {theme['shadow']}",
                    "height": "100%"
                }, children=[
                    html.Small(label, style={"color": theme["text_secondary"], "display": "block"}),
                    html.H2(value, style={"margin": "10px 0", "color": theme["text_primary"]}),
                    html.Small(desc, style={"color": theme["text_secondary"]})
                ])
                cards.append(dbc.Col(card, width=3))

            content.append(dbc.Row(cards, className="mb-4"))

    elif page == "temperaturas":
        content.append(html.P("Dados de temperatura mínima, máxima e média"))
    
    elif page == "precipitação":
        content.append(html.P("Volume de chuvas e padrões de precipitação"))

    elif page == "umidade":
        content.append(html.P("Umidade relativa do ar e padrões sazonais"))

    elif page == "comparativo":
        content.append(html.P("Análise comparativa entre estados e cidades"))

    elif page == "tendências":
        content.append(html.P("Análise de tendências de longo prazo e aquecimento global regional"))

    elif page == "análise":
        content.append(html.P("Mergulhe fundo nos dados com ferramentas avançadas"))

    content.append(html.Hr(style={"borderColor": theme["border"], "marginTop": "50px"}))
    content.append(html.Small(
        "Dados originários da NASA POWER API | Período: 2019-2024",
        style={"display": "block", "textAlign": "center", "color": theme["text_secondary"]}
    ))

    return content

if __name__ == "__main__":
    app.run(debug=True)