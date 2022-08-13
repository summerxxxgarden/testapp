import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

st.title("Экспорт дверей с сайта fis51.ru")

@st.cache
def f_doors_export():
    data1=[]
    #получаем айдишники и названия дверей
    st.write("Начинаем работу")
    for p in range(1,6):
        url=f'https://fis51.ru/catalog/2?page={p}#top'
        r=requests.get(url)
        soup=BeautifulSoup(r.text,'lxml')
        frond_doors=soup.findAll('div', class_='col-xl-4 col-lg-6 col-md-6 col-12 doors_list_item doors_list_item_2')

        for frond_door in frond_doors:
            frond_door_id = int(frond_door.find('a').get('href')[-3:].replace('/',''))
            frond_door_title = frond_door.find('strong').text
            data1.append([frond_door_id,frond_door_title])
        st.write(f"Собраны данные со страницы №{p}")
            
    df1 = pd.DataFrame(data1)
    door_ids=list(df1[0])

    #получаем описания дверей 
    data2=[]
    st.write(f"Всего дверей - {len(door_ids)}")
    persentage_of_doors=0
    for door_id in door_ids:
        url=f'https://fis51.ru/item/{door_id}'
        r=requests.get(url)
        soup=BeautifulSoup(r.text,'lxml')

        door_description=soup.find('div', id='dop_parm').text
        door_id_item=door_id
        
        data2.append([door_id_item,door_description])
        persentage_of_doors+=door_id
        
    st.write("Подготовка данных")
    df2=pd.DataFrame(data2)

    df1.columns=['id','title1']
    df2.columns=['id','description']

    df_description=df1.merge(df2,how='left',on='id')
    st.write("Готово!")
    return df_description

@st.cache
def convert_df(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')

clicked_download=st.download_button(
    label="Download data as CSV",
    data=convert_df(f_doors_export()),
    file_name='экспорт дверей.csv',
    mime='text/csv',
)
