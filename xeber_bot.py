import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

def xeberleri_getir():
    saytlar = [
        {"ad": "Milli.az", "url": "https://www.milli.az", "base": ""},
        {"ad": "Trend.az", "url": "https://az.trend.az", "base": "https://az.trend.az"},
        {"ad": "Day.az", "url": "https://news.day.az", "base": ""}
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    yeni_siyahi = []
    default_img = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"

    for sayt in saytlar:
        try:
            response = requests.get(sayt["url"], headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all(["div", "li", "article"])
            count = 0
            
            for item in items:
                link = item.find("a")
                img = item.find("img")
                if link and link.get("href") and len(link.text.strip()) > 30:
                    title = link.text.strip()
                    href = link.get("href")
                    if not href.startswith("http"): href = sayt["base"] + href
                    
                    img_url = ""
                    if img:
                        img_url = img.get("data-src") or img.get("src") or img.get("data-original")
                    
                    if not img_url or "base64" in img_url: img_url = default_img
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    if not img_url.startswith("http"): img_url = sayt["base"] + img_url

                    yeni_siyahi.append(f"""
                    <li class='news-card'>
                        <img src='{img_url}' referrerpolicy='no-referrer' onerror="this.src='{default_img}'">
                        <div class='text-content'>
                            <a href='{href}' target='_blank'>{title}</a>
                            <span class='source-tag'>[{sayt['ad']}]</span>
                        </div>
                    </li>""")
                    count += 1
                    if count >= 15: break
        except:
            continue
    return yeni_siyahi

yeni_xeberler = xeberleri_getir()
indiki_vaxt = datetime.now().strftime("%d.%m.%Y %H:%M")
html_final = f"""
<!DOCTYPE html>
<html lang='az'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Baku News</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; background: #fff; }}
        header {{ padding: 40px 20px; text-align: center; border-bottom: 2px solid #d32f2f; }}
        header h1 {{ margin: 0; font-size: 50px; font-weight: bold; letter-spacing: 2px; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 20px; }}
        ul {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; list-style: none; padding: 0; }}
        .news-card {{ background: #fff; border: 1px solid #eee; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }}
        .news-card img {{ width: 100%; height: 180px; object-fit: cover; }}
        .text-content {{ padding: 15px; flex-grow: 1; }}
        .text-content a {{ text-decoration: none; color: #1a1a1a; font-size: 18px; font-weight: 500; line-height: 1.4; display: block; margin-bottom: 10px; }}
        .source-tag {{ color: #d32f2f; font-size: 13px; font-weight: bold; text-transform: uppercase; }}
        footer {{ text-align: center; padding: 30px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <header><h1>BAKU NEWS</h1><p>Günün Ən Son Xəbərləri</p></header>
    <div class='container'><ul>{"".join(yeni_xeberler)}</ul></div>
    <footer><p>Son Yenilənmə: {indiki_vaxt} | Cuppulu</p></footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)
