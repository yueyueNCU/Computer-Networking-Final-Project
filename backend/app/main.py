# Path: app/main.py
from fastapi import FastAPI
from app.routers import map
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import Router 和原本的依賴定義
# 注意：這裡使用 "from app..." 表示執行時的根目錄必須是 app 的上一層 (backend)
from app.routers.queues import queue_router, get_queue_service
from app.routers.map import map_router, get_map_service
from app.routers.table import table_router, get_table_service

# Import 我們剛剛寫好的記憶體版 Service
# 提醒：請確保您已建立 app/infrastructure 資料夾，並將 memory_adapters.py 放在其中
from app.repositories.fake_all_repo import get_memory_queue_service, get_memory_map_service, get_memory_table_service

app = FastAPI(
    title="排隊系統 API (Dev Mode)",
    description="目前使用記憶體模擬資料庫，重啟後資料會重置",
    version="0.1.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
# 註冊 Router
app.include_router(queue_router, tags=["Queues"])
app.include_router(map_router, tags=["Restaurants"])
app.include_router(table_router, tags=["Tables"])

# 您可以透過環境變數控制，或者在開發階段直接寫死
USE_MOCK_DB = os.getenv("USE_MOCK_DB", "True").lower() == "true"

if USE_MOCK_DB:
    print("⚠️  正在使用 In-Memory 模擬資料庫模式")
    print("⚠️  所有排隊資料將儲存在 RAM 中，重啟後消失")
    # 這行程式碼的作用跟 TestClient 的 override 一模一樣
    # 它告訴 FastAPI: 只要有人要 get_queue_service，就給他 get_memory_queue_service
    app.dependency_overrides[get_queue_service] = get_memory_queue_service
    app.dependency_overrides[get_map_service] = get_memory_map_service
    app.dependency_overrides[get_table_service] = get_memory_table_service
else:
    print("[Mode] 使用 真實資料庫 (Production)")
    # app.dependency_overrides[get_queue_service] = get_real_queue_service
    # app.dependency_overrides[get_map_service] = get_real_map_service
    pass 
    # 注意：如果你在 Router 定義的 get_queue_service 預設就是拋出 Error，
    # 那這裡的 else 必須要 override，否則程式會報錯 NotImplementedError。


@app.get("/")
def root():
    return {"message": "Server is running!", "mode": "Memory Mock" if USE_MOCK_DB else "Production"}

if __name__ == "__main__":
    # 本地開發啟動
    # 因為檔案在 app/main.py，所以 import path 應該是 "app.main:app"
    # 執行指令建議：在 backend/ 目錄下執行 `python -m app.main` 或直接用 uvicorn 指令
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)