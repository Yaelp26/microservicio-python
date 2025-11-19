from fastapi import APIRouter
import httpx

router = APIRouter()

@router.post("/dispatch")
async def dispatch_webhook(payload: dict):
    partner_url = "https://webhook.site/33f09989-9dab-433d-b92a-9e104baa33b8"  # luego dinámico

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(partner_url, json=payload, timeout=5)
            return {
                "status": "sent",
                "partner_status": response.status_code
            }
        except Exception as e:
            return {"status": "error", "detail": str(e)}
