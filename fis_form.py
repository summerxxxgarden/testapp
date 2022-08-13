import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

data1=[]

for p in range(1,6):
    url=f'https://fis51.ru/catalog/2?page={p}#top'
    r=requests.get(url)
    soup=BeautifulSoup(r.text,'lxml')
    frond_doors=soup.findAll('div', class_='col-xl-4 col-lg-6 col-md-6 col-12 doors_list_item doors_list_item_2')

    for frond_door in frond_doors:
        frond_door_id = int(frond_door.find('a').get('href')[-3:].replace('/',''))
        frond_door_title = frond_door.find('strong').text
        data1.append([frond_door_id,frond_door_title])
        
df1 = pd.DataFrame(data1)
door_ids=list(df1[0])

data2=[]

for door_id in door_ids:
    url=f'https://fis51.ru/item/{door_id}'
    r=requests.get(url)
    soup=BeautifulSoup(r.text,'lxml')

    door_description=soup.find('div', id='dop_parm').text
    door_id_item=door_id
    
    data2.append([door_id_item,door_description])
    
df2=pd.DataFrame(data2)

df1.columns=['id','title1']
df2.columns=['id','description']

df_description=df1.merge(df2,how='left',on='id')
df_description
