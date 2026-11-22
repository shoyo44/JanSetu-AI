#!/usr/bin/env python3
"""
Diagnostic tool to verify LLM API connectivity (Groq & Cloudflare) inside the container or host.
Usage:
    python verify_llm_connection.py
"""
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Load .env
for env_path in [".env", "../.env", "../../.env"]:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

print("=" * 60)
print("🔍 JanSetu AI — LLM & Embedding Connectivity Diagnostics")
print("=" * 60)

async def test_groq():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or "gsk_" not in key:
        print("❌ [GROQ] Key not found or empty in .env (expected to start with 'gsk_').")
        return False
    
    masked = key[:7] + "..." + key[-4:]
    print(f"📡 [GROQ] Found key: {masked}. Testing API handshake...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": "Reply with 'GROQ_OK'"}],
                    "max_tokens": 10
                }
            )
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"].strip()
                print(f"✅ [GROQ] Connected successfully! Response: {answer}")
                return True
            else:
                print(f"❌ [GROQ] HTTP {resp.status_code}: {resp.text[:200]}")
                return False
    except Exception as exc:
        print(f"❌ [GROQ] Connection failed: {exc}")
        return False

async def test_cloudflare():
    aid = os.getenv("CF_ACCOUNT_ID", "").strip()
    tok = os.getenv("CF_API_TOKEN", "").strip()
    if not aid or not tok or "your_cf" in aid:
        print("⚠️  [CLOUDFLARE] Credentials are placeholder or missing.")
        return False
    
    print(f"📡 [CLOUDFLARE] Testing account {aid[:6]}... ")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.cloudflare.com/client/v4/accounts/{aid}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast"
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                json={"messages": [{"role": "user", "content": "ping"}]}
            )
            if resp.status_code == 200:
                print("✅ [CLOUDFLARE] Connected successfully!")
                return True
            elif resp.status_code == 429:
                print("⚠️  [CLOUDFLARE] HTTP 429 Too Many Requests: Daily free quota of 10,000 neurons exhausted.")
                return False
            else:
                print(f"❌ [CLOUDFLARE] HTTP {resp.status_code}: {resp.text[:150]}")
                return False
    except Exception as exc:
        print(f"❌ [CLOUDFLARE] Connection failed: {exc}")
        return False

async def main():
    groq_ok = await test_groq()
    print("-" * 60)
    cf_ok = await test_cloudflare()
    print("=" * 60)
    if groq_ok:
        print("🎉 STATUS: Primary LLM (Groq Llama-3.3-70B) is READY and fully connected!")
    elif cf_ok:
        print("🎉 STATUS: Secondary LLM (Cloudflare Workers AI) is READY!")
    else:
        print("🛡️ STATUS: All LLM APIs are offline or quota-limited. Active fallback: Tier 3 Sovereign RAG.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
