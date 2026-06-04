import requests
import pandas as pd
import io
import numpy as np
import time

# def calculate_heat_index(temp, rh):
#     """Calcula a Sensação Térmica."""
#     if temp < 20: return temp
#     hi = temp + 0.5555 * (6.11 * np.exp(5417.7530 * (1/273.16 - 1/(273.15 + rh))) - 10)
#     return hi

def calculate_heat_index(temp, rh):
    """Calcula a Sensação Térmica (Humidex) corrigida."""
    if temp < 20: 
        return temp
    
    # 1. Calcula a pressão de vapor de saturação baseada na temperatura atual (em Celsius)
    e_sat = 6.11 * np.exp(5417.7530 * (1/273.16 - 1/(273.15 + temp)))
    e_actual = e_sat * (rh / 100.0)
    hi = temp + 0.5555 * (e_actual - 10)
    return hi

def fetch_nasa_point_data(lat, lon, start_date="20190101", end_date="20240331"):
    """Coleta dados de um ponto específico por 5 anos."""
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "start": start_date, "end": end_date,
        "latitude": lat, "longitude": lon,
        "community": "ag", "parameters": "T2M,RH2M,PRECTOTCORR",
        "format": "csv"
    }
    try:
        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code == 200:
            csv_part = response.text.split("-END HEADER-")[-1].strip()
            return pd.read_csv(io.StringIO(csv_part))
    except Exception as e:
        print(f"Erro na coordenada {lat}, {lon}: {e}")
    return None

if __name__ == "__main__":
    print("Iniciando Pipeline Histórico (2019-2024)...")
    
    df_regioes = pd.read_csv("regioes.csv")
    # Limpa linhas vazias, remove cabeçalhos duplicados e deleta cidades repetidas
    df_regioes = df_regioes.dropna(subset=['CIDADE']).drop_duplicates(subset=['CIDADE'])
    df_regioes = df_regioes[df_regioes['CIDADE'] != 'CIDADE']
    all_data = []

    for _, cidade in df_regioes.iterrows():
        print(f"Baixando histórico de 5 anos para: {cidade['CIDADE']}...")
        df_cidade = fetch_nasa_point_data(cidade['LAT'], cidade['LON'])
        
        if df_cidade is not None:
            df_cidade['ESTADO'] = cidade['ESTADO']
            df_cidade['CIDADE'] = cidade['CIDADE']
            df_cidade['REGIAO'] = cidade['REGIAO']
            all_data.append(df_cidade)
            print(f"{len(df_cidade)} dias coletados.")
        time.sleep(1)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.replace(-999, np.nan).dropna(subset=['T2M', 'RH2M'])
        final_df['DATE'] = pd.to_datetime(final_df['YEAR'].astype(str) + final_df['DOY'].astype(str), format='%Y%j')

        # --- MÉTRICAS MASTIGADAS PARA O DASHBOARD ---
        
        # 1. Sensação Térmica
        final_df['HEAT_INDEX'] = final_df.apply(lambda x: calculate_heat_index(x['T2M'], x['RH2M']), axis=1)
        
        # 2. Métrica de Tendência: Média Móvel de 365 dias (Suaviza estações para ver o aquecimento)
        # Isso mostra se a 'linha base' de cada cidade está subindo
        final_df = final_df.sort_values(['CIDADE', 'DATE'])
        final_df['TENDENCIA_AQUECIMENTO'] = final_df.groupby('CIDADE')['T2M'].transform(lambda x: x.rolling(window=365, min_periods=1).mean())

        # 3. Métrica de Impacto: Diferença vs Primeiro Ano (Início do Aquecimento)
        # Calcula quanto a temperatura de hoje está diferente da média do primeiro ano (2019)
        # Isso gera um insight automático para o Dashboard
        media_2019 = final_df[final_df['YEAR'] == 2019].groupby('CIDADE')['T2M'].mean()
        final_df['AUMENTO_VS_2019'] = final_df.apply(lambda x: x['T2M'] - media_2019.get(x['CIDADE'], x['T2M']), axis=1)

        final_df.to_csv("dados_processados.csv", index=False)
        print(f"\nPipeline Histórico Concluído! Total: {len(final_df)} registros.")
    else:
        print("Falha na coleta.")