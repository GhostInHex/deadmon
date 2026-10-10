# LLM access - LiteLLM proxy (neatHack)

Shared LLM gateway for all teammates (Nova & Claude models). Use this for any
model calls in the project (e.g. deadmon's self-heal fix proposals).

Source: https://neatlogs.com/hackathon/models

## 1. Get your key

- Every teammate must finish **web check-in** first.
- Get your team's key using the **leader's email from web check-in** (solo?
  use your own registered email).
- Make your first call, then save your key privately.

## 2. Set the key in your backend

- Set `LITELLM_API_KEY` in your backend's process environment.
- If you use a `.env` file, load it in your app **and exclude it from Git**
  (add `.env` to `.gitignore`; never commit the key).

## 3. Point your client here

- **API base URL:** `https://litellm.vision.aivar.app/v1`
- Auth: send your key as the Bearer token. OpenAI-compatible API.

## 4. Choose a model

`nova-micro`, `nova-lite`, `nova-pro`, `nova-2-lite`, `claude-haiku`,
`claude-sonnet-4.6`, `claude-opus-4.6` (7 options)

### List available models

```bash
curl https://litellm.vision.aivar.app/v1/models \
  -H "Authorization: Bearer $LITELLM_API_KEY"
```

## Python example

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://litellm.vision.aivar.app/v1",
    api_key=os.environ["LITELLM_API_KEY"],
)

response = client.chat.completions.create(
    model="claude-haiku",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

## cURL example

```bash
curl https://litellm.vision.aivar.app/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku","messages":[{"role":"user","content":"Hello!"}]}'
```

## Budget

**One key. One shared allowance.**

- The provider sets a **$20 budget per team / solo over 30 days**. Requests
  stop when the budget is used.
- **All teammates share it.**
- This is **separate** from the $25 AWS infrastructure allowance, and does
  **not** add Bedrock permissions to your AWS account.

