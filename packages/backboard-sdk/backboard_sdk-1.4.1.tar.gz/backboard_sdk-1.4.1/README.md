# Backboard Python SDK

A developer-friendly Python SDK for the Backboard API. Build conversational AI applications with persistent memory and intelligent document processing.

> New to Backboard? We include $10 in free credits to get you started and support 1,800+ LLMs across major providers.

## New in v1.4.1

- **Memory Support**: Add persistent memory to assistants with automatic context retrieval
- **Memory Modes**: Control memory behavior with Auto, Readonly, and off modes
- **Memory Statistics**: Track usage and limits

## Installation

```bash
pip install backboard-sdk
```


## Quick Start

```python
import asyncio
from backboard import BackboardClient

async def main():
    client = BackboardClient(api_key="your_api_key_here")

    assistant = await client.create_assistant(
        name="Support Bot",
        description="A helpful customer support assistant",
    )

    thread = await client.create_thread(assistant.assistant_id)

    response = await client.add_message(
        thread_id=thread.thread_id,
        content="Hello! Can you help me with my account?",
        llm_provider="openai",
        model_name="gpt-4o",
        stream=False,
    )

    print(response.latest_message.content)

    # Streaming
    async for event in await client.add_message(
        thread_id=thread.thread_id,
        content="Stream me a short response",
        stream=True,
    ):
        if event.get("type") == "content_streaming":
            print(event.get("content", ""), end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

### Memory (NEW in v1.4.0)
- **Persistent Memory**: Store and retrieve information across conversations
- **Automatic Context**: Enable memory to automatically search and use relevant context
- **Manual Management**: Full control with add, update, delete, and list operations
- **Memory Modes**: Auto (search + write), Readonly (search only), or off

### Assistants
- Create, list, get, update, and delete assistants
- Configure custom tools and capabilities
- Upload documents for assistant-level context

### Threads
- Create conversation threads under assistants
- Maintain persistent conversation history
- Support for message attachments

### Documents
- Upload documents to assistants or threads
- Automatic processing and indexing for RAG
- Support for PDF, Office files, text, and more
- Real-time processing status tracking

### Messages
- Send messages with optional file attachments
- Streaming and non-streaming responses
- Tool calling support
- Custom LLM provider and model selection

## API Reference

### Client Initialization

```python
client = BackboardClient(api_key="your_api_key")
# or use as an async context manager
# async with BackboardClient(api_key="your_api_key") as client:
#     ...
```

### Assistants

```python
# Create assistant
assistant = await client.create_assistant(
    name="My Assistant",
    description="Assistant description",
    tools=[tool_definition],  # Optional
)

# List assistants
assistants = await client.list_assistants(skip=0, limit=100)

# Get assistant
assistant = await client.get_assistant(assistant_id)

# Update assistant
assistant = await client.update_assistant(
    assistant_id,
    name="New Name",
    description="New description",
)

# Delete assistant
result = await client.delete_assistant(assistant_id)
```

### Threads

```python
# Create thread
thread = await client.create_thread(assistant_id)

# List threads
threads = await client.list_threads(skip=0, limit=100)

# Get thread with messages
thread = await client.get_thread(thread_id)

# Delete thread
result = await client.delete_thread(thread_id)
```

### Messages

```python
# Send message
response = await client.add_message(
    thread_id=thread_id,
    content="Your message here",
    files=["path/to/file.pdf"],  # Optional attachments
    llm_provider="openai",  # Optional
    model_name="gpt-4o",  # Optional
    stream=False,
    memory="Auto",  # Optional: "Auto", "Readonly", or "off" (default)
)

# Streaming messages
async for chunk in await client.add_message(thread_id, content="Hello", stream=True):
    if chunk.get('type') == 'content_streaming':
        print(chunk.get('content', ''), end='', flush=True)
```

### Tool Integration (Simplified in v1.3.3)

#### Tool Definitions
```python
# Use plain JSON objects (no verbose SDK classes needed!)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

assistant = await client.create_assistant(
    name="Weather Assistant",
    tools=tools,
)
```

#### Tool Call Handling
```python
import json

# Enhanced object-oriented access with automatic JSON parsing
response = await client.add_message(
    thread_id=thread_id,
    content="What's the weather in San Francisco?",
    stream=False
)

if response.status == "REQUIRES_ACTION" and response.tool_calls:
    tool_outputs = []
    
    # Process each tool call
    for tc in response.tool_calls:
        if tc.function.name == "get_current_weather":
            # Get parsed arguments (required parameters are guaranteed by API)
            args = tc.function.parsed_arguments
            location = args["location"]
            
            # Execute your function and format the output
            weather_data = {
                "temperature": "68°F",
                "condition": "Sunny",
                "location": location
            }
            
            tool_outputs.append({
                "tool_call_id": tc.id,
                "output": json.dumps(weather_data)
            })
    
    # Submit the tool outputs back to continue the conversation
    final_response = await client.submit_tool_outputs(
        thread_id=thread_id,
        run_id=response.run_id,
        tool_outputs=tool_outputs
    )
    
    print(final_response.latest_message.content)
```

### Memory

```python
# Add a memory
await client.add_memory(
    assistant_id=assistant_id,
    content="User prefers Python programming",
    metadata={"category": "preference"}
)

# Get all memories
memories = await client.get_memories(assistant_id)
for memory in memories.memories:
    print(f"{memory.id}: {memory.content}")

# Get specific memory
memory = await client.get_memory(assistant_id, memory_id)

# Update memory
await client.update_memory(
    assistant_id=assistant_id,
    memory_id=memory_id,
    content="Updated content"
)

# Delete memory
await client.delete_memory(assistant_id, memory_id)

# Get memory stats
stats = await client.get_memory_stats(assistant_id)
print(f"Total memories: {stats.total_memories}")

# Use memory in conversation
response = await client.add_message(
    thread_id=thread_id,
    content="What do you know about me?",
    memory="Auto"  # Enable memory search and automatic updates
)
```


### Documents

```python
# Upload document to assistant
document = await client.upload_document_to_assistant(
    assistant_id=assistant_id,
    file_path="path/to/document.pdf",
)

# Upload document to thread
document = await client.upload_document_to_thread(
    thread_id=thread_id,
    file_path="path/to/document.pdf",
)

# List assistant documents
documents = await client.list_assistant_documents(assistant_id)

# List thread documents
documents = await client.list_thread_documents(thread_id)

# Get document status
document = await client.get_document_status(document_id)

# Delete document
result = await client.delete_document(document_id)
```

## Error Handling

The SDK includes comprehensive error handling:

```python
from backboard import (
    BackboardAPIError,
    BackboardValidationError,
    BackboardNotFoundError,
    BackboardRateLimitError,
    BackboardServerError,
)

async def demo_err():
    try:
        await client.get_assistant("invalid_id")
    except BackboardNotFoundError:
        print("Assistant not found")
    except BackboardValidationError as e:
        print(f"Validation error: {e}")
    except BackboardAPIError as e:
        print(f"API error: {e}")
```

## Supported File Types

The SDK supports uploading the following file types:
- PDF files (.pdf)
- Microsoft Office files (.docx, .xlsx, .pptx, .doc, .xls, .ppt)
- Text files (.txt, .csv, .md, .markdown)
- Code files (.py, .js, .html, .css, .xml)
- JSON files (.json, .jsonl)

## Requirements

- Python 3.8+
- httpx >= 0.27.0

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://backboard.io/docs
- Email: support@backboard.io
