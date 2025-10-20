from typing import List

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    wt_ai_keys: List[str] = []
    wt_model: str = "qwen3-max"   # ← 默认改为 qwen3-max
    wt_proxy: str = ""            # ← 保留字段但代码中已不再使用
    wt_history_lens: int = 1000
    wt_push_cron: str = "0 14,22 * * *"
    wt_group_list: List[int] = []