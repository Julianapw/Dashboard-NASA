import requests
import pandas as pd
import io
import numpy as np
import time
import os

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
    
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(current_dir, "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    
    df_regioes = pd.read_csv(os.path.join(data_dir, "regioes.csv"))
    all_data = []

    for _, cidade in df_regioes.iterrows():
        print(f"Baixando historico de 5 anos para: {cidade['CIDADE']}...")
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
        
        final_df = final_df.drop_duplicates(subset=['CIDADE', 'DATE'])
        final_df['HEAT_INDEX'] = final_df.apply(lambda x: calculate_heat_index(x['T2M'], x['RH2M']), axis=1)
        
        final_df = final_df.sort_values(['CIDADE', 'DATE'])
        final_df['TENDENCIA_AQUECIMENTO'] = final_df.groupby('CIDADE')['T2M'].transform(lambda x: x.rolling(window=365, min_periods=1).mean())
        
        media_2019 = final_df[final_df['YEAR'] == 2019].groupby('CIDADE')['T2M'].mean()
        final_df['AUMENTO_VS_2019'] = final_df.apply(lambda x: x['T2M'] - media_2019.get(x['CIDADE'], x['T2M']), axis=1)
        
        final_df['INDICE_COMPOSTO'] = (final_df['T2M'] * 0.5) + (final_df['RH2M'] * 0.3) - (final_df['PRECTOTCORR'] * 0.2)
        final_df['DIA_CHUVOSO'] = final_df['PRECTOTCORR'].apply(lambda x: 1 if x > 2.5 else 0)

        final_df.to_csv(os.path.join(data_dir, "dados_processados.csv"), index=False)
        print(f"\nPipeline Historico Concluido! Total: {len(final_df)} registros limpos.")
    else:
        print("Falha na coleta.")