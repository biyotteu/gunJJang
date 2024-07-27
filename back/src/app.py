from fastapi import FastAPI
from routers import lectures, schedule
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime
from datetime import datetime
from pytz import timezone
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

datetime.now(timezone('Asia/Seoul'))

app = FastAPI()


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lectures.router, prefix="/lecture", tags=["lectures"])
app.include_router(schedule.router, prefix="/schedule", tags=["schedule"])

app.mount("/static", StaticFiles(directory="static/static"), name="static")

app.mount("/images/", StaticFiles(directory="static/images"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")

# 기타 모든 경로에 대해 React index.html 파일 제공
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse("static/index.html")
