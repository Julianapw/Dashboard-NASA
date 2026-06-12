import io
import os
import time
import requests
import pandas as pd

def fetch_nasa_point_data(lat, lon, start_date="20110101", end_date="20211231"):
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "start": start_date, 
        "end": end_date,
        "latitude": lat, 
        "longitude": lon,
        "community": "ag", 
        "parameters": "T2M,RH2M,PRECTOTCORR",
        "format": "csv"
    }
    try:
        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code == 200:
            csv_part = response.text.split("-END HEADER-")[-1].strip()
            df = pd.read_csv(io.StringIO(csv_part))
            return df
    except Exception as e:
        print(f"Erro na coordenada {lat}, {lon}: {e}")
    return None

if __name__ == "__main__":
    regioes_coordenadas = [
        {"nome": "Norte", "lat": -3.1190, "lon": -60.0217},
        {"nome": "Nordeste", "lat": -12.9714, "lon": -38.5014},
        {"nome": "Sudeste", "lat": -23.5505, "lon": -46.6333},
        {"nome": "Sul", "lat": -25.4290, "lon": -49.2671},
        {"nome": "Centro-Oeste", "lat": -15.7938, "lon": -47.8827}
    ]
    
    lista_dataframes = []
    
    for regiao in regioes_coordenadas:
        print(f"Extraindo dados brutos da API para a Região {regiao['nome']}...")
        df_regiao = fetch_nasa_point_data(regiao["lat"], regiao["lon"])
        
        if df_regiao is not None:
            df_regiao["REGIAO_REPRESENTATIVA"] = regiao["nome"]
            lista_dataframes.append(df_regiao)
            
        time.sleep(2)
        
    if lista_dataframes:
        df_raw_completo = pd.concat(lista_dataframes, ignore_index=True)
        
        output_dir = os.path.join("data", "raw")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, "clima_nasa_raw.csv")
        df_raw_completo.to_csv(output_path, index=False)
        
        print("\n--- EXTRAÇÃO CONCLUÍDA COM SUCESSO ---")
        print(f"Dados salvos em: {output_path}")
        print(f"Total de registros brutos extraídos: {df_raw_completo.shape[0]}")
    else:
        print("Nenhum dado pôde ser extraído da API da NASA.")