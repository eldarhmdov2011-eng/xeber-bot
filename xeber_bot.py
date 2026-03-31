import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

def xeberleri_getir():
    # Saytlar və onların xüsusi axtarış yolları
    saytlar = [
        {"ad": "Oxu.az", "url": "https://oxu.az", "item": "div.news-i", "img": "img", "link": "a.news-i-inner", "base": "https://oxu.az"},
        {"ad": "Baku.ws", "url": "https://baku.ws", "item": "div.news-item", "img": "img", "link": "a", "base": ""},
        {"ad": "Qafqazinfo", "url": "https://qafqazinfo.az", "item": "div.news-box", "img": "img", "link": "a", "base": ""}
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://google.com"
    }
    
    yeni_siyahi = []
    default_img = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"

    for sayt in saytlar:
        try:
            response = requests.get(sayt["url"], headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # CSS selector ilə elementləri tapırıq
            items = soup.select(sayt["item"])
            count = 0
            
            for item in items:
                if count >= 25: break
                
                link_tag = item.select_one(sayt["link"])
                img_tag = item.select_one(sayt["img"])
                
                if link_tag and link_tag.get("href"):
                    title = link_tag.text.strip() or "Xəbər başlığı"
                    if len(title) < 15: continue # Çox qısa başlıqları atlayırıq
                    
                    href = link_tag.get("href")
                    if not href.startswith("http"): href = sayt["base"] + href
                    
                    # Şəkil linkini dərindən axtarırıq (data-src, src və s.)
                    img_url = ""
                    if img_tag:
                        img_url = img_tag.get("data-src") or img_tag.get("src") or img_tag.get("data-original")
                    
                    if not img_url: img_url = default_img
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    if not img_url.startswith("http"): img_url = sayt["base"] + img_url

                    yeni_siyahi.append(f"""
                    <li class='news-card'>
                        <div class='img-box'>
                            <img src='{img_url}' loading='lazy' onerror="this.src='{default_img}'">
                        </div>
                        <div class='text-box'>
                            <span class='badge'>{sayt['ad']}</span>
                            <a href='{href}' target='_blank'>{title}</a>
                        </div>
                    </li>""")
                    count += 1
        except Exception as e:
            print(f"Xəta {sayt['ad']}: {e}")
            continue
            
    return yeni_siyahi

# Fayl idarəetməsi
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        old_html = f.read()
        kohne_xeberler = re.findall(r"<li class='news-card'>.*?</li>", old_html, re.DOTALL)
else:
    kohne_xeberler = []

yeni_xeberler = xeberleri_getir()
butun_xeberler = yeni_xeberler + [x for x in kohne_xeberler if x not in yeni_xeberler]
butun_xeberler = butun_xeberler[:120]

# Dizayn (Ağ Fon və Baku News)
indiki_vaxt = datetime.now().strftime("%d.%m.%Y %H:%M")
html_final = f"""
<!DOCTYPE html>
<html lang='az'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Baku News - Canlı</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #fff; color: #1a1a1a; }}
        header {{ padding: 40px 20px; text-align: center; border-bottom: 5px solid #000; }}
        header h1 {{ font-size: 45px; margin: 0; text-transform: uppercase; font-weight: 900; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        ul {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; list-style: none; padding: 0; }}
        .news-card {{ border: 1px solid #eee; transition: 0.3s; background: #fff; }}
        .news-card:hover {{ box-shadow: 0 10px 20px rgba(0,0,0,0.1); transform: translateY(-5px); }}
        .img-box {{ width: 100%; height: 210px; overflow: hidden; background: #f9f9f9; }}
        .img-box img {{ width: 100%; height: 100%; object-fit: cover; }}
        .text-box {{ padding: 20px; }}
        .badge {{ background: #d32f2f; color: #fff; padding: 3px 8px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: inline-block; }}
        .text-box a {{ text-decoration: none; color: #000; font-size: 19px; font-weight: 700; line-height: 1.3; display: block; }}
        footer {{ text-align: center; padding: 40px; background: #f4f4f4; margin-top: 50px; font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <header><h1>BAKU NEWS</h1><p>Oxu.az • Baku.ws • Qafqazinfo</p></header>
    <div class='container'><ul>{"".join(butun_xeberler)}</ul></div>
    <footer><p>Son Yenilənmə: {indiki_vaxt} | Cuppulu News</p></footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)
