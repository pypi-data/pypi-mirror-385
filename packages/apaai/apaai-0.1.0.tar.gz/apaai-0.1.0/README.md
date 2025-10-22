# apaai-client

[![PyPI version](https://img.shields.io/pypi/v/apaai-client.svg)](https://pypi.org/project/apaai-client/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

**Python SDK for APAAI Protocol**

Open, vendor-neutral SDK for the APAAI Protocol's **Action → Policy → Evidence** loop.

- 📦 **Package**: `apaai-client`
- 🔌 **Protocol**: HTTP/JSON (`/actions`, `/evidence`, `/policy`)
- 🧪 **Minimal & testable**: Class-based API
- 🧱 **License**: Apache-2.0

---

## Install

```bash
pip install apaai-client
```

> **Reference server** (for local development):
>
> ```bash
> cd server
> npm i && npm run dev    # → http://localhost:8787
> ```

---

## Quickstart

```py
from apaai_client import AccountabilityLayer

# Initialize the accountability layer
apaai = AccountabilityLayer(
    endpoint="https://api.apaaiprotocol.org",
    api_key=os.getenv("APAAI_API_KEY")
)

# 1) Propose an action
decision = apaai.propose(
    type="send_email",
    actor={"kind": "agent", "name": "mail-bot"},
    target="mailto:client@acme.com",
    params={"subject": "Proposal"}
)

# 2) Add evidence
apaai.evidence.add(decision["actionId"], [
    {"name": "email_sent", "pass": True, "note": "msgId=123"}
])
```

---

## with_action Helper

The `with_action` helper orchestrates the complete flow:

```py
import asyncio
from apaai_client import AccountabilityLayer, with_action

apaai = AccountabilityLayer(
    endpoint="https://api.apaaiprotocol.org",
    api_key=os.getenv("APAAI_API_KEY")
)

async def main():
    await with_action(
        apaai=apaai,
        type="send_email",
        actor={"kind": "agent", "name": "mail-bot"},
        target="mailto:client@acme.com",
        params={"subject": "Proposal"},
        
        on_approval=async (action_data) => {
            # Handle approval workflow
            await apaai.human.approve(action_data["actionId"], "@reviewer")
        },
        
        execute=async () => {
            # Your business logic
            return await send_email({"to": "client@acme.com", "subject": "Proposal"})
        },
        
        evidence_on_success=lambda result: [
            {"name": "email_sent", "pass": True, "note": f"msgId={result['id']}"}
        ],
        evidence_on_error=lambda err: [
            {"name": "email_failed", "pass": False, "note": str(err)}
        ]
    )

asyncio.run(main())
```

---

## API Reference

### AccountabilityLayer Class

```py
apaai = AccountabilityLayer(
    endpoint: Optional[str] = None, 
    api_key: Optional[str] = None
)
```

### Core Methods

- **`propose(action)`** - Propose an action and get a decision
- **`evidence(action_id, checks)`** - Submit evidence for an action
- **`policy(action_type?)`** - Get policy for an action type
- **`approve(action_id, approver?)`** - Approve an action
- **`reject(action_id, reason?)`** - Reject an action
- **`get_action(action_id)`** - Get action details
- **`list_actions(filters?)`** - List actions with filters
- **`get_evidence(action_id)`** - Get evidence for an action
- **`set_policy(policy)`** - Set a policy

### Manager Interfaces

- **`apaai.policies.evaluate(action_id)`** - Evaluate policy for an action
- **`apaai.policies.enforce(action_type)`** - Enforce policy for an action type
- **`apaai.policies.set(policy)`** - Set a policy
- **`apaai.human.approve(action_id, approver?)`** - Approve an action
- **`apaai.human.reject(action_id, reason?)`** - Reject an action
- **`apaai.evidence.add(action_id, checks)`** - Add evidence for an action
- **`apaai.evidence.get(action_id)`** - Get evidence for an action
- **`apaai.actions.get(action_id)`** - Get action details
- **`apaai.actions.list(filters?)`** - List actions with filters

---

## Examples

### Basic Flow

```py
from apaai_client import AccountabilityLayer

apaai = AccountabilityLayer(endpoint="http://localhost:8787")

# Propose action
decision = apaai.propose(
    type="send_email",
    actor={"kind": "agent", "name": "mail-bot"},
    target="mailto:client@acme.com",
    params={"subject": "Proposal"}
)

# Handle approval if required
if decision["status"] == "requires_approval":
    apaai.approve(decision["actionId"], "@reviewer")

# Submit evidence
apaai.evidence.add(decision["actionId"], [
    {"name": "email_sent", "pass": True, "note": "msgId=123"}
])
```

### Using Manager Interfaces

```py
# Policy management
policy = apaai.policies.enforce("send_email")
apaai.policies.set({"rules": [...]})

# Human-in-the-loop
apaai.human.approve(action_id, "@reviewer")
apaai.human.reject(action_id, "Invalid recipient")

# Evidence management
apaai.evidence.add(action_id, [
    {"name": "email_sent", "pass": True, "note": "msgId=123"}
])
evidence = apaai.evidence.get(action_id)

# Action management
action = apaai.actions.get(action_id)
actions = apaai.actions.list({"type": "send_email"})
```

---

## Types

```py
from typing import Dict, List, Optional, Any

Actor = Dict[str, Any]  # {"kind": "agent", "name": "mail-bot", "provider": "openai"}

Action = Dict[str, Any]  # {
    "id": str,
    "timestamp": str,
    "type": str,
    "actor": Actor,
    "target": Optional[str],
    "params": Optional[Dict[str, Any]],
    "status": Optional[str],
    "checks": Optional[List[str]]
}

Check = Dict[str, Any]  # {"name": str, "pass": bool, "note": Optional[str]}

Evidence = Dict[str, Any]  # {"actionId": str, "checks": List[Check]}

Decision = Dict[str, Any]  # {"status": str, "checks": Optional[List[str]]}

PolicyRule = Dict[str, Any]  # {
    "when": Optional[Dict[str, str]],  # {"action": str} or {"actionType": str}
    "require": Optional[List[str]],
    "mode": Optional[str]  # "enforce" | "observe"
}

Policy = Dict[str, Any]  # {"rules": List[PolicyRule]}
```

---

## Testing

```bash
# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=apaai_client

# Run specific test file
python -m pytest tests/test_client.py
```

---

## Build & Publish

```bash
# Build the package
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

---

## License

Apache-2.0