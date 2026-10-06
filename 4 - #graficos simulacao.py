# ==============================================================================
# TCC - ROTEIRIZAÇÃO INTELIGENTE EM TRADE MARKETING
# Script 4: Geração do Painel Gráfico Visual (Estudo de Caso Loja MG-UBE)
# ==============================================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

print("--------------------------------------------------")
print("--- GERANDO FIGURA DO ESTUDO DE CASO (MG-UBE) ---")
print("--------------------------------------------------")

df_diario = pd.read_csv('resultado_previsao_mar_abr_2026.csv', sep=';')
df_ahp = pd.read_csv('pdvs_priorizados_ahp_tcc.csv', sep=';')

df_diario['Data_DT'] = pd.to_datetime(df_diario['Data'])
df_diario = df_diario.sort_values(by='Data_DT')
df_diario = df_diario.merge(df_ahp[['ID', 'Prioridade_Rota', 'Loja']], left_on='ID Loja', right_on='ID', how='left')

# Seleção da Loja MG-UBE (Tier 1)
id_loja_exemplo = df_ahp[df_ahp['Prioridade_Rota'] == 'Tier 1 - Alta']['ID'].iloc[0]
nome_loja = df_ahp[df_ahp['ID'] == id_loja_exemplo]['Loja'].values[0]

df_loja = df_diario[(df_diario['ID Loja'] == id_loja_exemplo) & (df_diario['Data_DT'] >= '2026-03-01') & (df_diario['Data_DT'] <= '2026-03-31')].copy()

# Simulação das visitas do Baseline (2 visitas esporádicas no mês)
np.random.seed(42)
df_loja['Presenca_Baseline'] = np.random.choice([0, 1], size=len(df_loja), p=[0.88, 0.12])

df_loja['Venda_Baseline_Com_Visita'] = df_loja.apply(
    lambda r: r['Venda_Diaria_Baseline'] * 1.12 if r['Presenca_Baseline'] == 1 else r['Venda_Diaria_Baseline'], axis=1
)

df_loja['Data_Str'] = df_loja['Data_DT'].dt.strftime('%d/%b')
x_labels = df_loja['Data_Str'].values
x_pos = np.arange(len(x_labels))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7.5))

fig.suptitle(f'TCC - Estudo de Caso no PDV: {nome_loja} (Tier 1 - Alta Prioridade)\nSimulação de Desempenho e Cobertura de Rotas em Março/2026', 
             fontsize=15, fontweight='bold', y=0.98)

# Painel 1: Linha de Tempo Diária
line1 = ax1.plot(x_pos, df_loja['Venda_Baseline_Com_Visita'], label='Venda Diária (Baseline)', color='#7f8c8d', linestyle='--', linewidth=2, marker='o')
line2 = ax1.plot(x_pos, df_loja['Venda_Diaria_Prevista'], label='Venda Diária (Modelo Proposto)', color='#27ae60', linewidth=2.5, marker='s')

ax1.set_title('1. Impacto Diário da Presença do Promotor nas Vendas', fontsize=12, fontweight='bold', pad=15)
ax1.set_ylabel('Venda Diária Prevista (R$)', fontsize=10, fontweight='bold', color='#1e8449')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)

ax1_visitas = ax1.twinx()
bar_width = 0.35
rects_v1 = ax1_visitas.bar(x_pos - bar_width/2, df_loja['Presenca_Baseline'], width=bar_width, alpha=0.35, color='#7f8c8d', label='Visita Realizada (Baseline)')
rects_v2 = ax1_visitas.bar(x_pos + bar_width/2, df_loja['Presença Promotor'], width=bar_width, alpha=0.6, color='#27ae60', label='Visita Agendada (Modelo Proposto)')

ax1_visitas.set_ylabel('Presença do Promotor (1 = Visita / 0 = Sem Visita)', fontsize=9, color='#2c3e50')
ax1_visitas.set_ylim(0, 3.5)
ax1_visitas.set_yticks([0, 1])
ax1_visitas.grid(False)

lines_labels = [line[0] for line in [line1, line2]] + [rects_v1, rects_v2]
labels = [l.get_label() for l in lines_labels]
ax1.legend(lines_labels, labels, loc='upper left', frameon=True, fontsize=8)

# Painel 2: Consolidado Mensal
fat_total_base = df_loja['Venda_Baseline_Com_Visita'].sum()
fat_total_prop = df_loja['Venda_Diaria_Prevista'].sum()
vis_total_base = int(df_loja['Presenca_Baseline'].sum())
vis_total_prop = int(df_loja['Presença Promotor'].sum())

cats = ['Planejamento\nConvencional (Baseline)', 'Modelo Proposto\n(PCA + AHP)']
faturamentos = [fat_total_base / 1000, fat_total_prop / 1000]

x_cats = np.arange(len(cats))
width_c = 0.4

bars_fat = ax2.bar(x_cats - width_c/2, faturamentos, width=width_c, color=['#95a5a6', '#27ae60'], label='Faturamento Acumulado (R$ Mil)')

ax2.set_title('2. Faturamento Total vs. Frequência de Visitas no Mês', fontsize=12, fontweight='bold', pad=15)
ax2.set_ylabel('Faturamento Total Mensal (R$ Mil)', fontsize=10, fontweight='bold', color='#2c3e50')
ax2.set_xticks(x_cats)
ax2.set_xticklabels(cats, fontweight='bold', fontsize=10)
ax2.set_ylim(0, max(faturamentos) * 1.25)

for bar in bars_fat:
    height = bar.get_height()
    ax2.annotate(f'R$ {height:.1f}k',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax2_vis = ax2.twinx()
visitas = [vis_total_base, vis_total_prop]
bars_vis = ax2_vis.bar(x_cats + width_c/2, visitas, width=width_c, color=['#7f8c8d', '#1e8449'], alpha=0.85, label='Qtd. Total de Visitas')

ax2_vis.set_ylabel('Quantidade de Visitas no Mês', fontsize=10, fontweight='bold', color='#1e8449')
ax2_vis.set_ylim(0, max(visitas) * 1.5)
ax2_vis.set_yticks(range(0, max(visitas) + 3))
ax2_vis.grid(False)

for bar in bars_vis:
    height = bar.get_height()
    ax2_vis.annotate(f'{int(height)} visitas',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e8449')

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_vis.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=8)

plt.tight_layout(rect=[0, 0.02, 1, 0.95])
plt.savefig('graficos_simulacao_tcc.png', dpi=300, bbox_inches='tight')
print("✅ Painel 'graficos_simulacao_tcc.png' gerado com sucesso!")