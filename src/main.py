import os
from dotenv import load_dotenv, find_dotenv

from tools import get_latest_traffic_log_file, read_file_content
from proxyAgent import run_proxy_agent
import asyncio

async def main():
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path, override=True)
    print(f"TRAFFIC_LOG_DIR: {os.getenv("LOGS_DIRECTORY")}")

    # Get the latest traffic log file
    latest_log = get_latest_traffic_log_file(os.getenv("LOGS_DIRECTORY"))
    print(f"Latest traffic log file: {latest_log}")
    file_content = read_file_content(latest_log)
    await run_proxy_agent(file_content)

if __name__ == "__main__":
    asyncio.run(main())
