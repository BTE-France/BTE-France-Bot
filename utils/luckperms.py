import json

import aiohttp


async def _lp_base_request(method, url, data={}):
    from utils import get_env  # avoid circular import

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, data=data, headers={"Authorization": f"Bearer {get_env('LUCKPERMS_REST_AUTH_KEY')}"}) as resp:
            await resp.read()
            return resp


async def lp_lookup_user(username: str):
    resp = await _lp_base_request("GET", f"https://luckperms.btefrance.fr/user/lookup?username={username}")
    if resp.status == 404:
        return None
    return await resp.json()


async def lp_get_user(uuid: str):
    resp = await _lp_base_request("GET", f"https://luckperms.btefrance.fr/user/{uuid}")
    if resp.status == 404:
        return None
    return await resp.json()


async def lp_promote_user(uuid: str):
    resp = await _lp_base_request("POST", f"https://luckperms.btefrance.fr/user/{uuid}/promote", data=json.dumps({"track": "rank"}))
    if resp.status == 404:
        return None
    return await resp.json()


async def lp_add_node_to_user(uuid: str, data: dict):
    resp = await _lp_base_request("POST", f"https://luckperms.btefrance.fr/user/{uuid}/nodes", data=json.dumps(data))
    if resp.status == 404:
        return None
    return await resp.json()


async def lp_search_nodes(key: str):
    resp = await _lp_base_request("GET", f"https://luckperms.btefrance.fr/user/search?key={key}")
    return await resp.json()
