import asyncio
import threading
import atexit
from typing import Any, Coroutine

class _BG:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.t = threading.Thread(target=self._run, daemon=True)
        self.started = False

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        if not self.started:
            self.t.start()
            self.started = True

    def submit_coro(self, coro: Coroutine[Any, Any, Any]) -> None:
        # fire-and-forget
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        if self.started:
            # Simple approach: just stop the loop after a brief delay
            def delayed_stop():
                if self.loop.is_running():
                    self.loop.stop()
            
            # Give tasks a moment to complete, then stop
            self.loop.call_later(0.1, delayed_stop)
            self.t.join(timeout=1)

_bg = _BG()
atexit.register(_bg.stop)
def fire_and_forget(coro: Coroutine[Any, Any, Any]):
    """Schedule an async coroutine with low priority. Non-blocking."""
    _bg.start()
    _bg.submit_coro(_throttled(coro))

async def _throttled(coro: Coroutine[Any, Any, Any]):
    # Simple execution with minimal delay
    await asyncio.sleep(0.001)  # Small delay to deprioritize
    return await coro