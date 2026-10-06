# ==============================================================================
# TCC - ROTEIRIZAÇÃO INTELIGENTE EM TRADE MARKETING
# Script 3: Geração de fRoteiro_Proposto.csv e Modelo Preditivo (Março/Abril 2026)
# ==============================================================================

import os
import pandas as pd
import numpy as np

print("--------------------------------------------------")
print("--- INICIANDO ETAPA 3: SIMULAÇÃO E PREVISÃO ---")
print("--------------------------------------------------")

# 1. Carregando base AHP
df_pdv = pd.read_csv('dpdvs_priorizados_ahp_tcc.csv', sep=';')

# 2. Construção do Calendário Dinâmico de Março e Abril/2026
dias_marco_abril = pd.date_range(start='2026-03-01', end='2026-04-30', freq='B')

registros_roteiro = []

for _, loja in df_pdv.iterrows():
    id_loja = loja['ID']
    tier = str(loja['Prioridade_Rota'])
    
    for data in dias_marco_abril:
        dia_mes = data.day
        dia_semana = data.weekday()
        semana_do_mes = (dia_mes - 1) // 7 + 1
        
        presenca = 0
        if 'Tier 1' in tier:
            if dia_semana == 0: # Frequência Semanal
                presenca = 1
        elif 'Tier 2' in tier:
            if dia_semana == 0 and semana_do_mes in [1, 3]: # Frequência Quinzenal
                presenca = 1
        else:
            if dia_semana == 0 and semana_do_mes == 1: # Frequência Mensal
                presenca = 1
                
        registros_roteiro.append({
            'Data': data.strftime('%Y-%m-%d'),
            'ID Loja': id_loja,
            'Presença Promotor': presenca
        })

df_roteiro_proposto = pd.DataFrame(registros_roteiro)
df_roteiro_proposto.to_csv('fRoteiro_Proposto.csv', index=False, sep=';')
print("✅ Tabela fato 'fRoteiro_Proposto.csv' gerada com sucesso!")

# 3. Modelo Preditivo de Vendas e Aplicação de Uplift
df_simulacao = df_roteiro_proposto.merge(df_pdv, left_on='ID Loja', right_on='ID', how='left')

# Escala diária por PDV
df_simulacao['Venda_Diaria_HW_Base'] = (df_simulacao['Fat_Hardware'] / 26.0) / 22.0
df_simulacao['Venda_Diaria_Sup_Base'] = (df_simulacao['Fat_Suprimento'] / 26.0) / 22.0

def calcular_venda_prevista(row):
    venda_hw = row['Venda_Diaria_HW_Base']
    venda_sup = row['Venda_Diaria_Sup_Base']
    presenca = row['Presença Promotor']
    
    if presenca == 1:
        venda_hw_pred = venda_hw * 1.15  # +15% em Hardware
        venda_sup_pred = venda_sup * 1.05  # +5% em Suprimentos
    else:
        venda_hw_pred = venda_hw
        venda_sup_pred = venda_sup
        
    return venda_hw_pred + venda_sup_pred

df_simulacao['Venda_Diaria_Baseline'] = df_simulacao['Venda_Diaria_HW_Base'] + df_simulacao['Venda_Diaria_Sup_Base']
df_simulacao['Venda_Diaria_Prevista'] = df_simulacao.apply(calcular_venda_prevista, axis=1)

df_simulacao[['Data', 'ID Loja', 'Presença Promotor', 'Venda_Diaria_Baseline', 'Venda_Diaria_Prevista']].to_csv('resultado_previsao_mar_abr_2026.csv', index=False, sep=';')
print("✅ Arquivo 'resultado_previsao_mar_abr_2026.csv' gerado!")