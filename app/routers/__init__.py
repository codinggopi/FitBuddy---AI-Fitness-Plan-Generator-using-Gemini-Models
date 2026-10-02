from app.routers.web import router as web_router
from app.routers.plans import router as plans_router
from app.routers.nutrition import router as nutrition_router
from app.routers.export import router as export_router

__all__ = ["web_router", "plans_router", "nutrition_router", "export_router"]
