"""简单测试脚本: 验证 Qwen 与 DeepSeek API Key 是否能正常调用。

使用方式:
  python test_providers.py

输出示例:
  === Provider: deepseek ===
  Status: SUCCESS | Latency: 0.85s | Model: deepseek-chat
  Response Preview: OK

  === Provider: qwen3 ===
  Status: FAILED | Latency: 0.12s | Model: qwen-plus
  Error: ...

注意:
- 仅做最小化一次对话调用,减少额度消耗。
- 请确保 .env 文件已存在并包含 QWEN_API_KEY 和 DEEPSEEK_API_KEY。
- 脚本不会写入任何敏感数据。
"""
from __future__ import annotations
import os
import time
import traceback
from typing import Dict, Any

try:
    from dotenv import load_dotenv
except ImportError:
    print("[WARN] 未安装 python-dotenv, 正在跳过自动加载 .env。执行 pip install python-dotenv 可启用。")
    def load_dotenv():
        pass

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    print("[ERROR] 未安装 langchain-openai，请先执行: pip install langchain-openai")
    raise

# 强制加载 .env
load_dotenv()

DEEPSEEK_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
QWEN_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
QWEN_KEY = os.getenv("QWEN_API_KEY")

PROMPT = "请只回复: OK"  # 简短提示词以减少计费


def test_provider(name: str) -> Dict[str, Any]:
    start = time.perf_counter()
    base_url = None
    api_key = None
    model = None

    if name == "deepseek":
        base_url = DEEPSEEK_BASE
        api_key = DEEPSEEK_KEY
        model = DEEPSEEK_MODEL
    elif name in ("qwen", "qwen3"):
        base_url = QWEN_BASE
        api_key = QWEN_KEY
        model = QWEN_MODEL
    else:
        return {"provider": name, "status": "UNSUPPORTED"}

    if not api_key:
        return {
            "provider": name,
            "status": "NO_KEY",
            "error": f"未找到 {name.upper()} API Key",
        }

    try:
        llm = ChatOpenAI(model=model, temperature=0, api_key=api_key, base_url=base_url)
        resp = llm.invoke(PROMPT)
        latency = time.perf_counter() - start
        content = getattr(resp, "content", "<no content>")
        return {
            "provider": name,
            "status": "SUCCESS" if content else "EMPTY",
            "latency": round(latency, 3),
            "model": model,
            "response_preview": content[:200],
        }
    except Exception as e:
        latency = time.perf_counter() - start
        return {
            "provider": name,
            "status": "FAILED",
            "latency": round(latency, 3),
            "model": model,
            "error": str(e),
            "trace": traceback.format_exc()[:800],
        }


def pretty_print(result: Dict[str, Any]):
    print(f"=== Provider: {result['provider']} ===")
    if result['status'] == "SUCCESS":
        print(f"Status: SUCCESS | Latency: {result['latency']}s | Model: {result['model']}")
        print("Response Preview:", result.get("response_preview", "<none>")[:200])
    elif result['status'] == "NO_KEY":
        print("Status: NO_KEY |", result.get("error"))
    elif result['status'] == "FAILED":
        print(f"Status: FAILED | Latency: {result['latency']}s | Model: {result['model']}")
        print("Error:", result.get("error"))
        if '402' in str(result.get('error', '')):
            print("Hint: 可能是余额/配额不足 (402)。请检查账户额度或更换其它模型。")
    else:
        print("Status:", result['status'])
    print()


def main():
    print("开始测试 DeepSeek 与 Qwen3 API 可用性\n")
    print(f"DeepSeek Key Present: {'YES' if DEEPSEEK_KEY else 'NO'}")
    print(f"Qwen3 Key Present: {'YES' if QWEN_KEY else 'NO'}\n")

    for provider in ["deepseek", "qwen3"]:
        res = test_provider(provider)
        pretty_print(res)

    print("测试完成。")
    print("如果均为 SUCCESS，则两个 API Key 可正常使用。")
    print("若出现 402 或 FAILED，请检查对应平台余额或网络连通性。")


if __name__ == "__main__":
    main()
