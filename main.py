import server
import asyncio

s = server.Server()
asyncio.new_event_loop().run_until_complete(s.runServer())