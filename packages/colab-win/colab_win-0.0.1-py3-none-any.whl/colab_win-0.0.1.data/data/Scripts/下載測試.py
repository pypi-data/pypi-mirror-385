# 1️⃣ 縮網址
vvv_name = "Python社團" #if sys.argv[2] in ["-H","-h"] else sys.argv[2] 
short_url = f"http://bit.ly/{vvv_name}"

import requests
# # 2️⃣ 取得最終真實 URL
# response = requests.head(short_url, allow_redirects=True)
# real_url = response.url
# print("真實 URL:", real_url)

# # 3️⃣ 下載檔案
# file_name = real_url.split("/")[-1]  # 從 URL 取檔名
# r = requests.get(real_url, stream=True)

# with open(  f"{file_name}.ipynb" , "wb") as f:
#     for chunk in r.iter_content(chunk_size=8192):
#         f.write(chunk)

# print(f"✅ 已下載 {file_name}.ipynb") 



# 取得最終 URL
r = requests.head(short_url, allow_redirects=True)
real_url = r.url

# 嘗試從 Content-Disposition 取得檔名
file_name = None
cd = r.headers.get("Content-Disposition")
if cd and "filename=" in cd:
    file_name = cd.split("filename=")[-1].strip('\"')
else:
    from urllib.parse import unquote
    print(real_url)
    # fallback: 從 URL 最後一段取得檔名
    file_name = unquote(real_url.split("/")[-1])

print("下載檔名:", file_name) ## # .ipynb