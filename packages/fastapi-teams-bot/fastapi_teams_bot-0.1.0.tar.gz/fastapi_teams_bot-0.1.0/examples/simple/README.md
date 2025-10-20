# Simple Echo Bot Example

A minimal Teams bot that echoes back what you say.

## Setup

1. Set environment variables:
```bash
export MICROSOFT_APP_ID="your-app-id"
export MICROSOFT_APP_PASSWORD="your-password"
```

2. Install dependencies:
```bash
pip install fastapi-teams-bot uvicorn
```

3. Run the bot:
```bash
python main.py
```

4. Test with Teams emulator or deploy to Azure

## How it works

The echo processor is a simple async function that returns the user's message:

```python
async def echo_processor(user_message, user, conversation_id, metadata):
    return {"message": f"You said: {user_message}"}
```

That's all you need to create a working Teams bot!
