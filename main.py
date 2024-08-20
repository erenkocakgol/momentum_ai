##########################################################
# MOMENTUM ARTIFICIAL INTELLIGENCE GÜNDEM HABER JENERATÖRÜ
# v1.3
# Copyright 2024 Eren Koçakgöl
##########################################################
## KÜTÜPHANELER

import json
import requests
from bs4 import BeautifulSoup
import openai
import sqlite3
from PIL import Image
from io import BytesIO
import os
import re
import unicodedata
import base64

##########################################################
## GLOBAL DEĞİŞKENLER

scraped_news = dict()

##########################################################
## KONFİGÜRASYON

def config():
    with open('config.json', 'r') as file:
        config = json.load(file)

    kategoriler = config["kategoriler"]
    api_key = config["api_key"]

    print("Config dosyası başarıyla okundu.")  # Checkpoint 1
    print(f"Kategoriler: {kategoriler}")
    return kategoriler, api_key


##########################################################
## KISIM 1: ARAŞTIRMA-VERİ ÇEKME

def search(kategoriler):
    for kategori in kategoriler:
        kategori_url = f"https://www.ntv.com.tr/{kategori}"
        print(f"{kategori} kategorisi için URL oluşturuldu: {kategori_url}")  # Checkpoint 2

        response = requests.get(kategori_url)
        response.raise_for_status()  # İstek başarısızsa hata ver
        print(f"{kategori} kategorisi için veri çekildi.")  # Checkpoint 3

        soup = BeautifulSoup(response.text, 'html.parser')

        headlines = []
        for item in soup.find_all('a', class_="card-text-link text-elipsis-3", limit=3):
            title = item.text.strip()
            link = item['href']
            if not link.startswith('http'):
                link = "https://www.ntv.com.tr" + link
            headlines.append((title, link))

        if not headlines:
            print(f"{kategori} kategorisi için haber bulunamadı.")  # Checkpoint 4
        else:
            print(f"{kategori} kategorisi için {len(headlines)} haber bulundu.")  # Checkpoint 5

        news = []
        for i, (title, link) in enumerate(headlines, start=1):
            print(f"{i}. {title}")
            print(f"   Link: {link}")
            news.append((title, link))
        scraped_news[kategori] = news
    print("Tüm kategoriler için haberler çekildi.")  # Checkpoint 6


##########################################################
## KISIM 2: PREDICTION-GENERATING
def slugify(text):
    # Büyük harfleri küçük harflere çevirme
    text = text.lower()
    
    # Unicode karakterleri normalleştirip Türkçe karakterleri dönüştürme
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Boşlukları tire ile değiştirme
    text = re.sub(r'\s+', '-', text)
    
    # Geçersiz karakterleri kaldırma (sadece harfler, sayılar ve tire kalır)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Birden fazla ardışık tireyi tek bir tireye indirgeme
    text = re.sub(r'-+', '-', text)
    
    # Baştaki ve sondaki tireleri temizleme
    return text.strip('-')

def generating(api_key):
    all_generated_texts = []
    for kategori, articles in scraped_news.items():
        print(f"{kategori} kategorisinden {len(articles)} haber işlenecek.")  # Checkpoint 7
        for title, url in articles:
            response = requests.get(url)
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            subtitle_parent = soup.find('div', class_="category-detail-left")
            baslik = subtitle_parent.find('h1').get_text(strip=True)
            altbaslik = subtitle_parent.find('h2').get_text(strip=True)
            
            parent_div = soup.find_all('div', class_="content-news-tag-selector")
            
            p_tags = [p for div in parent_div for p in div.find_all('p')]
            article_text = " ".join([p.text.strip() for p in p_tags])
            
            print(f"{url} linki başarıyla alındı.")  # Checkpoint 8
            
            
            def pixabay():
                # Pixabay API anahtarınızı buraya ekleyin
                api_key = "39678317-faf80aed0e9382b0a022d6351"
                query = slugify(baslik)  # Aranacak kelime
                url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&per_page=3"

                response = requests.get(url)
                data = response.json()

                # Eğer resim bulunduysa, ilk resmi indir
                if data['hits']:
                    image_url = data['hits'][0]['largeImageURL']
                    img_data = requests.get(image_url).content

                    with open(f"/Users/erenkocakgol/repos/postafon.com/habermomentum/static/depo/{query}.jpg", "wb") as handler:
                        handler.write(img_data)
                        print("Image downloaded successfully!")
                else:
                    print("No images found.")
            
            pixabay()
            
            '''img_parent = soup.find('div', class_="card-img-wrapper")
            img_element = img_parent.find('img')
            img_url = img_element['src']
            
            img_title = slugify(baslik)
            
            # Eğer Base64 formatında bir resimse
            if img_url.startswith('data:image'):
                try:
                    # Base64 verisinin başlangıcını ayır
                    header, encoded = img_url.split(',', 1)
                    
                    # Resim formatını belirlemek için header'ı incele
                    image_format = header.split(';')[0].split('/')[1]
                    
                    # Base64 kodunu çöz
                    image_data = base64.b64decode(encoded)
                    
                    # Resmi kaydet
                    with open(f"images/{img_title}.{image_format}", 'wb') as file:
                        file.write(image_data)
                    
                    print(f"Resim başarıyla {img_title}.{image_format} olarak kaydedildi!")
                except Exception as e:
                    print(f"Base64 resmi kaydederken hata oluştu: {str(e)}")

            # Eğer Base64 değilse, URL üzerinden resmi indir
            else:
                try:
                    # Resmi URL'den çek
                    response_img = requests.get(img_url)

                    # HTTP isteği başarılı mı kontrol et
                    if response_img.status_code == 200:
                        # Resmin MIME türünü al
                        content_type = response_img.headers.get('Content-Type', '')
                        
                        # MIME türünden uzantıyı çıkar
                        extension = content_type.split('/')[-1]
                        
                        # Eğer uzantı bilinmiyorsa varsayılanı .jpg yap
                        if extension not in ['png', 'jpeg', 'jpg', 'gif', 'bmp', 'webp']:
                            extension = 'jpg'
                        
                        # Resmi kaydet
                        with open(f"images/{img_title}.{extension}", 'wb') as file:
                            file.write(response_img.content)
                        
                        print(f"Resim başarıyla {img_title}.{extension} olarak kaydedildi!")
                    else:
                        print(f"Resim indirilemedi, durum kodu: {response_img.status_code}")
                except Exception as e:
                    print(f"Resim URL'den indirilirken hata oluştu: {str(e)}")'''
            
            def rewrite_text(text, length=400, i=0):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # Modeli burada belirtiyorsunuz
                        messages=[
                            {"role": "system", "content": "Bu görevde, eğer varsa verilen haber metninin başlığındaki olayı (alakasız konuları atlayarak) Türkçe olarak yeniden yazacaksınız. 'NTV' kelimesi olmamalı ve her konuyu başlıklar ile ayırmalısınız. Yoksa cevap vermeyin."},
                            {"role": "user", "content": f"Haber Metni = {text}"}
                        ],
                        max_tokens=length + 50,  # Döndürülecek maksimum token sayısı
                        temperature=0.6,  # Yaratıcılık seviyesi
                    )
                    return response.choices[0].message['content'].strip()

                except Exception as e:
                    i += 1
                    if i < 4:
                        print(f"{i}. kez yeniden deneniyor...")
                        return rewrite_text(text=text, length=length, i=i)
                    else:
                        print(f"OpenAI API hatası: {e}")
                        return "Yeniden yazma başarısız oldu."


            generated_text = rewrite_text(text=baslik+ " " +altbaslik+ " " +article_text).replace("#", "").replace("*", "")
            #image_path = generate_image(title, api_key)  # Resmi oluştur ve yolunu al
            image_path = slugify(baslik)
            all_generated_texts.append((kategori, title, generated_text, image_path))  # Resmi de ekle
            print(f"Metin başarıyla yeniden yazıldı.")  # Checkpoint 9

    if not all_generated_texts:
        print("Hiçbir metin oluşturulamadı.")  # Checkpoint 10
    else:
        print(f"{len(all_generated_texts)} metin oluşturuldu.")  # Checkpoint 11

    return all_generated_texts

##########################################################
## KISIM 3: RESİM ÜRETME

def generate_image(title, api_key):
    try:
        response = openai.Image.create(
            prompt=f"512x512 boyutlarında başlığı; {title} olan, haber için kapak resmi yarat",
            n=1,
            size="512x512",
            api_key=api_key
        )
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        # Create directory if it does not exist
        if not os.path.exists('images'):
            os.makedirs('images')

        # Convert title to URL-friendly format
        sanitized_title = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower()).strip('-')
        image_path = f"images/{sanitized_title[:50]}.png"  # Resmi kaydet

        image.save(image_path)
        print(f"Resim başarıyla oluşturuldu ve kaydedildi: {image_path}")
        return image_path  # Resmin yolunu döndür
        
    except Exception as e:
        print(f"OpenAI API hatası: {e}")
        return None


##########################################################
## KISIM 4: VERİTABANI KAYDI

def create_db():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kategori TEXT NOT NULL DEFAULT 'genel',
        title TEXT NOT NULL DEFAULT 'Başlık Yok',
        content TEXT NOT NULL DEFAULT 'İçerik Yok',
        image TEXT  -- Resim yolunu tutacak sütun
    )
    ''')
    
    conn.commit()
    conn.close()

def save_to_db(news_data):
    # Veritabanını yeniden oluştur
    if os.path.exists('news.db'):
        os.remove('news.db')
    create_db()

    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()

    # Varsayılan değerlerle NULL olanları değiştir
    processed_data = []
    for data in news_data:
        # Eğer değerlerden biri None ise varsayılan değerle değiştir
        processed_data.append((
            data[0] if data[0] is not None else 'genel',
            data[1] if data[1] is not None else 'Başlık Yok',
            data[2] if data[2] is not None else 'İçerik Yok',
            data[3] if data[3] is not None else ''
        ))

    cursor.executemany('''
    INSERT INTO news (kategori, title, content, image) VALUES (?, ?, ?, ?)
    ''', processed_data)
    
    conn.commit()
    conn.close()
    print("Veriler veritabanına kaydedildi.")
    
##########################################################
## KISIM 5: DÖNGÜ

kategoriler, api_key = config()
openai.api_key = api_key
search(kategoriler=kategoriler)
generated_texts = generating(api_key=api_key)

save_to_db(generated_texts)

print("Oluşturulan metinler veritabanına kaydedildi.")
