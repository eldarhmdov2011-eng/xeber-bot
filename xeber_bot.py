import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

def xeberleri_getir():
    saytlar = {
        "Oxu.az": "https://oxu.az",
        "Qafqazinfo": "https://qafqazinfo.az",
        "Report.az": "https://report.az"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    yeni_siyahi = []
    default_img = "https://via.placeholder.com/100x70?text=News"

    for ad, url in saytlar.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            count = 0
            
            if "oxu.az" in url:
                items = soup.find_all("div", class_="news-i")
                for item in items:
                    link = item.find("a", class_="news-i-inner")
                    title = item.find("div", class_="title")
                    img_tag = item.find("img")
                    img_url = img_tag.get("src") if img_tag else default_img
                    if img_url and not img_url.startswith("http"):
                        img_url = "https://oxu.az" + img_url

                    if link and title and count < 30:
                        yeni_siyahi.append(f"""
                        <li>
                            <img src='{img_url}' alt='news'>
                            <div class='text-content'>
                                <small style='color:#d32f2f'>[{ad}]</small>
                                <a href='https://oxu.az{link.get('href')}' target='_blank'>{title.text.strip()}</a>
                            </div>
                        </li>
                        """)
                        count += 1
            
            else: # Digər saytlar üçün sadələşdirilmiş çəkim
                links = soup.find_all("a")
                for l in links:
                    t = l.text.strip()
                    if len(t) > 30 and count < 30:
                        h = l.get('href')
                        full_h = h if h.startswith("http") else url + h
                        yeni_siyahi.append(f"""
                        <li>
                            <img src='{default_img}' alt='news'>
                            <div class='text-content'>
                                <small style='color:#d32f2f'>[{ad}]</small>
                                <a href='{full_h}' target='_blank'>{t}</a>
                            </div>
                        </li>
                        """)
                        count += 1
        except:
            continue
    return yeni_siyahi

# 1. Köhnə xəbərləri oxu
kohne_xeberler = []
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        kohne_xeberler = re.findall(r"<li>.*?</li>", content, re.DOTALL)

# 2. Yeni xəbərləri çək və birləşdir
yeni_gelenler = xeberleri_getir()
butun_xeberler = yeni_gelenler + [x for x in kohne_xeberler if x not in yeni_gelenler]
butun_xeberler = butun_xeberler[:150]

# 3. Yeni Ağ Dizayn (BAKU NEWS)
indiki_vaxt = datetime.now().strftime("%d.%m.%Y %H:%M")
html_basliq = f"""
<!DOCTYPE html>
<html lang='az'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Baku News Portal</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; background: #ffffff; color: #333; }}
        .header {{ background: #f8f9fa; padding: 20px; border-bottom: 3px solid #d32f2f; text-align: center; }}
        h1 {{ margin: 0; color: #1a1a1a; letter-spacing: 2px; font-size: 32px; font-weight: bold; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 0 15px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ display: flex; align-items: center; gap: 15px; padding: 15px 0; border-bottom: 1px solid #eee; }}
        li:last-child {{ border-bottom: none; }}
        li img {{ width: 100px; height: 70px; object-fit: cover; border-radius: 4px; background: #eee; }}
        .text-content {{ flex: 1; }}
        a {{ text-decoration: none; color: #1a1a1a; font-size: 17px; font-weight: 500; line-height: 1.4; }}
        a:hover {{ color: #d32f2f; }}
        .footer {{ text-align: center; padding: 30px; color: #888; font-size: 13px; background: #f8f9fa; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class='header'>
        <h1>BAKU NEWS</h1>
        <p style='margin:5px 0 0; color:#666;'>Günün ən vacib xəbərləri</p>
    </div>
    <div class='container'>
        <ul>
"""

html_sonluq = f"""
        </ul>
    </div>
    <div class='footer'>
        <p>Avtomatik Yenilənmə: {indiki_vaxt}</p>
    </div>
</body>
</html>
"""

tam_html = html_basliq + "".join(butun_xeberler) + html_sonluq
with open("index.html", "w", encoding="utf-8") as f:
    f.write(tam_html)
