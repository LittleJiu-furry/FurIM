import asyncio
from server import Server

s = Server(moreLog=True)
asyncio.new_event_loop().run_until_complete(s.runServer())
