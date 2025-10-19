import aiohttp
import asyncio

class D1Error(Exception):
    pass

class D1:
    def __init__(self, accountid: str, token: str, db: str):
        self.accountid = accountid
        self.token = token
        self.db = db
        self.queryurl = f"https://api.cloudflare.com/client/v4/accounts/{accountid}/d1/database/{db}/query"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def _req(self, method: str, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.queryurl, headers=self.headers, **kwargs) as req:
                resp = await req.json()
                if not req.ok or not resp.get("success", True):
                    raise D1Error(f"Cloudflare error {req.status}: {resp}")
                return resp.get("result")

    async def execute(self, query: str, binds: list | tuple | set = []):
        data = {
                "sql": query,
        }
        if binds:
            data["parameters"] = list(binds)
        return [q["results"] for q in await self._req("POST", json=data)]
