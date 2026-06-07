import requests
import pandas as pd
import os

def fetch_ibge_regional_data():
    url = "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93?localidades=N2[all]"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            results = data[0]['resultados'][0]['series']
            regional_rows = []
            for item in results:
                region_name = item['localidade']['nome']
                population = int(item['serie']['2022'])
                regional_rows.append({
                    "REGIAO": region_name,
                    "POPULACAO_REGIAO": population
                })
            return pd.DataFrame(regional_rows)
    except Exception as e:
        print(f"Erro ao coletar dados regionais do IBGE: {e}")
    return None

if __name__ == "__main__":
    print("Iniciando coleta de dados populacionais por Regiao...")
    df_regioes_ibge = fetch_ibge_regional_data()
    if df_regioes_ibge is not None:
        target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        os.makedirs(target_dir, exist_ok=True)
        df_regioes_ibge.to_csv(os.path.join(target_dir, "dados_ibge.csv"), index=False)
        print("Arquivo dados_ibge.csv gerado com sucesso por Regiao!")
    else:
        print("Falha na geracao do arquivo.")