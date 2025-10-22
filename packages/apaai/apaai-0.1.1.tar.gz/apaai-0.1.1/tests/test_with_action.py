import asyncio
import responses
from apaai_client import AccountabilityLayer, AccountabilityLayerOptions, Actor, with_action


@responses.activate
def test_with_action_approved_path():
    responses.add(
        responses.POST,
        "http://localhost:8787/actions",
        json={"actionId": "a_1", "status": "approved"},
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        "http://localhost:8787/evidence",
        json={"verified": True},
        status=200,
        content_type="application/json",
    )

    apaai = AccountabilityLayer(AccountabilityLayerOptions())

    async def run():
        return {"id": "ok"}

    async def main():
        res = await with_action(
            apaai=apaai,
            type="send_email",
            actor=Actor(kind="agent", name="bot"),
            target="mailto:client@acme.com",
            params={"subject": "Hi"},
            execute=run,
            evidence_on_success=lambda r: [{"name": "email_sent", "pass": True, "note": f"id={r['id']}"}],
            evidence_on_error=lambda e: [{"name": "email_failed", "pass": False, "note": str(e)}],
        )
        assert res["id"] == "ok"

    asyncio.run(main())


@responses.activate
def test_with_action_requires_approval_calls_hook():
    responses.add(
        responses.POST,
        "http://localhost:8787/actions",
        json={"actionId": "a_2", "status": "requires_approval", "checks": ["reviewer_approval"]},
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        "http://localhost:8787/evidence",
        json={"verified": True},
        status=200,
        content_type="application/json",
    )

    apaai = AccountabilityLayer(AccountabilityLayerOptions())
    called = {"v": False}

    async def on_approval(_info):
        called["v"] = True

    async def run():
        return {}

    async def main():
        await with_action(
            apaai=apaai,
            type="send_email",
            actor=Actor(kind="agent", name="bot"),
            on_approval=on_approval,
            execute=run,
            evidence_on_success=lambda r: [{"name": "email_sent", "pass": True}],
            evidence_on_error=lambda e: [{"name": "email_failed", "pass": False, "note": str(e)}],
        )

    asyncio.run(main())
    assert called["v"] is True
