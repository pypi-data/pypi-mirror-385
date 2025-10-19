import asyncio
from core_registry_client import RegistryClient

async def test_sdk():
    async with RegistryClient(base_url="http://localhost:8000") as client:
        print(" SDK client created")
        index = await client.get_index()
        print(f" Index: v1={index.tracks['v1'].count}, v2={index.tracks['v2'].count}")
        
asyncio.run(test_sdk())
