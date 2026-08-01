from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import applications, jobs, resumes

app = FastAPI(title="Career Quest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(applications.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
