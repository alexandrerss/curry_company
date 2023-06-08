#importando bibiotecas
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home",page_icon="🎲", layout='wide')

#image_path = 'D:\\Comunidade_ds\\repos\\FTC\\'
image = Image.open('target.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.write ('# Curry Company Growth Dashboard')


st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar este Dashboard ?
    - Visão Empresa:
        - Visão Gerencial : Metricas Gerais de comportamento.
        - Visão Tática : Indicadores semanais de crescimento.
        - Visão Geográfica : Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes

    ### Duvidas ?
    - alexandrerss@yahoo.com.br
""")
