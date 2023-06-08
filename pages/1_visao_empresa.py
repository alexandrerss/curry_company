#importando bibiotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import folium as fl
import streamlit as st
import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon="💹", layout='wide')

# ---------------------------------
# FUNÇÃO LIMPEZA DOS DADOS
# ---------------------------------

def limpeza(df):
    """ Função para limpeza da base de dados """

    # Excluir as linhas com NAN
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Road_traffic_density'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Type_of_vehicle'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    # Comando para remover o texto de números - versao sem o FOR
    df.loc[:,"ID"] = df.loc[:,"ID"].str.strip()
    
    # Remover espaco da string
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    
    #Limpando a coluna de tempo
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )

    return(df)

# =================================
# FUNCOES DESTE MODULO
# =================================

def order_metric (df):
    colunas = ['ID', 'Order_Date']
    dados = df.loc[:,colunas].groupby('Order_Date').count().reset_index()
    # realizar o grafico
    figura = px.bar(dados, x='Order_Date', y='ID' )
    return figura 

def traffic_order_share(df):            
    auxiliar = df.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    auxiliar = auxiliar.loc[auxiliar['Road_traffic_density'] != 'NaN', :]
    auxiliar['entrega_percent'] = auxiliar['ID'] / auxiliar['ID'].sum()
    pizza = px.pie( auxiliar, values='entrega_percent', names='Road_traffic_density')
    return pizza

def traffic_order_city (df):
    df_aux = df.loc[:,['ID','City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density'] ).count().reset_index()
    bolha = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID')
    return bolha

def order_by_week (df):
    df['Week'] = df['Order_Date'].dt.strftime('%U')
    semana = df.loc[:,['ID', 'Week']].groupby('Week').count().reset_index()
    linha = px.line(semana, x='Week', y='ID' )
    return linha

def order_share_by_week (df):
    df_aux01  = df.loc[:,['ID','Week']].groupby('Week').count().reset_index()
    df_aux02 = df.loc[:,['Week','Delivery_person_ID']].groupby('Week').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    linhas = px.line(df_aux, x='Week', y='Order_by_delivery' )
    return linhas

def contry_maps (df):
    
    df_aux = df.loc[:, ['City', 'Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density'] ).median().reset_index()
    mapa = fl.Map()

    for index, location_info in df_aux.iterrows():
        fl.Marker( [location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']] ,popup=location_info[['City','Road_traffic_density']]).add_to( mapa )

    folium_static (mapa, width=1024, height=600)

# =================================
# INICIO
# =================================

#importar o arquivo csv
df1 = pd.read_csv('dataset/train.csv')

# Executando a limpeza (função)
df  = limpeza(df1)


# =================================
# BARRA LATERAL
# =================================

#image_path = ('D:/Comunidade_ds/repos/FTC/target.jpg')
image = Image.open('target.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', value = datetime.datetime(2022, 4, 13), min_value = datetime.datetime(2022, 2, 1), max_value = datetime.datetime(2022, 4, 6), format = 'DD-MM-YYYY' )
st.sidebar.markdown('''---''')

trafic_options = st.sidebar.multiselect('Quais as condições do transito?',['Low','Medium','High','Jam'],default=['Low','Medium','High','Jam'] )
st.sidebar.markdown('''---''')

#Filtro da data
linhas_selec = df['Order_Date'] < date_slider
df=df.loc[linhas_selec,:]

#Filtro do transito
linhas_selec = df['Road_traffic_density'].isin(trafic_options)
df=df.loc[linhas_selec,:]

 

# =================================
# LAYOUT - VISAO DO CLIENTE
# =================================

st.header('Marketplace - Visão do Cliente')

tab1, tab2, tab3, = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #1. Quantidade de pedidos por dia.
        st.markdown('# Quantidade de pedidos por dia')
        figura = order_metric (df)
        st.plotly_chart(figura, use_conteiner_width = True)
        
    with st.container():
        col1,col2 = st.columns(2)
        
        with col1:
            
            st.markdown('#### Por tipos de tráfego')
            pizza = traffic_order_share(df)  
            st.plotly_chart(pizza , use_container_width = True)
            
        with col2:
            st.markdown('#### Por ordem de cidades')
            bolha = traffic_order_city(df) 
            st.plotly_chart(bolha , use_container_width = True)

            
            
with tab2:
    with st.container():
        st.markdown('# Pedidos por semana')
        linhas = order_by_week (df)
        st.plotly_chart(linhas , use_container_width = True)
        
    with st.container():
        st.markdown('# Entregador por semana')
        linhas = order_share_by_week (df)
        st.plotly_chart(linhas , use_container_width = True)
            
with tab3:
    st.markdown('# Mapa')
    contry_maps(df)







    
    
