import streamlit as st
import requests
from io import BytesIO
import pandas as pd

st.title('Переводчик схем')
st.subheader('Загрузи свою блок-схему, чтобы начать')

with st.sidebar:
    st.title ('Настройки')

    mode_name = st.selectbox('Выберите как расположена схема',
                        ['Сверху вниз', 'Слева направо'],
                        placeholder="Выберите вариант..." )
    
    file = st.file_uploader('Загрузи блок-схему в формате png', type='png')

if st.button('Загрузить данные'):
    if file is None:
        st.error('Файл не загружен!')
        st.stop()
    
    if mode_name == 'Сверху вниз':
        mode = 'up-down'
    elif file and mode_name == 'Слева направо':
        mode = 'left-right'

    files = {
            'file': (file.name, file.getvalue(), 'image/png')
        }
    
    data = {
        'mode': mode
    }

    with st.spinner('Обработка схемы...'):
        try:
            response = requests.post(
                "http://api:8000/api/v1/analyze",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success("Обработка завершена!")
                
                st.download_button(
                    label="Скачать CSV",
                    data=response.content,
                    file_name=f"Description_{file.name.replace('.png', '')}.csv",
                    mime="text/csv"
                )
                
                st.subheader("Превью CSV:")
                csv_data = pd.read_csv(BytesIO(response.content))
                st.dataframe(csv_data, use_container_width=True)
                
            else:
                st.error(f"Ошибка сервера: {response.status_code}")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Не удалось подключиться к серверу. Убедитесь, что сервер запущен")