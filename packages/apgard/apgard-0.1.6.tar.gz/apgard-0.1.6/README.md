# Apgard SDK - Client Usage Guide

Apgard is a Python SDK for tracking user interactions with chatbots across a platform. Its primary feature, **Break Tracker**, monitors ongoing sessions and notifies users when a break is due. By default, it reminds users every 3 hours that the chatbot is AI-generated and not human.

---

## Installation

```
pip install apgard
from apgard import ApgardClient
```

# Initialize client
```
apgard_client = ApgardClient(api_key="your-api-key")
```

# Track user activity
```
status = client.breaks.activity(
    user_id="user_123",
    thread_id="conversation_456"
)
```
# Check if break is due
```
if status.break_due:
    print(status.message)  # Show break reminder to user
```
## Basic Usage

```
from apgard import ApgardClient

client = ApgardClient(
    api_key="your-api-key"
)
```

# Track User Activity

Call activity() whenever the user interacts with your chatbot:

```
status = client.breaks.activity(
    user_id="user_123",
    thread_id="conversation_456",  # Optional: tracks per conversation
    metadata={"model": "gpt-4", "temperature": 0.7}  # Optional
)
```

# Handle Break Status

```
status = client.breaks.activity(user_id="user_123")

if status.break_due:
    # Display break reminder
    print(status.message)
else:
    # Continue chatbot interaction
    print("User can continue chatting")
```

## Advanced Usage
Custom Break Duration

Set a custom break threshold (default: 180 minutes / 3 hours):

```
from apgard import BreakTracker

break_tracker = BreakTracker(client=client, break_time_minutes=120)
status = break_tracker.activity(user_id="user_123")
```