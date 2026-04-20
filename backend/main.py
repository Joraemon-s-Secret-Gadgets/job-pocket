from fastapi import FastAPI

# router
from routers.health import router

app = FastAPI()

app.include_router(router)
