# LangGraph Integration Example

This example shows how to integrate `fastapi-teams-bot` with a LangGraph workflow.

## Setup

1. Set environment variables:
```bash
export MICROSOFT_APP_ID="your-app-id"
export MICROSOFT_APP_PASSWORD="your-password"
```

2. Install dependencies:
```bash
pip install fastapi-teams-bot uvicorn langgraph
```

3. Run the bot:
```bash
python main.py
```

## How it works

The example includes:

- **Command handling** (`/help`, `/new`)
- **CSV upload processing**
- **Adaptive Cards** with interactive buttons
- **LangGraph integration** (simulated - replace with your workflow)

## Integration with Your LangGraph Workflow

Replace the simulated `process_user_message` function with your actual LangGraph workflow:

```python
from your_agent.workflow import process_user_message  # Your actual workflow

app = create_teams_bot(process_user_message)
```

Your workflow function should match this signature:

```python
async def process_user_message(
    user_message: str,
    user: dict,  # {"name": str, "id": str}
    conversation_id: str,
    metadata: Optional[dict] = None,
) -> dict:  # {"message": str, "csv": dict, "adaptive_card": dict}
    # Your LangGraph workflow here
    pass
```

## Features Demonstrated

- Text message handling
- Command processing
- CSV file uploads
- Adaptive Cards with actions
- Button click handling
- User feedback collection
