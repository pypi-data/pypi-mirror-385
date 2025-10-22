import requests
from urllib.parse import unquote
import mimetypes

short_url = "http://bit.ly/python社團"

# 取得最終 URL
r = requests.head(short_url, allow_redirects=True)
real_url = r.url

# 嘗試從 Content-Disposition 取得檔名
file_name = None
cd = r.headers.get("Content-Disposition")
if cd and "filename=" in cd:
    file_name = cd.split("filename=")[-1].strip('\"')
else:
    # 從 URL 最後一段取得檔名
    file_name = unquote(real_url.split("/")[-1])

# 如果沒有副檔名，用 Content-Type 猜
if "." not in file_name:
    content_type = r.headers.get("Content-Type")
    ext = mimetypes.guess_extension(content_type) if content_type else None
    if ext:
        file_name += ext
    else:
        file_name += ".bin"  # fallback

print("下載檔名:", file_name)

# 下載檔案
r = requests.get(real_url, stream=True)
with open(file_name, "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"✅ 已下載 {file_name}")
