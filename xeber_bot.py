import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

def xeberleri_getir():
    # Şəkilləri və başlıqları 100% fərqli və düzgün verən saytlar
    saytlar = [
        {"ad": "Trend.az", "url": "https://az.trend.az", "base": "https://az.trend.az"},
        {"ad": "Milli.az", "url": "https://www.milli.az", "base": ""},
        {"ad": "Day.az", "url": "https://news.day.az", "base": ""}
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    yeni_siyahi = []
    # Əgər şəkil heç tapılmazsa çıxacaq ehtiyat şəkil
    default_img = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"

    for sayt in saytlar:
        try:
            response = requests.get(sayt["url"], headers=headers, timeout=25)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Hər sayt üçün xüsusi xəbər bloklarını tapırıq
            items = []
            if "trend.az" in sayt["url"]:
                items = soup.find_all("div", class_="news-item")
            elif "milli.az" in sayt["url"]:
                items = soup.find_all("li", class_="news-item")
            else:
                items = soup.find_all("div", class_="news-item")

            count = 0
            for item in items:
                if count >= 15: break
                
                link_tag = item.find("a")
                img_tag = item.find("img")
                
                if link_tag and link_tag.get("href") and len(link_tag.text.strip()) > 25:
                    title = link_tag.text.strip()
                    href = link_tag.get("href")
                    if not href.startswith("http"): href = sayt["base"] + href
                    
                    # Şəkil linkini dərindən axtarırıq ki, hər xəbərin ÖZ şəkli gəlsin
                    img_url = ""
                    if img_tag:
                        # Saytlar fərqli atributlardan istifadə edə bilər
                        img_url = img_tag.get("data-src") or img_tag.get("src") or img_tag.get("data-original")
                    
                    if not img_url or "base64" in img_url: 
                        continue # Şəkil yoxdursa bu xəbəri atlayırıq ki, hamısı eyni olmasın
                        
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    if not img_url.startswith("http"): img_url = sayt["base"] + img_url

                    yeni_siyahi.append(f"""
                    <li class='news-card'>
                        <img src='{img_url}' referrerpolicy='no-referrer' loading='lazy' onerror="this.parentElement.style.display='none'">
                        <div class='text-content'>
                            <a href='{href}' target='_blank'>{title}</a>
                            <span class='source-tag'>[{sayt['ad']}]</span>
                        </div>
                    </li>""")
                    count += 1
        except:
            continue
            
    return yeni_siyahi

# Köhnə xəbərləri silirik ki, Qafqazinfo qalıqları təmizlənsin
yeni_gelenler = xeberleri_getir()
butun_xeberler = yeni_gelenler[:80] # Maksimum 80 ən təzə xəbər

# SCREENSHOT DİZAYNI
indiki_vaxt = datetime.now().strftime("%d.%m.%Y %H:%M")
html_final = f"""
<!DOCTYPE html>
<html lang='az'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Baku News</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; background: #ffffff; color: #333; }}
        header {{ padding: 35px 20px; text-align: center; border-bottom: 3px solid #d32f2f; margin-bottom: 30px; }}
        header h1 {{ margin: 0; font-size: 45px; font-weight: bold; color: #000; letter-spacing: 1px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        ul {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; list-style: none; padding: 0; }}
        .news-card {{ background: #fff; border: 1px solid #eee; border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; transition: 0.3s; }}
        .news-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); }}
        .news-card img {{ width: 100%; height: 200px; object-fit: cover; border-bottom: 1px solid #f0f0f0; }}
        .text-content {{ padding: 20px; flex-grow: 1; }}
        .text-content a {{ text-decoration: none; color: #1a1a1a; font-size: 19px; font-weight: 600; line-height: 1.4; display: block; margin-bottom: 12px; }}
        .text-content a:hover {{ color: #d32f2f; }}
        .source-tag {{ color: #d32f2f; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        footer {{ text-align: center; padding: 40px; color: #bbb; font-size: 13px; margin-top: 50px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <header><h1>BAKU NEWS</h1><p style='color:#777;'>Trend • Milli • Day.az</p></header>
    <div class='container'><ul>{"".join(butun_xeberler)}</ul></div>
    <footer><p>Son Yenilənmə: {indiki_vaxt} | Cuppulu News</p></footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)
