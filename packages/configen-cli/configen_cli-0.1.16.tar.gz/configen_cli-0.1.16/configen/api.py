import backoff
import httpx
import os

from configen import system, property, decoder


@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
async def validate_api_key(api_key: str):
    try:
        auth = {"Authorization": f"Bearer {api_key}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{property.CONFIGEN_API_URL}/validate-api-key", headers=auth, timeout=100.0)
        if response.status_code == 200:
            return response.status_code, decoder.decode_and_decompress(response.json().get("data"))
        else:
            return response.status_code, {"error": response.text}
    except httpx.RequestError as e:
        print(e)
        return 503, {"error": str(e)}


@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
async def start_session(app_version: str):
    try:
        auth = {"Authorization": f"Bearer {property.CONFIGEN_API_KEY}"}
        data = {
            "app_version": app_version,
            "host_id": property.HOST_ID,
            "system_info": system.get_system_info()
        }
        body = {"data": decoder.compress_and_encode(data)}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{property.CONFIGEN_API_URL}/sessions", headers=auth, json=body,
                                         timeout=100.0)
        if response.status_code == 200:
            return response.status_code, decoder.decode_and_decompress(response.json().get("data"))
        else:
            return response.status_code, {"error": response.text}
    except httpx.RequestError as e:
        print(e)
        return 503, {"error": str(e)}


@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
async def followup_conversation(session_id: str, cli_input: str):
    try:
        auth = {"Authorization": f"Bearer {property.CONFIGEN_API_KEY}"}
        data = {"cli_input": f"{cli_input}. Current dir: {os.getcwd()}"}
        body = {"data": decoder.compress_and_encode(data)}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{property.CONFIGEN_API_URL}/sessions/{session_id}/conversations",
                                         headers=auth, json=body, timeout=100.0)
        if response.status_code == 200:
            return response.status_code, decoder.decode_and_decompress(response.json().get("data"))
        else:
            return response.status_code, {"error": response.text}
    except httpx.RequestError as e:
        print(e)
        return 503, {"error": str(e)}
