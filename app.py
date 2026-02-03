import streamlit as st

st.title('Переводчик схем')
st.subheader('Загрузи свою блок-схему, чтобы начать')

with st.sidebar:
    st.title ('Настройки')

    mode_name = st.selectbox('Выберите как расположена схема',
                        ['Сверху вниз', 'Слева направо'],
                        placeholder="Выберите вариант..." )
    
    file = st.file_uploader('Загрузи блок-схему в формате png', type='png')

if st.button('Загрузить данные'):
    if file:
        if mode_name == 'Сверху вниз':
            mode = 'up-down'
        elif file and mode_name == 'Слева направо':
            mode = 'left-right'
        
        
    else:
        st.write('Файл не загружен')