import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    # Priority: Cloud injected PORT env var -> settings.PORT -> fallback 8000
    port = int(os.environ.get("PORT", settings.PORT))
    host = os.environ.get("HOST", settings.HOST if not os.environ.get("PORT") else "0.0.0.0")
    
    # Reload when running locally in development
    is_cloud_prod = bool(os.environ.get("PORT"))
    reload = settings.DEBUG or not is_cloud_prod

    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} on http://{host}:{port} ...")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
