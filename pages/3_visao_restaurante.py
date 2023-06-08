#importando bibiotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import folium as fl
import streamlit as st
import numpy as np
import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon="🍲", layout='wide')

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

def avg_std_time_on_traffic (df):  
        
    cols= ['City','Time_taken(min)','Road_traffic_density']
    df_aux = df.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['Media','Desvio_Padrao']
    df_aux = df_aux.reset_index()
            
    fig=px.sunburst(df_aux, path=['City','Road_traffic_density'], values='Media', 
                     color='Desvio_Padrao', color_continuous_scale='RdBu',
                     color_continuous_midpoint=np.average(df_aux['Desvio_Padrao']))
    
    
    return fig    

def avg_std_time_graph (df):
    df_aux = df.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['Media','Desvio_Padrao']
    df_aux = df_aux.reset_index()    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['Media'],error_y=dict(type='data', array=df_aux['Desvio_Padrao'] )))                       
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery (df,festival,op):
        df_aux = df.loc[:,['Time_taken(min)','Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
        df_aux.columns = ['Media','Desvio_Padrao']
        df_aux = df_aux.reset_index()
        df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2  )
        return df_aux

def distance(df, fig):
    if fig == False:
        colunas = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df['distancia']= df.loc[:,colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1 )
        media = np.round(df['distancia'].mean(),2)
        return media
            
    else:
        colunas = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df['distancia']= df.loc[:,colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1 )
        media = df.loc[:,['City','distancia']].groupby(['City']).mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=media['City'], values=media['distancia'], pull=[0,0.1,0])])
        return fig   
       

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
# LAYOUT - VISAO DOS RESTAURANTES
# =================================

st.header('Marketplace - Visão dos Restaurantes')

tab1, tab2, tab3, = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4, col5, col6 =  st.columns(6)
        with col1:
            st.markdown('##### Entregadores Únicos')
            delivery_unico = len(df.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Únicos',delivery_unico)
            
        with col2:
            st.markdown('##### Distância Média')
            media = distance (df, fig=False)
            col2.metric('Média',media)          
            
        with col3:
            st.markdown('##### Média com Festival')
            df_aux = avg_std_time_delivery(df,'Yes','Media')
            col3.metric('Com Festival', df_aux)
             
        with col4:
            st.markdown('##### DV com Festival')
            df_aux = avg_std_time_delivery(df,'Yes','Desvio_Padrao')
            col4.metric('Com Festival', df_aux)
            
        with col5:
            st.markdown('##### Média Sem Festival')
            df_aux = avg_std_time_delivery(df,'No','Media')     
            col5.metric('Sem Festival', df_aux)
            
        with col6:
            st.markdown('##### DV sem Festival')
            df_aux = avg_std_time_delivery(df,'No','Desvio_Padrao')
            col6.metric('Sem Festival', df_aux)
                        
                
    with st.container():
        st.markdown('''---''')

        coluna1, coluna2 =  st.columns(2)

        with coluna1:
            st.markdown('Média e Desvio Padrão')
            fig = avg_std_time_graph (df)
            st.plotly_chart(fig, use_container_width = True)

        with coluna2:
            st.markdown('Distribuião do Distância')
            df_aux = df.loc[:,['City','Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
            df_aux.columns = ['Media','Desvio_Padrao']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do Tempo')

        coluna1, coluna2 =  st.columns(2)
        
        with coluna1:
            
            st.markdown('Tempo media de entrega por cidade')
            fig = distance(df,fig=True)
            st.plotly_chart(fig, use_container_width = True)
            
        with coluna2:
            st.markdown('Cidade e Tráfego')             
            fig = avg_std_time_on_traffic (df)
            st.plotly_chart(fig, use_container_width = True)



