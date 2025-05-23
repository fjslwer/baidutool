from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

app = Flask(__name__)

def get_domains(keyword, pages=5):
    domains = set()  # 使用集合避免重复域名
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for page in range(pages):
        # 百度搜索URL，pn参数控制分页（每页10条）
        url = f'https://www.baidu.com/s?wd={keyword}&pn={page*10}'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取搜索结果中的链接
            links = soup.select('div.result-c-container a[href]')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    # 解析真实URL
                    real_url = get_real_url(href, headers)
                    if real_url:
                        domain = urlparse(real_url).netloc
                        if domain and not domain.endswith('baidu.com'):  # 过滤百度自身域名
                            domains.add(domain)
            time.sleep(1)  # 防止请求过快
        except Exception as e:
            print(f"Error on page {page+1}: {e}")
    
    return sorted(list(domains))  # 返回排序后的域名列表

def get_real_url(baidu_url, headers):
    try:
        response = requests.get(baidu_url, headers=headers, allow_redirects=True, timeout=5)
        return response.url if response.status_code == 200 else None
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    domains = []
    keyword = ''
    if request.method == 'POST':
        keyword = request.form['keyword'].strip()
        if keyword:
            domains = get_domains(keyword)
    return render_template('index.html', domains=domains, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)