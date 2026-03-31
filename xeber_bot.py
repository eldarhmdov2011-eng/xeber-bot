import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime

# Xəbər mənbələri
SITES = {
    "Oxu.az": "https://oxu.az",
    "Azxeber.com": "https://azxeber.com",
    "Baku.ws": "https://baku.ws"
}

DB_FILE = "link_bazasi.txt"
HTML_FILE = "index.html"

def xeberleri_cek(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=15, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        if "oxu.az" in url:
            items = soup.find_all('a', class_='news-i-inner')[:10]
        elif "azxeber.com" in url:
            items = soup.select('.news-box a')[:10]
        elif "baku.ws" in url:
            items = soup.select('.news_item a')[:10]
            
        for item in items:
            link = item.get('href')
            if link and not link.startswith('http'):
                link = url + link
            title = item.text.strip()
            if title and link:
                news_list.append({"title": title, "link": link})
        return news_list
    except Exception as e:
        print(f"Xəta baş verdi ({url}): {e}")
        return []

def bazada_var(link):
    if not os.path.exists(DB_FILE): return False
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return link in f.read()

def html_yenile(yeni_xeberler):
    # Əgər fayl yoxdursa, ana şablonu yarat
    if not os.path.exists(HTML_FILE):
        baslangic_html = """
        <!DOCTYPE html>
        <html lang="az">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Xəbər.az - Canlı Xəbər Lenti</title>
            <style>
                body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 0; }
                header { background: #fff; padding: 20px; border-bottom: 4px solid #00b4cc; text-align: center; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                header h1 { margin: 0; color: #00b4cc; font-size: 35px; font-weight: 900; letter-spacing: -1px; }
                
                .container { width: 95%; max-width: 1000px; margin: 20px auto; }
                #xeber-lenti { display: flex; flex-direction: column-reverse; }

                .news-card { 
                    background: white; 
                    margin-bottom: 15px; 
                    padding: 25px; 
                    border-radius: 12px; 
                    text-decoration: none; 
                    display: block; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    transition: transform 0.2s;
                    border-left: 6px solid #00b4cc;
                }
                .news-card:hover { transform: scale(1.01); background: #fafafa; }

                .category { color: #ff4757; font-weight: bold; font-size: 13px; text-transform: uppercase; margin-bottom: 8px; display: block; }
                .title { font-size: 28px; color: #1e272e; font-weight: 800; line-height: 1.3; display: block; }
                .meta { color: #7f8c8d; font-size: 13px; margin-top: 12px; display: block; font-style: italic; }

                @media (max-width: 768px) {
                    header h1 { font-size: 26px; }
                    .news-card { padding: 15px; border-radius: 5px; border-left-width: 4px; }
                    .title { font-size: 18px; }
                    .container { width: 100%; margin: 10px 0; }
                }
            </style>
        </head>
        <body>
            <header><h1>XƏBƏR.AZ</h1></header>
            <div class="container"><div id="xeber-lenti"></div></div>
        </body>
        </html>
        """
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(baslangic_html)

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    indi = datetime.now().strftime("%d.%m.%Y %H:%M")
    marker = ""
    yeni_html_blok = ""

    for site_name, news in yeni_xeberler.items():
        for n in news:
            if not bazada_var(n["link"]):
                yeni_html_blok += f'''
                <a href="{n["link"]}" class="news-card" target="_blank">
                    <span class="category">{site_name}</span>
                    <span class="title">{n["title"]}</span>
                    <span class="meta">Əlavə edildi: {indi}</span>
                </a>
                '''
                with open(DB_FILE, "a", encoding="utf-8") as db:
                    db.write(n["link"] + "\n")
    
    if yeni_html_blok:
        content = content.replace(marker, marker + yeni_html_blok)
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

# Əsas dövr (1 saatdan bir işləyir)
if __name__ == "__main__":
    print("Xəbər.az Botu işə düşdü...")
    while True:
        saat = datetime.now().strftime("%H:%M:%S")
        print(f"[{saat}] Saytlar yoxlanılır...")
        
        results = {name: xeberleri_cek(url) for name, url in SITES.items()}
        yenilendi = html_yenile(results)
        
        if yenilendi:
            print("Yeni xəbərlər tapıldı və sayta əlavə edildi!")
        else:
            print("Yeni xəbər yoxdur.")
            
        print("1 saatlıq yuxuya keçilir... (Konsolu bağlama!)")
        time.sleep(3600)
