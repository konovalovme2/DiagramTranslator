import streamlit as st
import requests
from io import BytesIO, StringIO
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
    else:
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
                "http://host.docker.internal:8000/api/v1/analyze",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success("Обработка завершена!")
                
                blocks = result["data"]["blocks"]
                df = pd.DataFrame(blocks)
                
                if 'id' in df.columns and 'text' in df.columns:
                    df = df[['id', 'text']]
                    df.columns = ['Шаг', 'Действие']
                
                st.dataframe(df, use_container_width=True)
                
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False, encoding='utf-8')
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="Скачать как CSV",
                    data=csv_data,
                    file_name=f"flowchart_{file.name.replace('.png', '')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.error(f"Ошибка сервера: {response.status_code}")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Не удалось подключиться к серверу. Убедитесь, что сервер запущен. {str(e)}")