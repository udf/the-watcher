import asyncio


OWNER = 232787997


async def loop_runner(logger, loop_body):
  while 1:
    try:
      await loop_body()
    except Exception as e:
      logger.exception('Unhandled exception in loop body')
    await asyncio.sleep(1)
