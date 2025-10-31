import os
from asyncio import TaskGroup

import httpx
from dotenv import load_dotenv

_ = load_dotenv()

API_KEY = os.getenv("JAZZHR_API_KEY")
if API_KEY is None:
    raise ValueError("JAZZHR_API_KEY not found in environment variables")

BASE_URL = "https://api.resumatorapi.com/v1"
OUTDIR = "data/resumes"
MAX_WORKERS = 8  # tune for your bandwidth/API limits
REQUEST_TIMEOUT = 45
RETRY_MAX = 4

APP_ID = "prospect_20251029115427_7TKL8P0XNF0OMBLG"
URL = f"{BASE}/applicants/{APP_ID}/resume?apikey={API_KEY}"


def get_client():
    return httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=REQUEST_TIMEOUT,
        params={"apikey": API_KEY},
    )


async def download_task(_id: int):
    # download task
    ...


IDS = [1, 2, 3, 4]


# check https://docs.python.org/3/library/asyncio-queue.html for N workers at a time
async def download_all_concurrently():
    async with TaskGroup() as tg:
        for id in IDS:
            _ = tg.create_task(download_task(id))


async def main():
    client = get_client()

    res = await client.get(f"/applicants/{APP_ID}/resume")

    print(f"Response status: {res.status_code}")

    if res.status_code == 200:
        with open("data/test_resume2.pdf", "wb") as f:
            _ = f.write(res.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
