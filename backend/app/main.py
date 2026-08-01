from fastapi import FastAPI

from app.routers import applications, jobs, resumes

app = FastAPI(title="Career Quest API")

app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(applications.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
