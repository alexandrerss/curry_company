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

st.set_page_config( page_title='Visão Entregadores', page_icon="🚚", layout='wide')

# ---------------------------------
# FUNÇÕES
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

def top_delivers(df, top_asc):
    df2 = ( df.loc[:, ['Delivery_person_ID','City','Time_taken(min)', ]].groupby(['City','Delivery_person_ID']).mean ()    .sort_values(['City','Time_taken(min)'], ascending = top_asc ).reset_index() ) 
    aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    aux2 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    aux3 = df2.loc[df2['City'] == 'Urban', :].head(10)

    df3 = pd.concat( [aux1,aux2,aux3] ).reset_index(drop=True)
    return df3
 
# =================================
# INICIO
# =================================

#importar o arquivo csv
df1 = pd.read_csv('D:/Comunidade_ds/repos/FTC/dataset/train.csv')

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
# LAYOUT - VISAO DOS ENTREGADORES
# =================================

st.header('Marketplace - Visão dos Entregadores')

tab1, tab2, tab3, = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 =  st.columns(4, gap='large')
        
        with col1:
            st.subheader('Mais Velho') 
            maior = df.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior Idade',maior)
            
        with col2:
            st.subheader('Menor Idade') 
            menor = df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor Idade',menor)
            
        with col3:
            st.subheader('Melhor condição de Veículos')
            melhor = df.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição',melhor)
            
        with col4:
            st.subheader('Pior condição de Veículos')
            pior = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição',pior)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2, =  st.columns(2)
        with col1:
            st.markdown('#### Avaliações médias por entregador') 
            entregador = ( df.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']]
                          .groupby('Delivery_person_ID')
                          .mean().reset_index() )
            st.dataframe(entregador)
        with col2:
            st.markdown('#### Avaliações médias por trânsito') 
            trafego = ( df.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                       .groupby('Road_traffic_density')
                       .agg({'Delivery_person_Ratings' : ['mean','std']}))
            trafego.columns = ['media','desvio']
            st.dataframe(trafego)
            
            st.markdown('#### Avaliações médias por clima') 
            clima = ( df.loc[:, ['Delivery_person_Ratings','Weatherconditions']]
                     .groupby('Weatherconditions')
                     .agg({'Delivery_person_Ratings' : ['mean','std']}) )
            clima.columns = ['media','desvio']
            st.dataframe(clima)

    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de entrega')

        col1, col2, =  st.columns(2)
        with col1:
            st.subheader('Top Entregadores mais rápidos') 
            df3 = top_delivers (df, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.subheader('Top Entregadores mais lentos') 
            df3 = top_delivers (df, top_asc=False)
            st.dataframe(df3)

            
            
            
            
        
