import os
import sys
import json
import zlib
import base64
import aiohttp
import asyncio
import inquirer
import platform
import pyperclip
import webbrowser
import coloredlogs


__version__ = "2.0"
SWITCH_TOKEN = "OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"


os.system('cls' if sys.platform.startswith('win') else 'clear')
os.system(f'TITLE LockerGenerator v{__version__} by Liqutch')

coloredlogs.logging.basicConfig(level=coloredlogs.logging.INFO)
log = coloredlogs.logging.getLogger(__name__)
coloredlogs.install(fmt="[%(asctime)s][%(levelname)s] %(message)s", datefmt="%H:%M:%S", logger=log)


class EpicAccount:
    def __init__(self, data: dict = {}) -> None:
        self.raw = data

        self.access_token = data.get("access_token", "")
        self.display_name = data.get("displayName", "")
        self.account_id = data.get("account_id", "")
    
    async def get_profile(self):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method="POST",
                url="https://fngw-mcp-gc-livefn.ol.epicgames.com"
                f"/fortnite/api/game/v2/profile/{self.account_id}/client/QueryProfile?profileId=athena&rvn=-1",
                headers={"Authorization": f"bearer {self.access_token}", "Content-Type": "application/json"},
                data=json.dumps({})
            ) as request:
                if request.status == 200:
                    return await request.json()
                else:
                    data = await request.json()
                    log.info("There was a problem while getting the profile.")
                    log.info("{}/{}/{}\n".format(request.status, data["numericErrorCode"], data["errorCode"]))
                    log.info(f"ProfileExtractor v{__version__} will close in 5 seconds. Try again later.")
                    await asyncio.sleep(5)
                    sys.exit()


class Generator:
    def __init__(self) -> None:
        self.http: aiohttp.ClientSession

        self.access_token = ""
        self.user_agent = f"LockerGenerator/{__version__} {platform.system()}/{platform.version()}"
        
    async def start(self) -> None:
        self.http = aiohttp.ClientSession(headers={"User-Agent": self.user_agent})

        self.access_token = await self.get_access_token()

        log.info("Opening device code link in a new tab...")
        device_code = await self.create_device_code()
        webbrowser.open(device_code[0], new=1)

        account = await self.wait_for_device_code_completion(code=device_code[1])
        data = await account.get_profile()

        os.system('cls' if sys.platform.startswith('win') else 'clear')
        log.info(f"Logged in as: {account.display_name}\n")

        choice = [inquirer.Confirm('start', message="Do you want to start the process?",default=True)]
        answers = inquirer.prompt(choice)

        os.system('cls' if sys.platform.startswith('win') else 'clear')
        if not answers['start']:
            log.info(f'Closing LockerGenerator v{__version__}...')
            await asyncio.sleep(1)
            sys.exit()

        account_items = data["profileChanges"][0]["profile"]["items"]
        athena_creation_date = data["profileChanges"][0]["profile"]["created"]

        log.info("Generating the locker...")
        all_items = list(map(lambda item: account_items[item]["templateId"].split(":")[1], account_items))
        
        locker = []
        fngg_items = await self.get_fngg_items()
        fngg_items_lowercase = list(map(lambda x: x.lower(), fngg_items.keys()))

        for item in all_items: 
            if item in fngg_items_lowercase:
                original_id = list(fngg_items.keys())[fngg_items_lowercase.index(item.lower())]
                locker.append(original_id)

        ints = list(map(lambda it: int(fngg_items[it]), locker))
        ints.sort()

        diff = list(map(lambda e: str(e[1] - ints[e[0] - 1]) if e[0] > 0 else str(e[1]), enumerate(ints)))
        compress = zlib.compressobj(
            level=-1,
            method=zlib.DEFLATED,
            wbits=-9,
            memLevel=zlib.DEF_MEM_LEVEL,
            strategy=zlib.Z_DEFAULT_STRATEGY
        )
        compressed = compress.compress(f"{athena_creation_date},{','.join(diff)}".encode())
        compressed += compress.flush()

        encoded = base64.urlsafe_b64encode(compressed).decode().rstrip("=")
        
        url = f"https://fortnite.gg/my-locker?items={encoded}"
        os.startfile(url)

        log.info("Link successfully copied to the clipboard. Press enter to close the program.")
        pyperclip.copy(url)
        
        input(), sys.exit()

    async def get_fngg_items(self) -> dict:
        async with self.http.request(
            method="GET",
            url="https://fortnite.gg/api/items.json",
        ) as request:
            return await request.json()
    
    async def get_access_token(self) -> str:
        async with self.http.request(
            method="POST",
            url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"basic {SWITCH_TOKEN}",
            },
            data={
                "grant_type": "client_credentials",
            },
        ) as request:
            data = await request.json()

        return data["access_token"]
    
    async def create_device_code(self) -> tuple:
        async with self.http.request(
            method="POST",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization",
            headers={
                "Authorization": f"bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        ) as request:
            data = await request.json()

        return data["verification_uri_complete"], data["device_code"]

    async def wait_for_device_code_completion(self, code: str) -> EpicAccount:
        os.system('cls' if sys.platform.startswith('win') else 'clear')
        log.info("Waiting for authentication...")

        while True:
            async with self.http.request(
                method="POST",
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                headers={
                    "Authorization": f"basic {SWITCH_TOKEN}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "device_code", "device_code": code},
            ) as request:
                if request.status == 200:
                    auth_data = await request.json()
                    break
                else:
                    pass

                await asyncio.sleep(5)
                
        return EpicAccount(data=auth_data)

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        loop.run_forever()


ext = Generator()
ext.run()