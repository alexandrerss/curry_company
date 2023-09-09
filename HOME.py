import streamlit as st
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title='HOME', page_icon="🌀")

#image_path = 'C:/Comunidade_DS/repos/FTC/curry_company/'

image = Image.open ('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown(' # Indian Curry Company ')
st.sidebar.markdown(' ### A sua comida mais rápida e aonde você quiser bem quentinha! ')
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Alexadrerss© 🌎🎓📊') 
with st.sidebar:
    components.html("""
                    <div class="badge-base LI-profile-badge" data-locale="en_US" data-size="large" data-theme="light" data-type="VERTICAL" data-vanity="alexandrerss" data-version="v1"><a class="badge-base__link LI-simple-link" href=https://www.linkedin.com/in/alexandrerss/"></a></div>
                    <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>              
              """, height= 310)

st.write ('# Curry Company Dashboard')

st.markdown(
    """
    Criado para a visualização de métricas dos entregadores e restaurantes cadastrados.
    #### Como Utilizar?
    - Visão Empresa
        - Visão Gerencial : Métricas Gerais
        - Visão Tática : Indicadores semanais
        - Visão Geográfica : Geolocalização
    - Visão Entregador
        - Indicadores semanais
    - Visão Restaurantes
        - Indicadores semanais          
""")