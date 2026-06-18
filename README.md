# 法律申論題交流平台

以 Streamlit 打造的法律申論題眾包網站。使用者上傳申論作答可賺取代幣（+3），再用代幣解鎖查看他人作答（-1）。帳號與上傳者代號皆經去識別化處理。

## 功能

- **帳號系統**：登入／註冊合一頁；密碼 SHA-256 雜湊；註冊送 3 代幣並自動登入
- **導覽**：`st.navigation`；未登入僅「登入／註冊」；登入後顯示首頁與功能頁
- **上傳作答**：依 `config/taxonomy.json` 選分類；本卷分數／等第；防重複與相似度檢查
- **瀏覽題庫**：六欄篩選後顯示公開題目與作答；1 代幣解鎖
- **個人頁面**：代幣、上傳筆數、已解鎖清單

## 技術棧

- Python + Streamlit（>=1.36）
- 資料：JSON + CSV（無資料庫）
- 題庫目錄：`config/taxonomy.json`（可 commit）
- 使用者資料：`data/`（`.gitignore`，勿 commit）

## 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 專案結構

```
law-essay-platform/
├── app.py
├── views/home.py
├── pages/
│   ├── login.py       # 登入／註冊
│   ├── upload.py
│   ├── browse.py
│   └── profile.py
├── config/taxonomy.json
├── utils/
│   ├── session.py
│   ├── user_store.py
│   ├── nav_pages.py
│   ├── taxonomy.py
│   ├── answers_store.py
│   └── questions_store.py
├── data/              # 本機執行時自動建立（不進 git）
├── requirements.txt
└── README.md
```

## 上傳 GitHub

```bash
cd law-essay-platform
git init
git add .
git status   # 確認沒有 data/ 被加入
git commit -m "Initial commit: law essay platform"
git branch -M main
git remote add origin https://github.com/你的帳號/law-essay-platform.git
git push -u origin main
```

**推送前檢查**：`git status` 不應出現 `data/users.json`、`data/answers.csv` 等使用者資料。

## 部署 Streamlit Community Cloud

1. 將 repo 推到 GitHub（見上）
2. 前往 [share.streamlit.io](https://share.streamlit.io) → New app
3. 設定：
   - Repository：你的 repo
   - Branch：`main`
   - Main file path：`app.py`
4. **Secrets**（Settings → Secrets）加入：

```toml
SESSION_SECRET = "隨機長字串請自行產生"
```

5. Deploy

### 雲端部署限制（必讀）

| 項目 | 說明 |
|------|------|
| `data/` | 不進 git，部署後為**空資料**；需重新註冊、上傳 |
| 持久化 | 免費版重啟可能清空 `data/`；正式上線需另規劃儲存 |
| 題目 | 管理者手動維護 `data/questions.json`（或之後管理者頁） |
| `fcntl` | `user_store.py` 檔案鎖在 Linux 可用；Windows 本機開發需注意 |

## 代幣規則

- 註冊：+3
- 上傳成功：+3
- 解鎖：-1

## 安全注意事項

- `data/` 勿 commit
- 上線務必設定 `SESSION_SECRET`（見 `.streamlit/secrets.toml.example`）
- 登入錯誤訊息不區分帳號／密碼

## 驗收

見 [DEMO_CHECKLIST.md](./DEMO_CHECKLIST.md)、[HANDOFF.md](./HANDOFF.md)。
