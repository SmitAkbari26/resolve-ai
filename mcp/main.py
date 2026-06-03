import asyncio
from loader import load_tools
from server import main

load_tools()

if __name__ == "__main__":
    asyncio.run(main())