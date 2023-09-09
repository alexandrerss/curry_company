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

st.set_page_config (page_title="Visão Empresa", page_icon='📠', layout='wide') 

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

def pedidos_dia (df):
    diario = df.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(diario, x='Order_Date', y='ID', labels={'Order_Date':'Data', 'ID':'Quantidade de Pedidos'})
    fig.update_traces(marker_color = 'blue', marker_line_color = 'black', marker_line_width = 1, opacity = 1)
    
    return fig
  
def dist_trafego (df):
        
    trafego = df.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    trafego['percent_entregas'] = trafego['ID'] / trafego['ID'].sum()
    fig = px.pie(trafego, values='percent_entregas', names='Road_traffic_density', labels={'percent_entregas':'Percentual de Entregas', 'Road_traffic_density':'Densidade de Trafego'}, hole = 0.5)
    fig.update_traces(marker = dict(line = dict(color = 'black', width = 1)))
    
    return fig
  
def volume_trafego (df):
    volume = df.loc[:,['ID','Road_traffic_density','City']].groupby(['City','Road_traffic_density']).count().reset_index()
    fig = px.scatter(volume,x='City', y='Road_traffic_density', size='ID', color='City', labels={'City':'Cidade', 'Road_traffic_density':'Densidade de Trafego', 'ID' : 'Quantidade de Pedidos'})
    
    return fig

def pedidos_semana(df):
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
    semana = df.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(semana, x='week_of_year', y='ID', labels={'week_of_year':'Semana do Ano', 'ID':'Quantidade de Pedidos'})

    return fig
  
def entregador_semana (df):
    # Quantidade de pedidos por semana / Número Unico de entregadores por semana
    var01 = df.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index() # pedidos da semana
    var02 = df.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index() # Quant de entregadores da semana
    #Realizando o merge das variaveis
    aux = pd.merge(var01,var02,how='inner')
    aux['order_by_deliver'] = aux['ID'] / aux['Delivery_person_ID']
    fig = px.line( aux, x='week_of_year', y='order_by_deliver', labels={'week_of_year':'Semana do Ano', 'order_by_deliver':'Pedidos por Semana'},markers = True)
    fig.update_traces(line = dict(width = 4, color = "blue"),marker = dict(color = "red", size = 10, opacity = 0.7))
        
    return fig

def mapa_local (df): 
    localiza = df.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    mapa = folium.Map( zoom_start=11 )    
    for index, location_info in localiza.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( mapa )
    folium_static (mapa, width=1026, height=600)
    
    return None

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


                    
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('## Quantidade de pedidos por dia')
        fig = pedidos_dia (df)
        st.plotly_chart(fig,use_container_width=True)
        
        
    with st.container():
      col1, col2 = st.columns(2)
      
      with col1:
        st.markdown('Distribuição dos pedidos por tipo de tráfego')
        fig = dist_trafego (df)
        st.plotly_chart(fig,use_container_width=True)     
        
      with col2:
        st.markdown('Volume de pedidos por cidade e tipo de tráfego')
        fig = volume_trafego (df)
        st.plotly_chart(fig,use_container_width=True)

                  
with tab2:
    with st.container():  
        st.markdown('## Pedidos por semana')
        fig = pedidos_semana (df)
        st.plotly_chart(fig,use_container_width=True)     
  
    with st.container():  
        st.markdown('## Pedidos de entregador por semana') 
        fig = entregador_semana (df)
        st.plotly_chart(fig,use_container_width=True)
          
          
with tab3:
    st.markdown('## Mapa com localizações')
    mapa_local (df)

