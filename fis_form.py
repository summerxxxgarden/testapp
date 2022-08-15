import streamlit as st

st.title("Импорт товаров с сайта gigi.ru")

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os,requests,vk_api

def main():
    
    print("Начинаем выгрузку товаров с сайта gigi.ru")

    data=[]

    for p in range(1,9):
        url=f'https://www.gigi.ru/vsya_produktsiya/?PAGEN_1={p}'

        r=requests.get(url)
        soup = BeautifulSoup(r.text,'lxml')

        products=soup.findAll('div', class_='bx_catalog_item')

        for product in products:
            title = product.find('div', class_='bx_catalog_item_title').find('a').get('title')
            price=product.find('div',class_='bx_catalog_item_price').find('div','bx_price').text[:7]
            pic=product.find('a',class_='bx_catalog_item_images').get('style')

    #является продуктом для косметологов
            try:
                prof_product=product.find('div','bx_price').find('div',class_='prod_only_cosmetolog').text
            except AttributeError:
                prof_product=False

    #Старая цена
            try:
                old_price=product.find('div','bx_price').find('span',class_='old_price').text
            except AttributeError:
                old_price=False

            data.append([title,price,prof_product,old_price,pic])


    columns=['title1','price12','prof_product','old_price','pic']
    df_kremy_antivozrastnye=pd.DataFrame(data, columns=columns)
    df_kremy_antivozrastnye.loc[:, 'category'] = 'Продукция GIGI'

    df=df_kremy_antivozrastnye
    df.drop_duplicates()

    def price1(x, y, z):
        if x==False and y == False:
            return z
        elif x=='товар доступен только для авторизованных косметологов' and y == False:
            return "товар доступен только для авторизованных косметологов"
        elif x==False and y !=False:
            return z

    df['price'] = df.apply(lambda x: price1(x['prof_product'], x['old_price'], x['price12']), axis =  1)

    df=df.drop_duplicates()
    df=df.drop(labels='price12', axis=1)
    df = df.loc[df['prof_product'] != 'товар доступен только для авторизованных косметологов']
    df = df.loc[df['price'] != ''].reset_index(drop=True)

    df_split1=df.title1.str.split(pat=' ', n=1, expand=True)
    df_split1.columns=['sku','title']
    df = pd.concat([df,df_split1], axis=1).drop(labels=['title1','prof_product'], axis=1).reindex(columns=['sku','title','price','old_price','pic','category'])

    df=df.replace('background-image: url\(\'','https://www.gigi.ru/',regex=True).replace('\'\)','',regex=True)
    df['price'] = df['price'].replace(' ','',regex=True).replace('руб','',regex=True).replace('р','',regex=True).astype('float')
    df['old_price'] = df['old_price'].replace(' ','',regex=True).replace('руб.','',regex=True).replace('р','',regex=True).astype('float')

    drop_sku = ['13000', '33000', '33003', '33004', '33008', '33006', '15244', '33154', '24070', '27116', '24006', '24008']

    df=df.loc[~df['sku'].isin(drop_sku)]

    idx=df[df['sku']=='27120-1'].index.values[0]

    df['price'][idx]=391
    df['title'][idx]='Салфетка-пилинг трехкислотная GIGI Acnon Triple Acid Rapid Wipe, 2 шт'

    print("Выгрузка с сайта закончена")
    
#авторизируемся в Вк через токен
    token="vk1.a.ArZr8sr5xVNPBq9__me_03WaMdJCq6I-gU0TP3GR1BXil6_jFRraTzoV1iHu58vLAeRdMAKS3ifNQsSnPE37iXuoIjEQ8SXVD26izi6qoZRZG-qKtBXpjAOXFa18CNDBxMpTTSdGMG0VqCR4syzmEsxaEdZ8VLlEWGoVJyHpl9FOjnWhXFTH8VNcb20Kr5Sl"
    vk_session = vk_api.VkApi(token=token)
    print("Авторизация Вк прошла успешно")
    
#получение товаров GiGi из подборки группы
    def get_market_byid(owner_id=-211848929,album_id=25,count=114):
        get_markets_albums = vk_session.method("market.get",{
                'owner_id':owner_id,
                'album_id':album_id,
                'count':count})
        return get_markets_albums
    
#добавление товаров GiGi в подборку
    def add_products_toalbum(item_ids, owner_id=-211848929,album_ids=25):
        products_toalbum = vk_session.method("market.addToAlbum",{
                'owner_id':owner_id,
                'album_ids':album_ids,
                'item_ids':item_ids})
        return products_toalbum

#удаление товаров по их id
    def delete_market(item_id,owner_id=-211848929):
        delete_markets = vk_session.method("market.delete",{
                'owner_id':owner_id,
                'item_id':item_id})
        return delete_markets

#получение подборок группы
    def get_albums(owner_id=-211848929):
        get_albums = vk_session.method("market.getAlbums",{
                'owner_id':owner_id})
        return get_albums
    
    j=get_market_byid()
    print("id товаров получены")
    l1=[]
    
    print("Удаление товаров")
    for i in range(j['count']):
        l1.append(j['items'][i]['id'])

    for i in range(len(l1)):
        delete_market(l1[i])
        print('.', end=' ')
    print("Товары успешно удалены")

#определяем функцию загрузки изображений, скачиваем файлы из списка, и сохраняем их названия в переменной filenames
    def download(url):
        get_response = requests.get(url,stream=True)
        file_name  = url.split("/")[-1]
        with open(file_name, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    fa=f.write(chunk)
    
    print()
    print('Начинаем скачивание изображений')
    l=list(df.pic)
    for i in l:
        download(i)
        print('.', end=' ')
    print()
    print('Изображения скачены')

    filenames=[]
    print('Формируеем список изображений')
    for i in l:
        filenames.append(i.split("/")[-1])
        print('.', end=' ')

#объявляем загрузчик фото
    upload = vk_api.VkUpload(vk_session)
    print()
    print('Загрузчик фото объявлен')

#загружаем фото и получаем их id в список main_photo_ids
    print("Начинается загрузка фото на сервер")
    main_photo_ids=[]
    photo_not_uploaded=[]
    photo_not_uploaded_id=[]
    for j in range(len(filenames)):
        try:
            photo = upload.photo_market(photo=filenames[j], group_id=211848929, main_photo=1)
            main_photo_ids.append(photo[0]['id'])
            print('.', end=' ')
        except Exception:
            print(f'Файл [{j}] {filenames[j]} не был загружен')
            photo_not_uploaded.append(filenames[j])
            print(f'Файл [{j}] {filenames[j]} был добавлен в список "Photo_not_uploaded"')
            photo_not_uploaded_id.append(j)
    df = df.drop(labels = photo_not_uploaded_id,axis = 0).reset_index(drop=True)
    print('Загрузка фото на сервер завершена')
#определяем функцию добавления товаров, поля для загрузки
    description = 'Заказать на сайте: https://beautyshop51.ru/catalog'
    def market_add(name,price,main_photo_id,owner_id=-211848929,description=description,category_id=702):
        market_uploads = vk_session.method("market.add",{
            'owner_id':owner_id,
            'name':name,
            'description':description,
            'category_id':category_id,
            'price':price,
            'main_photo_id':main_photo_id})
        return market_uploads

    name=list(df.title)
    price=list(df.price)
    
    print('Начинается загрузка товаров')
    for i in range(len(df)):
        market_add(name=name[i],price=price[i],main_photo_id=main_photo_ids[i])
        print('.', end=' ')
    print()
    print('Загрузка товаров завершена')
    
    def get_market_byid(owner_id=-211848929,count=114):
        get_markets_albums = vk_session.method("market.get",{
            'owner_id':owner_id,
            'count':count})
        return get_markets_albums
    
    products = get_market_byid()
    
    print("Перемещение товаров в подборку GiGi")
    for product in range(len(products['items'])):
        add_products_toalbum(products['items'][product]['id'])
        print('.', end=' ')
    print()
    print('Товары перемещены в подборку GiGi')

if __name__ == '__main__':
    main() 
