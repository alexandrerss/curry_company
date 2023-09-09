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
from haversine import haversine
import plotly.graph_objects as go

st.set_page_config (page_title="Visão Restaurantes", page_icon='🍲', layout='wide' ) 

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

def distancia (df):
    colunas=['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']   
    df['distancia']= df.loc[:,colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1 )
    media = np.round(df['distancia'].mean(),2)
    return media

def com_festival (df,festival,op):
    festa = df.loc[:,['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean','std']})     
    festa.columns = ['Média','Desvio_Padrão']
    festa=festa.reset_index()
    festa=np.round(festa.loc[festa['Festival']==festival,op],2)   
    return festa

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
        st.title('Métricas dos Restaurantes')
        col1, col2,col3,col4,col5,col6 = st.columns(6)
        
        with col1:
            unico = df.loc[:,'Delivery_person_ID'].nunique()
            col1.metric("Entregadores", unico)
            
        with col2:
            media = distancia(df)
            col2.metric("Distância Média", media)  
            
        with col3:
            festa = com_festival (df, 'Yes', 'Média')
            col3.metric("Média com Festival", festa)
            
        with col4:
            festa = com_festival (df, 'Yes', 'Desvio_Padrão')
            col4.metric("Média com Festival", festa)
            
        with col5:
            festa = com_festival (df, 'No', 'Média')
            col5.metric("Média sem Festival", festa)
            
        with col6:
            festa = com_festival (df, 'No', 'Desvio_Padrão')
            col6.metric("STD sem Festival", festa)
            
    with st.container():    
        st.markdown("""---""")
        st.title('Tempo Médio e Desvio Padrão') 
        col1, col2 = st.columns(2)
            
        with col1: 
            cidades = df.loc[:,['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)' : ['mean','std']})
            cidades.columns = ['Média','Desvio_Padrão']
            cidades=cidades.reset_index()
            fig=go.Figure()
            fig.add_trace(go.Bar(name='Control', x=cidades['City'], y=cidades['Média'], error_y=dict(type='data', array=cidades['Desvio_Padrão'])))
            fig.update_layout(barmode='group')
            fig.update_traces(marker_color = 'magenta', marker_line_color = 'black', marker_line_width = 1, opacity = 1)
            st.plotly_chart(fig,use_container_width = True)
            
        with col2: 
            tabela = df.loc[:,['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)' : ['mean','std']})
            tabela.columns = ['Média','Desvio_Padrão']
            tabela=tabela.reset_index()  
            st.dataframe(tabela)     

            
    with st.container():    
        st.markdown("""---""")
        st.title('Distrubuição do Tempo')   
        col1, col2 = st.columns(2)
            
        with col1: 
            colunas=['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df['distancia']= df.loc[:,colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1 )
            media = df.loc[:, ['City', 'distancia']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=media['City'], values=media['distancia'], pull=[0, 0.1, 0], opacity=0.75)])
            fig.update_traces(marker = dict(line = dict(color = 'black', width = 2)))
            st.plotly_chart(fig,use_container_width = True)
            
        with col2: 
            tipo = df.loc[:,['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)' : ['mean','std']})
            tipo.columns = ['Média','Desvio_Padrão']
            tipo = tipo.reset_index()
            fig = px.sunburst(tipo, path=['City', 'Road_traffic_density'], values='Média', color='Desvio_Padrão', color_continuous_scale='BuPu',
                            color_continuous_midpoint=np.average(tipo['Desvio_Padrão']))
            st.plotly_chart(fig,use_container_width = True)
        
            

        
            