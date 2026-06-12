import os
import pandas as pd

def clean_population_data(raw_path):
    df = pd.read_csv(raw_path)
    
    df.rename(columns={df.columns[0]: "Regiao"}, inplace=True)
    df["Regiao"] = df["Regiao"].astype(str).str.strip()
    
    df_long = df.melt(
        id_vars=["Regiao"], 
        var_name="ANO", 
        value_name="POPULACAO"
    )
    
    df_long["ANO"] = pd.to_numeric(df_long["ANO"]).astype(int)
    df_long["POPULACAO"] = pd.to_numeric(df_long["POPULACAO"]).astype(int)
    
    return df_long

def clean_nasa_data(raw_path):
    df = pd.read_csv(raw_path)
    
    df.rename(columns={"REGIAO_REPRESENTATIVA": "Regiao"}, inplace=True)
    df["Regiao"] = df["Regiao"].astype(str).str.strip()
    
    df["YEAR"] = df["YEAR"].astype(int)
    df["DOY"] = df["DOY"].astype(int)
    
    return df

def run_cleaning_pipeline():
    
    raw_pop_path = os.path.join("data", "raw", "Tabela 6579.csv")
    raw_nasa_path = os.path.join("data", "raw", "clima_nasa_raw.csv")
    
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    df_pop_clean = clean_population_data(raw_pop_path)
    df_nasa_clean = clean_nasa_data(raw_nasa_path)
    
    print("- Integrando as bases de dados via Merge...")
    df_integrated = pd.merge(
        df_nasa_clean, 
        df_pop_clean, 
        left_on=["Regiao", "YEAR"], 
        right_on=["Regiao", "ANO"], 
        how="inner"
    )
    
    df_integrated.drop(columns=["ANO"], inplace=True)
    
    output_path = os.path.join(processed_dir, "dados_combinados_clean.csv")
    df_integrated.to_csv(output_path, index=False)
    
    print(f"Arquivo integrado salvo em: {output_path}")
    print(f"Total de registros gerados: {df_integrated.shape[0]} linhas\n")

if __name__ == "__main__":
    run_cleaning_pipeline()