import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

def xeberleri_getir():
    # Saytlar və onların xüsusi axtarış ayarları
    saytlar = [
        {"ad": "Oxu.az", "url": "https://oxu.az", "class": "news-i"},
        {"ad": "Report.az", "url": "https://report.az", "class": "news-block"},
        {"ad": "Qafqazinfo", "url": "https://qafqazinfo.az", "class": "news-box"}
    ]
    
    # Saytları aldatmaq üçün "İnsan" maskası (User-Agent)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    yeni_siyahi = []
    default_img = "https://images.unsplash.com/photo-1585007600263-ad12200a09a5?q=80&w=1000"

    for sayt in saytlar:
        try:
            response = requests.get(sayt["url"], headers=headers, timeout=20)
            if response.status_code != 200: continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            count = 0
            
            # Oxu.az üçün xüsusi şəkil və başlıq çəkmə
            if "oxu.az" in sayt["url"]:
                items = soup.find_all("div", class_="news-i")
                for item in items[:30]:
                    link_tag = item.find("a", class_="news-i-inner")
                    title_tag = item.find("div", class_="title")
                    img_tag = item.find("img")
                    
                    if link_tag and title_tag:
                        title = title_tag.text.strip()
                        href = "https://oxu.az" + link_tag.get("href")
                        img_url = img_tag.get("src") if img_tag else default_img
                        if not img_url.startswith("http"): img_url = "https://oxu.az" + img_url
                        
                        yeni_siyahi.append(f"""
                        <li class='news-card'>
                            <img src='{img_url}' alt='img'>
                            <div class='text-content'>
                                <a href='{href}' target='_blank'>{title}</a>
                                <span class='source'>[{sayt['ad']}]</span>
                            </div>
                        </li>""")
                        count += 1

            # Digər saytlar üçün ümumi axtarış
            else:
                links = soup.find_all("a")
                for l in links:
                    t = l.text.strip()
                    if len(t) > 40 and count < 25:
                        h = l.get('href')
                        full_h = h if h.startswith("http") else sayt["url"] + h
                        yeni_siyahi.append(f"""
                        <li class='news-card'>
                            <img src='{default_img}' alt='img'>
                            <div class='text-content'>
                                <a href='{full_h}' target='_blank'>{t}</a>
                                <span class='source'>[{sayt['ad']}]</span>
                            </div>
                        </li>""")
                        count += 1
        except:
            continue
    return yeni_siyahi

# Köhnə xəbərləri qoru və yeniləri üstə yığ
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        old_content = f.read()
        kohne_xeberler = re.findall(r"<li class='news-card'>.*?</li>", old_content, re.DOTALL)
else:
    kohne_xeberler = []

yeni_gelenler = xeberleri_getir()
butun_xeberler = yeni_gelenler + [x for x in kohne_xeberler if x not in yeni_gelenler]
butun_xeberler = butun_xeberler[:120] # Limit 120 xəbər

# Ağ Dizayn və Böyük Şəkillər (CSS)
indiki_vaxt = datetime.now().strftime("%d.%m.%Y %H:%M")
html_final = f"""
<!DOCTYPE html>
<html lang='az'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Baku News</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f4f4f4; color: #222; }}
        header {{ background: #fff; padding: 25px; text-align: center; border-bottom: 5px solid #d32f2f; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ margin: 0; font-size: 40px; color: #1a1a1a; letter-spacing: 2px; }}
        .container {{ max-width: 1100px; margin: 30px auto; padding: 0 20px; }}
        ul {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; list-style: none; padding: 0; }}
        .news-card {{ background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.08); transition: 0.3s; }}
        .news-card:hover {{ transform: translateY(-8px); box-shadow: 0 12px 25px rgba(0,0,0,0.15); }}
        .news-card img {{ width: 100%; height: 200px; object-fit: cover; border-bottom: 1px solid #eee; }}
        .text-content {{ padding: 20px; }}
        .text-content a {{ text-decoration: none; color: #111; font-size: 19px; font-weight: 600; line-height: 1.4; display: block; margin-bottom: 10px; }}
        .text-content a:hover {{ color: #d32f2f; }}
        .source {{ font-size: 13px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }}
        footer {{ text-align: center; padding: 40px; background: #fff; margin-top: 50px; border-top: 1px solid #ddd; color: #777; }}
    </style>
</head>
<body>
    <header><h1>BAKU NEWS</h1><p>Günün Ən Son Xəbərləri</p></header>
    <div class='container'><ul>{"".join(butun_xeberler)}</ul></div>
    <footer><p>Son Yenilənmə: {indiki_vaxt} | Cuppulu tərəfindən</p></footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)
