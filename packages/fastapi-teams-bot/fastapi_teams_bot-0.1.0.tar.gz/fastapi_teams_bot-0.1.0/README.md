# FastAPI Teams Bot 🤖

[![PyPI version](https://badge.fury.io/py/fastapi-teams-bot.svg)](https://pypi.org/project/fastapi-teams-bot/)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-teams-bot.svg)](https://pypi.org/project/fastapi-teams-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A FastAPI-based framework for building Microsoft Teams bots with pluggable message processing. Perfect for integrating with LangGraph, LangChain, or any custom async message processor.

## ✨ Features

- 🚀 **FastAPI Integration**: Modern, fast, async web framework
- 🔌 **Pluggable Architecture**: Bring your own message processor
- 📎 **File Handling**: Built-in CSV upload/download support
- 🎴 **Adaptive Cards**: Native support for rich interactive cards
- ⚡ **Typing Indicators**: Professional user experience
- 🔐 **Authentication**: Complete Bot Framework authentication handling
- 🧪 **Well Tested**: Comprehensive test coverage
- 📝 **Type Safe**: Full type hints with mypy support

## 🚀 Quick Start

### Installation

```bash
pip install fastapi-teams-bot
```

### Minimal Example

```python
from fastapi_teams_bot import create_teams_bot

async def my_message_processor(user_message, user, conversation_id, metadata):
    """Your custom message processing logic."""
    return {
        "message": f"Hello {user['name']}! You said: {user_message}",
    }

# Create the bot
app = create_teams_bot(my_message_processor)

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
```

### With Environment Variables

```bash
# Set these environment variables:
export MICROSOFT_APP_ID="your-app-id"
export MICROSOFT_APP_PASSWORD="your-password"
export MICROSOFT_APP_TENANT_ID="your-tenant-id"  # Optional
```

```python
from fastapi_teams_bot import create_teams_bot
from my_agent import process_message

app = create_teams_bot(process_message)
```

## 📚 Integration Examples

### With LangGraph

```python
from fastapi_teams_bot import create_teams_bot
from langgraph.graph import StateGraph

# Your LangGraph workflow
graph = StateGraph(...)
# ... define your graph ...

async def process_with_langgraph(user_message, user, conversation_id, metadata):
    """Process message through LangGraph."""
    result = await graph.ainvoke({
        "user_message": user_message,
        "user_id": user["id"],
        "conversation_id": conversation_id,
    })
    
    return {
        "message": result["response"],
        "adaptive_card": result.get("card", {}),
    }

app = create_teams_bot(process_with_langgraph)
```

### With LangChain

```python
from fastapi_teams_bot import create_teams_bot
from langchain.agents import AgentExecutor

agent = AgentExecutor(...)  # Your LangChain agent

async def process_with_langchain(user_message, user, conversation_id, metadata):
    """Process message through LangChain."""
    result = await agent.ainvoke({"input": user_message})
    
    return {"message": result["output"]}

app = create_teams_bot(process_with_langchain)
```

### With Adaptive Cards

```python
async def my_processor(user_message, user, conversation_id, metadata):
    """Return an adaptive card."""
    card = {
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": f"Hello {user['name']}!",
                "size": "Large",
                "weight": "Bolder"
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Click me",
                "data": {"action": "button_clicked"}
            }
        ]
    }
    
    return {
        "message": "Here's an interactive card:",
        "adaptive_card": card,
    }

app = create_teams_bot(my_processor)
```

### With CSV Export

```python
async def export_data(user_message, user, conversation_id, metadata):
    """Export data as CSV."""
    csv_content = "Name,Email,Status\nJohn,john@example.com,Active\n"
    
    return {
        "message": "Here's your data export:",
        "csv": {
            "csv_content": csv_content,
            "filename": "export.csv"
        }
    }

app = create_teams_bot(export_data)
```

### Handling CSV Uploads

```python
async def handle_csv(user_message, user, conversation_id, metadata):
    """Handle uploaded CSV files."""
    if metadata and metadata.get("action_type") == "csv_upload":
        csv_data = metadata["csv_data"]
        
        # Process the CSV
        lines = csv_data.split("\n")
        row_count = len(lines) - 1  # Minus header
        
        return {
            "message": f"Processed CSV with {row_count} rows!",
        }
    
    return {"message": "Please upload a CSV file."}

app = create_teams_bot(handle_csv)
```

## 🔧 Advanced Configuration

```python
from fastapi_teams_bot import TeamsBot, BotConfig

config = BotConfig(
    app_id="your-app-id",
    app_password="your-password",
    app_tenant_id="your-tenant-id",
    endpoint_path="/api/messages",
    enable_typing_indicator=True,
    max_file_size_mb=20,
    supported_file_types=["text/csv", "application/pdf"],
)

bot = TeamsBot(config)
app = bot.create_app(message_processor=my_processor)

# Add custom routes
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## 📖 API Reference

### MessageProcessor Protocol

Your message processor must implement this signature:

```python
async def message_processor(
    user_message: str,
    user: User,  # {"name": str, "id": str}
    conversation_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> MessageResponse:  # {"message": str, "csv": dict, "adaptive_card": dict}
    ...
```

### Metadata Types

**CSV Upload:**
```python
metadata = {
    "action_type": "csv_upload",
    "csv_data": str  # CSV content as string
}
```

**Button Click:**
```python
metadata = {
    "action_type": str,  # e.g., "add_to_cart"
    "action_data": dict  # Full action payload from Adaptive Card
}
```

### BotConfig Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app_id` | str | required | Microsoft App ID |
| `app_password` | str | required | Microsoft App Password |
| `app_tenant_id` | str | None | Microsoft Tenant ID (optional) |
| `endpoint_path` | str | "/api/messages" | Bot endpoint path |
| `enable_typing_indicator` | bool | True | Show typing indicator |
| `max_file_size_mb` | int | 10 | Max file upload size |
| `supported_file_types` | list[str] | ["text/csv"] | Supported MIME types |

## 🧪 Testing

```python
import pytest
from fastapi_teams_bot import User

@pytest.mark.asyncio
async def test_my_processor():
    """Test your message processor."""
    result = await my_message_processor(
        user_message="Hello",
        user={"name": "Test User", "id": "test-123"},
        conversation_id="conv-456",
    )
    
    assert "Hello" in result["message"]
```

## 🎯 Use Cases

This library is perfect for:

- **Customer Support Bots**: Integrate with your support knowledge base
- **Sales Assistants**: Help users browse products and place orders
- **Data Analysis Bots**: Upload CSV files and get insights
- **Workflow Automation**: Trigger actions through conversational interface
- **Internal Tools**: Company directory, IT helpdesk, HR assistant
- **AI Agents**: Connect LLMs (GPT, Claude, etc.) to Teams

## 📦 What's Included

- ✅ Bot endpoint (`/api/messages`)
- ✅ Authentication & token validation
- ✅ Message processing
- ✅ Typing indicators
- ✅ Adaptive Cards
- ✅ CSV upload/download
- ✅ File consent handling
- ✅ Error handling
- ✅ Logging
- ✅ Type definitions

## 🛠️ Development

### Setup

```bash
git clone https://github.com/vishalgoel2/fastapi-teams-bot.git
cd fastapi-teams-bot

# Sync dependencies
uv sync

# Or install in development mode
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=fastapi_teams_bot

# Run with HTML coverage report
uv run pytest tests/ --cov=fastapi_teams_bot --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## 🤝 Contributing

Contributions are welcome! Please check out our [Contributing Guide](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [Microsoft Bot Framework](https://dev.botframework.com/)
- Inspired by the need for simple, flexible Teams bot development

## 📧 Support

- 📖 [Documentation](https://github.com/vishalgoel2/fastapi-teams-bot#readme)
- 🐛 [Issue Tracker](https://github.com/vishalgoel2/fastapi-teams-bot/issues)
- 💬 [Discussions](https://github.com/vishalgoel2/fastapi-teams-bot/discussions)

## 🗺️ Roadmap

- [ ] Support for more file types (PDF, images, etc.)
- [ ] Built-in rate limiting
- [ ] Conversation state management helpers
- [ ] Teams app manifest generator
- [ ] Deployment templates (Azure, Docker)
- [ ] More examples (OpenAI, Anthropic, etc.)

## ⭐ Star History

If you find this project helpful, please consider giving it a star!

---

Made with ❤️ by [Vishal Goel](https://github.com/vishalgoel2)
