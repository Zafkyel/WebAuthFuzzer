import aiohttp
from bs4 import BeautifulSoup

class Recon:
    async def get_fingerprint(self, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5, ssl=False) as resp:
                    html = await resp.text(errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.string.strip() if soup.title else "No Title"
                    server = resp.headers.get('Server', 'Unknown')
                    return {"url": url, "title": title, "server": server}
        except:
            return {"url": url, "title": "Timeout/Error", "server": "N/A"}