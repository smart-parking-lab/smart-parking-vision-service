from fastapi import FastAPI
from app.core.cors import setup_cors
from app.api.health import router as health_router
from app.api.parking_sessions import router as sessions_router
from app.api.invoices import router as invoices_router
from app.api.parking_slots import router as slots_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Parking — BE Core",
        description="Backend Core xử lý business logic, MQTT, DB cho hệ thống bãi đỗ xe thông minh",
        version="1.0.0",
    )

    setup_cors(app)

    # API routes cho Dashboard gọi
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(invoices_router, prefix="/api/v1")
    app.include_router(slots_router, prefix="/api/v1")

    @app.get("/", tags=["Root"])
    def root():
        return {"status": "ok", "service": "BE Core — Smart Parking"}

    return app


app = create_app()
