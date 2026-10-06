# ==============================================================================
# TCC - ROTEIRIZAÇÃO INTELIGENTE EM TRADE MARKETING
# Script 2: Matriz de Saaty 4x4, Teste de Consistência (CR) e Tiers de Rota
# ==============================================================================

import os
import pandas as pd
import numpy as np

print("--------------------------------------------------")
print("--- INICIANDO ETAPA 2: MODELAGEM AHP ---")
print("--------------------------------------------------")

# 1. Carregando a base com o Score da PCA
df_pdv = pd.read_csv('dpdvs_score_pca.csv', sep=';')

# 2. Definição da Matriz de Comparação Par a Par (Escala de Saaty)
criterios = ['Potencial_PCA', 'Vendas_Hardware', 'Canal_Trade', 'Historico_Visitas']

matriz_saaty = np.array([
    [1.0,   2.0,   5.0,   7.0],   # Potencial_PCA
    [1/2,   1.0,   4.0,   6.0],   # Vendas_Hardware
    [1/5,   1/4,   1.0,   3.0],   # Canal_Trade
    [1/7,   1/6,   1/3,   1.0]    # Historico_Visitas
])

# 3. Normalização e Vetor Próprio de Pesos
soma_colunas = matriz_saaty.sum(axis=0)
matriz_normalizada = matriz_saaty / soma_colunas
pesos_criterios = matriz_normalizada.mean(axis=1)

# 4. Teste de Consistência Matemática (CR)
vetor_ponderado = np.dot(matriz_saaty, pesos_criterios)
lambda_max = np.mean(vetor_ponderado / pesos_criterios)
n = len(criterios)
CI = (lambda_max - n) / (n - 1)
RI = 0.90 # Para n = 4
CR = CI / RI

print(f"✅ Lambda Máximo (λ_max): {lambda_max:.4f}")
print(f"✅ Razão de Consistência (CR): {CR*100:.2f}%")

# 5. Aplicação dos Pesos nos PDVs (Pontuação Ponderada)
df_ahp = df_pdv.copy()

# Min-Max Scaling
score_min, score_max = df_ahp['Score_PCA_Potencial'].min(), df_ahp['Score_PCA_Potencial'].max()
df_ahp['C1_Potencial'] = (df_ahp['Score_PCA_Potencial'] - score_min) / (score_max - score_min)

fat_hw_max = df_ahp['Fat_Hardware'].max()
df_ahp['C2_Hardware'] = df_ahp['Fat_Hardware'] / fat_hw_max if fat_hw_max > 0 else 0

df_ahp['C3_Canal'] = df_ahp['Canal Trade'].apply(lambda x: 1.0 if 'Marco' in str(x) else 0.2)

vis_min, vis_max = df_ahp['Total_Visitas'].min(), df_ahp['Total_Visitas'].max()
df_ahp['C4_Visitas'] = (df_ahp['Total_Visitas'] - vis_min) / (vis_max - vis_min) if vis_max > vis_min else 0

# Score Final AHP
df_ahp['Score_AHP_Final'] = (
    df_ahp['C1_Potencial'] * pesos_criterios[0] +
    df_ahp['C2_Hardware']  * pesos_criterios[1] +
    df_ahp['C3_Canal']     * pesos_criterios[2] +
    df_ahp['C4_Visitas']   * pesos_criterios[3]
)

# Categorização em Tiers
df_ahp['Prioridade_Rota'] = pd.qcut(
    df_ahp['Score_AHP_Final'], 
    q=[0, 0.40, 0.80, 1.0], 
    labels=['Tier 3 - Baixa', 'Tier 2 - Média', 'Tier 1 - Alta']
)

df_ahp_ranking = df_ahp.sort_values(by='Score_AHP_Final', ascending=False)
df_ahp_ranking.to_csv('dpdvs_priorizados_ahp_tcc.csv', index=False, sep=';')
print("✅ Tabela 'pdvs_priorizados_ahp_tcc.csv' exportada com sucesso!")