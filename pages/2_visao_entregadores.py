# ==============================================================================
# IMPORTAR BIBLIOTECAS
# ==============================================================================
import pandas as pd
import numpy as np
import re
import plotly.express as px
import folium
import streamlit as st
import datetime as dt
import streamlit.components.v1 as components
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config (page_title="Visão Entregadores", page_icon='🚲', layout='wide' ) 

# ==============================================================================
# FUNÇÕES 
# ==============================================================================

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

def entregadores (df, ordem):
    df2 = ( df.loc[:, ['Delivery_person_ID','City','Time_taken(min)' ]]
           .groupby(['City','Delivery_person_ID'])
           .mean ()
           .sort_values(['City','Time_taken(min)'], ascending = ordem ).reset_index() )             
    aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    aux2 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    aux3 = df2.loc[df2['City'] == 'Urban', :].head(10)   
    df3 = pd.concat( [aux1,aux2,aux3] ).reset_index(drop=True)
    return df3

# ==============================================================================
# IMPORTAR DATASETS 
# ==============================================================================

df = pd.read_csv("datasets/train.csv")

# limpeza dos dados
df = limpeza (df)

# ==============================================================================
# BARRA LATERAL - SIDEBAR
# ==============================================================================
st.header('Marketplace - Visão do Cliente')

image = Image.open ('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown(' # Indian Curry Company ')
st.sidebar.markdown(' ### A sua comida mais rápida e aonde você quiser bem quentinha! ')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Qual seria a data limite?')

data_limite = st.sidebar.slider('Data Limite', 
                                value = dt.datetime(2022, 4, 13), 
                                min_value = dt.datetime(2022, 2, 11), 
                                max_value = dt.datetime(2022, 4, 6), 
                                format = 'DD-MM-YYYY' )

st.sidebar.markdown('''---''')

opt_trafego = st.sidebar.multiselect('Quais as condições do transito?',
                                     ['Low','Medium','High','Jam'],
                                     default=['Low','Medium','High','Jam'] )
st.sidebar.markdown('''---''')

st.sidebar.markdown('### Powered by Alexadrerss© 🌎🎓📊') 
with st.sidebar:
    components.html("""
                    <div class="badge-base LI-profile-badge" data-locale="en_US" data-size="large" data-theme="light" data-type="VERTICAL" data-vanity="alexandrerss" data-version="v1"><a class="badge-base__link LI-simple-link" href=https://www.linkedin.com/in/alexandrerss/"></a></div>
                    <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>              
              """, height= 310)


# Filtro de DATA
linhas_selec = df['Order_Date'] < data_limite
df = df.loc[linhas_selec, :]

# Filtro de DENSIDADE DE TRANSITO
linhas_selec = df['Road_traffic_density'].isin(opt_trafego)
df = df.loc[linhas_selec, :]

# ==============================================================================
# LAYOUT DA PAGINA
# ==============================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-','-'])

with tab1:
    with st.container():
        st.title('Métricas dos Entregadores')
        col1, col2,col3,col4 = st.columns(4, gap='large')
        with col1:
            st.markdown('Entregador mais velho')
            velho = df.loc[:,'Delivery_person_Age'].max()
            col1.metric("Idade", velho)
            
        with col2:
            st.markdown('Entregador mais novo')
            novo = df.loc[:,'Delivery_person_Age'].min()
            col2.metric("Idade", novo)
            
        with col3:
            st.markdown('Melhor condição de veículos')
            melhor = df.loc[:,'Vehicle_condition'].max()
            col3.metric("Nota", melhor)
            
        with col4:
            st.markdown('Pior condição de veículos')
            pior = df.loc[:,'Vehicle_condition'].min()
            col4.metric("Nota", pior)
            
    with st.container():
        st.markdown('''---''')
        st.title('Avaliações dos Entregadores')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Avaliação média por entregador')
            aval_media = df.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe (aval_media)
            
        with col2:
            st.markdown('Avaliação média por transito')
            aval_trafego = df.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings' : ['mean','std']})
            aval_trafego.columns = ['Média','Desvio_Padrão']
            st.dataframe (aval_trafego)
            
            st.markdown('Avaliação média por clima')
            aval_clima = df.loc[:,['Weatherconditions', 'Delivery_person_Ratings']].groupby('Weatherconditions').agg({'Delivery_person_Ratings' : ['mean','std']})
            aval_clima.columns = ['Média','Desvio_Padrão']
            st.dataframe (aval_clima)
                      
            
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade das Entregas')  
                
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Entregadores mais rápidos')
            df3 = entregadores (df, ordem=True)
            st.dataframe (df3)
            
        with col2:
            st.markdown('Entregadores mais Lentos')
            df3 = entregadores (df, ordem=False)
            st.dataframe (df3)
            

            

