import os
import pandas as pd

def load_clean_data(input_path):
    return pd.read_csv(input_path)

def extract_date_features(df):
    date_series = pd.to_datetime(df["YEAR"].astype(str) + "-" + df["DOY"].astype(str), format="%Y-%j")
    
    df["ANO"] = date_series.dt.year
    df["MES"] = date_series.dt.month
    
    df.drop(columns=["DOY", "YEAR"], inplace=True)
    return df

def aggregate_to_executive_view(df):
    # Agrupa os dados diários em uma visão mensal sintética por Região
    # Isso reduz o volume de linhas e consolida os principais indicadores
    df_exec = df.groupby(["Regiao", "ANO", "MES"]).agg(
        TEMP_MEDIA=("T2M", "mean"),
        UMIDADE_MEDIA=("RH2M", "mean"),
        PRECIPITACAO_ACUMULADA=("PRECTOTCORR", "sum"),
        POPULACAO_ESTIMADA=("POPULACAO", "first")
    ).reset_index()
    
    return df_exec

def run_transformation_pipeline():
    print("Iniciando a etapa de Transformação para o Painel Executivo...")
    
    input_path = os.path.join("data", "processed", "dados_combinados_clean.csv")
    output_path = os.path.join("data", "processed", "dados_dashboard_executivo.csv")
    
    if not os.path.exists(input_path):
        print(f"Erro: O arquivo {input_path} não foi encontrado. Rode o cleaning.py primeiro.")
        return

    df = load_clean_data(input_path)
    
    print("- Extraindo componentes de tempo dos registros...")
    df = extract_date_features(df)
    
    print("- Agregando dados para formato sintético (Mensal por Região)...")
    df_executive = aggregate_to_executive_view(df)
    
    # Salvando a base pronta para os gráficos executivos
    df_executive.to_csv(output_path, index=False)
    
    print("\n--- ETAPA DE TRANSFORMAÇÃO CONCLUÍDA ---")
    print(f"Arquivo executivo gerado com sucesso em: {output_path}")
    print(f"Colunas prontas para os gráficos: {list(df_executive.columns)}\n")

if __name__ == "__main__":
    run_transformation_pipeline()