import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

def xeberleri_getir():
    # Şəkilləri bloklamayan və rahat çəkilən saytlar
    saytlar = [
        {"ad": "Trend.az", "url": "https://az.trend.az", "base": "https://az.trend.az"},
        {"ad": "Milli.az", "url": "https://www.milli.az", "base": ""},
        {"ad": "Day.az", "url": "https://news.day.az", "base": ""}
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    
    yeni_siyahi = []
    # Şəkil tapılmayanda çıxacaq default şəkil
    default_img = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"

    for sayt in saytlar:
        try:
            response = requests.get(sayt["url"], headers=headers, timeout=25)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Xəbər bloklarını axtarırıq
            items = soup.find_all(["div", "li"], class_=re.compile("news|item|post|article"))
            count = 0
            
            for item in items:
                if count >= 20: break
                
                link_tag = item.find("a")
                img_tag = item.find("img")
                
                # Başlıq çox qısa olmasın (reklamları keçmək üçün)
                if link_tag and link_tag.get("href") and len(link_tag.text.strip()) > 30:
                    title = link_tag.text.strip()
                    href = link_tag.get("href")
                    if not href.startswith("http"): href = sayt["base"] + href
                    
                    img_url = ""
                    if img_tag:
                        # Müxtəlif şəkil yollarını yoxlayırıq
                        img_url = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-original")
                    
                    if not img_url: img_url = default_img
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    if not img_url.startswith("http"): img_url = sayt["base"] + img_url

                    yeni_siyahi.append(f"""
                    <li class='news-card'>
                        <img src='{img_url}' referrerpolicy='no-referrer' loading='lazy' onerror="this.src='{default_img}'">
                        <div class='text-content'>
                            <a href='{href}' target='_blank'>{title}</a>
                            <span class='source-tag'>[{sayt['ad']}]</span>
                        </div>
                    </li>""")
                    count += 1
        except:
            continue
            
    return yeni_siyahi

# Köhnə xəbərləri oxu
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        old_content = f.read()
        kohne_xeberler = re.findall(r"<li class='news-card'>.*?</li>", old_content, re.DOTALL)
else:
    kohne_xeberler = []

yeni_gelenler = xeberleri_getir()
butun_xeberler = yeni_gelenler + [x for x in kohne_xeberler if x not in yeni_gelenler]
butun_xeberler = butun_xeberler[:100]

# SCREENSHOT-DAKI DİZAYNIN TAM EYNİSİ
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
        header {{ padding: 40px 20px; text-align: center; border-bottom: 2px solid #d32f2f; margin-bottom: 20px; }}
        header h1 {{ margin: 0; font-size: 50px; font-weight: bold; color: #000; letter-spacing: 2px; }}
        header p {{ color: #666; margin-top: 10px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        ul {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; list-style: none; padding: 0; }}
        .news-card {{ background: #fff; border: 1px solid #eee; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; transition: 0.2s; }}
        .news-card:hover {{ box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
        .news-card img {{ width: 100%; height: 180px; object-fit: cover; border-bottom: 1px solid #f9f9f9; }}
        .text-content {{ padding: 15px; flex-grow: 1; }}
        .text-content a {{ text-decoration: none; color: #1a1a1a; font-size: 18px; font-weight: 500; line-height: 1.4; display: block; margin-bottom: 10px; }}
        .text-content a:hover {{ text-decoration: underline; }}
        .source-tag {{ color: #d32f2f; font-size: 13px; font-weight: bold; text-transform: uppercase; }}
        footer {{ text-align: center; padding: 30px; color: #999; font-size: 12px; margin-top: 40px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <header>
        <h1>BAKU NEWS</h1>
        <p>Günün Ən Son Xəbərləri</p>
    </header>
    <div class='container'>
        <ul>
            {"".join(butun_xeberler)}
        </ul>
    </div>
    <footer>
        <p>Yenilənmə: {indiki_vaxt} | Cuppulu</p>
    </footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)
    
