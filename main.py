import asyncio
import sys

# Import the main function from script
from script import main

# Pygbag compatibility - run the async main function
if sys.platform == "emscripten":
    # Running in browser via Pygbag
    asyncio.ensure_future(main())
else:
    # Running on desktop
    asyncio.run(main())
