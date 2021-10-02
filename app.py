# importar bibliotecas
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

dataset='https://raw.githubusercontent.com/maiaufrrj/superstore_data/main/superstore_dataset2011-2015.csv'
geolink='https://raw.githubusercontent.com/albertyw/avenews/master/old/data/average-latitude-longitude-countries.csv'
 
@st.cache #ajuda a criar um cache pra acelerar o carregamento dos dados
def load_data():
    """
    Carrega os dados de disponíveis no GitHub
 
    :return: DataFrame com colunas selecionadas.
    """
    columns = {'Row ID':'id_linha',
               'Order ID': 'id_pedido', 
               'Order Date': 'data_pedido',
               'Ship Date': 'data_envio',
               'Ship Mode': 'modalidade_frete',
               'Customer ID': 'id_cliente',
               'Customer Name': 'cliente',
               'Segment': 'segmento',
               'City': 'cidade',
               'State': 'estado',
               'Country': 'país',
               'Postal Code': 'cod_postal',
               'Market': 'mercado',
               'Region': 'regiao',
               'Product ID': 'id_produto',
               'Category': 'categoria_produto',
               'Sub-Category': 'subcategoria_produto',
               'Product Name': 'produto',
               'Sales': 'vendas',
               'Quantity': 'quantidade',
               'Discount': 'desconto',
               'Profit': 'lucro',
               'Shipping Cost': 'custo_envio',
               'Order Priority': 'prioridade'
               }
    
    df = pd.read_csv(dataset, encoding= 'unicode_escape')
    df=df.rename(columns=columns)
    geo_data = pd.read_csv(geolink, encoding= 'unicode_escape')
    
    geo_dict = {'Country': 'país',
             'Latitude': 'latitude',
             'Longitude': 'longitude'}

    #trocando nomes das colunas e selecionando coluna de índice
    geo_data=geo_data.rename(columns=geo_dict).set_index('país')
    del geo_data['ISO 3166 Country Code']
    df = pd.merge(df, geo_data, 
                      on ='país', 
                      how ='inner') 
    pd.set_option('display.precision', 2)
    
    df['ano'] = pd.DatetimeIndex(df['data_pedido']).year
    df['mês'] = pd.DatetimeIndex(df['data_pedido']).month
    #df['data_pedido'] = pd.to_datetime(df['data_pedido'].dt.strftime('%d-%m-%Y'), infer_datetime_format=True)
    #df['data_envio'] = pd.to_datetime(df['data_envio'].dt.strftime('%d-%m-%Y'), infer_datetime_format=True)
    
    df['data_pedido'] = pd.to_datetime(df['data_pedido'], format='%d-%m-%Y', infer_datetime_format=True)
    df['data_envio'] = pd.to_datetime(df['data_envio'], format='%d-%m-%Y', infer_datetime_format=True)
    df['lucro_unitário'] = df['lucro'] / df['quantidade']
    df['tempo_preparação'] = df['data_envio'] - df['data_pedido']
    df=df.set_index('id_pedido')
    return df
 
# carregar os dados
df = load_data()
label_mercado = df.mercado.unique().tolist()
label_segmento = df.segmento.unique().tolist()

# SIDEBAR
# Parâmetros e número de ocorrências
st.sidebar.header("Parâmetros")
info_sidebar = st.sidebar.empty()    # placeholder, para informações filtradas que só serão carregadas depois
 
# Slider de seleção do ano
st.sidebar.subheader("Ano")
year_to_filter = st.sidebar.slider('Escolha o ano desejado', 2011, 2014)

# Checkbox da Tabela
st.sidebar.subheader("Tabela")
tabela = st.sidebar.empty()    # placeholder que só vai ser carregado com o df_filtrado
 
# Multiselect com os labels
label_to_filter_mercado = st.sidebar.multiselect(
    label="Selecione o Mercado",
    options=label_mercado,
    default=["Africa", 'APAC', 'EMEA', 'EU','US', 'LATAM', 'Canada' ]
)

label_to_filter_segmento= st.sidebar.multiselect(
    label="Selecione o Segmento",
    options=label_segmento,
    default=["Home Office", 'Consumer', 'Corporate']
)




# Informação no rodapé da Sidebar
st.sidebar.markdown("""
A base de dados utilizada está disponível no ***Kaggle***.
""")
 
# Somente aqui os dados filtrados por ano são atualizados em novo dataframe
df_filtrado = df[(df['data_pedido'].dt.year == year_to_filter) & 
                 (df.mercado.isin(label_to_filter_mercado)) & 
                 (df.segmento.isin(label_to_filter_segmento))]
 
# Aqui o placehoder vazio finalmente é atualizado com dados do df_filtrado
info_sidebar.info("{} ocorrências selecionadas.".format(df_filtrado.shape[0]))


# MAIN
st.title("AliPaga")
st.markdown(f"""
            Estão sendo exibidas as ocorrências classificadas como **{", ".join(label_to_filter_mercado)}**
            para o ano de **{year_to_filter}**.
            """)
 
# raw data (tabela) dependente do checkbox
if tabela.checkbox("Mostrar tabela de dados"):
    st.write(df_filtrado)
 
 
# mapa
st.subheader("Mapa")
st.map(df_filtrado)

#gráficos de dispersão
fig1 = px.scatter(df_filtrado, x='custo_envio', y='lucro', color='mercado')
st.plotly_chart(fig1)

fig2 = px.scatter(df_filtrado, x='vendas', y='lucro', color='categoria_produto')


fig3 = px.scatter_matrix(df_filtrado,
    dimensions=["custo_envio", "lucro", "vendas", 'desconto'],
    color='categoria_produto')
#fig.show()
st.plotly_chart(fig3)

#matriz de correlação
#fig4, ax = plt.subplots()
#ax = sns.heatmap(df_filtrado)
#st.pyplot(fig4)

corr = df_filtrado[['custo_envio','lucro','vendas','desconto','quantidade']].corr()

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=bool))

# Set up the matplotlib figure
fig4, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0, vmin=-.3,
            square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True)

st.pyplot(fig4)
