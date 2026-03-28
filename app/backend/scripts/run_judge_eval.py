"""运行单次 LLM-as-Judge 评估。"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from openai import AsyncAzureOpenAI

from app.evaluation_helpers import run_llm_judge


async def _run(messages_path: Path, session_id: str) -> None:
    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    try:
        messages = json.loads(messages_path.read_text(encoding="utf-8"))
        result = await run_llm_judge(
            client=client,
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            session_id=session_id,
            messages=messages,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        await client.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("messages_path")
    parser.add_argument("--session-id", default="sample-session")
    args = parser.parse_args()
    asyncio.run(_run(Path(args.messages_path), args.session_id))


if __name__ == "__main__":
    main()
