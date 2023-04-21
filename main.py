try:
  import os
  import time
  import json
  import zlib
  import base64
  import logging
  import requests
  import coloredlogs
except ImportError as e:
  print(f'{e.name} modülü yüklü değil. Lütfen programı çalıştırmadan önce "packages.bat" ile gerekli modülleri yükleyin.')
  time.sleep(5)
  exit()
  
os.system('cls')
os.system('TITLE Fortnite.GG Locker by Liqutch')
coloredlogs.logging.basicConfig(level=coloredlogs.logging.INFO)
log = coloredlogs.logging.getLogger(__name__)
coloredlogs.install(fmt="[%(asctime)s][%(levelname)s] %(message)s", datefmt="%H:%M:%S", logger=log)

if not os.path.isfile('account.json'):       
  log.error('"account.json" dosyası bulunamadı, program kapatılıyor...')
  time.sleep(5)
  exit()

try:
  with open("account.json", encoding="utf-8") as f:
    data = json.load(f)
    account_id = data["account_id"]
    device_id = data["device_id"]
    secret = data["secret"]
except:
  log.error("Hesap bilgilerini alırken bir sorun oluştu. Lütfen dosyanın düzgün yapılandırıldığından emin olun.")
  time.sleep(5)
  exit()

def generateToken():
  url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
  body = f"grant_type=device_auth&account_id={account_id}&device_id={device_id}&secret={secret}"
  headers = {
    "Authorization":
    "basic M2Y2OWU1NmM3NjQ5NDkyYzhjYzI5ZjFhZjA4YThhMTI6YjUxZWU5Y2IxMjIzNGY1MGE2OWVmYTY3ZWY1MzgxMmU=",
    "Content-Type": "application/x-www-form-urlencoded"
  }
  response = requests.post(url, data=body, headers=headers)
  if response.status_code == 400:
    log.error("Token oluşturulamadı. Lütfen bilgilerinizi kontrol edin.")
    time.sleep(5)
    exit()
  if response.status_code == 200:
    log.info("Token başarıyla oluşturuldu.")
    return response.json()["access_token"]
token = generateToken()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
request = requests.post(f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{account_id}/client/QueryProfile?profileId=athena", data="{}", headers=headers)
if request.status_code == 200:
  log.info("Profil bilgileri başarıyla alındı.")
  data = request.json()
  athena_creation_date = data["profileChanges"][0]["profile"]["created"]
  account_items = data["profileChanges"][0]["profile"]["items"]
  cosmetics = ["AthenaCharacter", "AthenaBackpack", "AthenaPickaxe", "AthenaDance", "AthenaGlider", "AthenaItemWrap", "AthenaLoadingScreen", "AthenaMusicPack", "AthenaSkyDiveContrail", "BannerToken"]

  locker = []
  for item in account_items:
      if data["profileChanges"][0]["profile"]["items"][item]["templateId"].split(":")[0] in cosmetics:
        locker.append(data["profileChanges"][0]["profile"]["items"][item]["templateId"].split(":")[1])
  
  items = []
  response = requests.get('https://fortnite.gg/api/items.json')
  log.info("Dolap içerikleri Fortnite.GG ile eşleştiriliyor...")
  for lockeritems in locker:
    for itemlist in response.json():
      if itemlist.lower() == lockeritems:
        items.append(itemlist)
  try:
    fngg_items = requests.get('https://fortnite.gg/api/items.json').json()
    ints = list(map(lambda it: int(fngg_items[it]), items))
    ints.sort()

    diff = list(map(lambda e: str(e[1] - ints[e[0] - 1]) if e[0] > 0 else str(e[1]), enumerate(ints)))
    compress = zlib.compressobj(level=-1, method=zlib.DEFLATED, wbits=-9,
    memLevel=zlib.DEF_MEM_LEVEL, strategy=zlib.Z_DEFAULT_STRATEGY)
    compressed = compress.compress(f"{athena_creation_date},{','.join(diff)}".encode())
    compressed += compress.flush()

    encoded = base64.urlsafe_b64encode(compressed).decode().rstrip("=")
    url = f"https://fortnite.gg/my-locker?items={encoded}"
  except:
    log.error("Eşleştirme sırasında bir hata oluştu, lütfen tekrar deneyin veya destek alın.")
  log.info(f"Fortnite.GG bağlantısı başarıyla oluşturuldu:\n{url}")
  os.startfile(url)
  input()
else:
  log.error(f"Profil bilgileri alınırken bir hata oluştu. [{request.status_code}]")
  time.sleep(5)
  exit()