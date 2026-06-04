import pandas as pd

def gerar_insights_etapa_5():
    try:
        df = pd.read_csv("dados_processados.csv")
    except FileNotFoundError:
        print("Erro: O arquivo dados_processados.csv não foi encontrado. Rode o pipeline primeiro.")
        return

    print("=" * 60)
    print("        ETAPA 5: ANÁLISE EXPLORATÓRIA E INSIGHTS")
    print("=" * 60 + "\n")
    print("--- 1. AUMENTO DE TEMPERATURA EM RELAÇÃO A 2019 ---")
    
    aumento_medio_geral = df.groupby('REGIAO')['AUMENTO_VS_2019'].mean().sort_values(ascending=False)

    df_2023 = df[df['YEAR'] == 2023]
    aumento_medio_2023 = df_2023.groupby('REGIAO')['AUMENTO_VS_2019'].mean().sort_values(ascending=False)
    
    print("\n[Insights para o Dashboard] Aumento médio histórico acumulado (Região):")
    for regiao, valor in aumento_medio_geral.items():
        print(f" - Região {regiao}: {valor:+.2f}°C em média vs 2019")
        
    print("\n[Insights para o Dashboard] Aumento médio especificamente no ano de 2023:")
    for regiao, valor in aumento_medio_2023.items():
        print(f" - Região {regiao}: {valor:+.2f}°C vs 2019")
    
    print("\n" + "-"*50 + "\n")

    print("--- 2. ANÁLISE DE CRITICIDADE DO ÍNDICE DE CALOR ---")
    
    LIMIAR_CRITICO = 35.0
    df['DIA_CRITICO'] = df['HEAT_INDEX'] >= LIMIAR_CRITICO
 
    ranking_criticidade = df.groupby(['REGIAO', 'CIDADE', 'ESTADO']).agg(
        Media_Indice_Calor=('HEAT_INDEX', 'mean'),
        Max_Indice_Calor=('HEAT_INDEX', 'max'),
        Total_Dias_Criticos=('DIA_CRITICO', 'sum'),
        Total_Dias_Monitorados=('DIA_CRITICO', 'count')
    ).reset_index()
 
    ranking_criticidade['PCT_DIAS_CRITICOS'] = (ranking_criticidade['Total_Dias_Criticos'] / ranking_criticidade['Total_Dias_Monitorados']) * 100
 
    ranking_top_critico = ranking_criticidade.sort_values(by='Total_Dias_Criticos', ascending=False)
    
    print(f"\nTop 5 Cidades onde o Índice de Calor é mais crítico (Limiar >= {LIMIAR_CRITICO}°C):")
    for idx, row in ranking_top_critico.head(5).iterrows():
        print(f" {idx+1}. {row['CIDADE']} - {row['ESTADO']} ({row['REGIAO']})")
        print(f"    -> Dias críticos: {row['Total_Dias_Criticos']} de {row['Total_Dias_Monitorados']} ({row['PCT_DIAS_CRITICOS']:.1f}% do tempo)")
        print(f"    -> Média do Índice de Calor: {row['Media_Indice_Calor']:.1f}°C | Pico Máximo: {row['Max_Indice_Calor']:.1f}°C")
  
    print("\nCriticidade consolidada por Região (Total de dias críticos acumulados nas cidades):")
    criticidade_regional = df.groupby('REGIAO')['DIA_CRITICO'].sum().sort_values(ascending=False)
    for regiao, dias in criticidade_regional.items():
        print(f" - Região {regiao}: {dias} dias registrados acima de {LIMIAR_CRITICO}°C")

if __name__ == "__main__":
    gerar_insights_etapa_5()