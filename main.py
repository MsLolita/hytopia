import asyncio

from core.autoreger import AutoReger


async def main():
    print("Main <crypto/> moves: https://t.me/+tdC-PXRzhnczNDli\n")

    await AutoReger().start()


if __name__ == '__main__':
    asyncio.run(main())
