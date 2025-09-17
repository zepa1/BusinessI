import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('consulta.csv', sep =';', encoding='utf-8')
df = df.replace('-', '0')
st.title('Visualização dos Dados Econômicos')
st.write('Fonte: consulta.csv')

# Exibir tabela completa
st.subheader('Tabela de Dados')
st.dataframe(df)

# Seleção de localidade
localidades = df['Localidade'].unique()
localidade = st.selectbox('Selecione a localidade:', localidades)
df_local = df[df['Localidade'] == localidade]

# Seleção de variável
variaveis = df['Variável'].unique()
variavel = st.selectbox('Selecione a variável:', variaveis)
df_var = df_local[df_local['Variável'] == variavel]

# Preparar dados para gráfico
anos = df.columns[2:]
valores = df_var.iloc[0, 2:].str.replace('.', '').str.replace(',', '.').astype(float)

# Exibir gráfico
st.subheader(f'Evolução de {variavel} em {localidade}')
fig, ax = plt.subplots()
ax.plot(anos, valores, marker='o')
ax.set_xlabel('Ano')
ax.set_ylabel(variavel)
ax.set_title(f'{variavel} - {localidade}')
plt.xticks(rotation=45)
st.pyplot(fig)
