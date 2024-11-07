import asyncio

from fastapi import FastAPI
import uvicorn

from recommend import recommend_by_article_id
from save import seed_mongo

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

async def main():
    await seed_mongo()
    print(recommend_by_article_id(1852640193518112770, 5))

if __name__ == '__main__':
    asyncio.run(main())
    # uvicorn.run(app, host="127.0.0.1", port=8000)
