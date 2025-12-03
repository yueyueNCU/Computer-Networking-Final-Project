# 後端
## 創建Virtual Environment (初次創建就好)

1. 在vscode打開命令面板
    ```
    Ctrl+Shift+P
    ```
2. 執行創建環境的命令:
    * 輸入 Python: Create Environment 並選擇它
    * 選擇Venv
    * 選擇一個python解析器
## 進入Virtual Environment (開始寫專案時就要進入)

1. 在vscode powershell中打上
    ```
    .\.venv\Scripts\activate 
    ```
2. 開始下載套件
    ```
    pip install -r requirements.txt
    ```

## 更新或加入套件 
1. 安裝你的Dependency
    ```
    pip install {你的Dependency}
    ```
2. 將Dependency寫入requirements.txt
    ```
    pip freeze > requirements.txt
    ```

## 執行pytest測試
```
cd backend
python -m pytest
```

# 前端
<!-- npm init vue@latest frontend -->
1. 先下載Node.js
https://nodejs.org/zh-tw/download
2. 運行前端伺服器
```
    cd frontend
    npm install
    npm run format
    npm run dev
```