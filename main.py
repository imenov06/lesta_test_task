from fastapi import FastAPI

from pages.router import router as router_pages

app = FastAPI()
app.include_router(router_pages)
