from fastapi import FastAPI

from app.api import user, post, collaboration

app = FastAPI()
app.include_router(user.router)
app.include_router(post.router)
app.include_router(collaboration.router)

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}