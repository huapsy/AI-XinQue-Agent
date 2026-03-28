"""执行固定 red team 回归样本。"""

from __future__ import annotations

import json

from app.red_team_runner import run_red_team_suite


def main() -> None:
    print(json.dumps({"results": run_red_team_suite()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
