from __future__ import annotations
from typing import Any, Callable, Awaitable, Dict, List, Optional
import asyncio
from .client import AccountabilityLayer


async def with_action(
    *,
    apaai: AccountabilityLayer,
    type: str,
    actor: Dict[str, Any],
    target: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    id: Optional[str] = None,
    timestamp: Optional[str] = None,
    on_approval: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    execute: Optional[Callable[[], Awaitable[Any]]] = None,
    evidence_on_success: Optional[Callable[[Any], List[Dict[str, Any]]]] = None,
    evidence_on_error: Optional[Callable[[Exception], List[Dict[str, Any]]]] = None,
) -> Any:
    decision = apaai.propose(type=type, actor=actor, target=target, params=params, id=id, timestamp=timestamp)

    if decision.get("status") == "rejected":
        raise RuntimeError(f"APAAI decision rejected for {decision.get('actionId')}")

    if decision.get("status") == "requires_approval" and on_approval:
        await on_approval({"actionId": decision["actionId"], "checks": decision.get("checks")})

    try:
        result = await execute() if execute else None
        
        checks = []
        if result is not None and evidence_on_success:
            checks = evidence_on_success(result)
        elif result is not None:
            checks = [{"name": "action_executed", "pass": True}]
        else:
            checks = [{"name": "action_executed", "pass": True}]
            
        apaai.evidence(decision["actionId"], checks)
        return result
    except Exception as err:  # noqa: BLE001
        checks = evidence_on_error(err) if evidence_on_error else [{"name": "action_failed", "pass": False, "note": str(err)}]
        try:
            apaai.evidence(decision["actionId"], checks)
        except Exception:
            pass
        raise
