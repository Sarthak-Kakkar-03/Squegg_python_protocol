import asyncio

from src.squegg import Squegg, SqueggData

async def main():
    squegg = Squegg()
    await squegg.run()

if __name__ == '__main__':
    asyncio.run(main())
