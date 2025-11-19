from fastapi import APIRouter
import httpx

router = APIRouter()

@router.post("/dispatch")
async def dispatch_webhook(payload: dict):
    partner_url = "http://partner.example.com/hook"  # luego dinámico

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(partner_url, json=payload, timeout=5)
            return {
                "status": "sent",
                "partner_status": response.status_code
            }
        except Exception as e:
            return {"status": "error", "detail": str(e)}
