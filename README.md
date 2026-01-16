# 游泳池收費收據系統 (展示版)

臺北市立大學游泳池收費收據管理系統 - **展示版本（無須登入）**

## 功能特色

- 📝 **收據開立**: 選擇收費項目、輸入金額，快速開立收據
- 🖨️ **收據列印**: 產生 A4 格式收據，可直接列印或下載 PDF
- 📊 **統計報表**: 日報表、月報表，支援匯出 Excel
- ✅ **出納驗證**: 出納人員逐筆或批次驗證收據
- ❌ **作廢管理**: 申請作廢需經審核，保留完整稽核軌跡
- 🔧 **系統管理**: 收費項目與使用者管理

## 展示模式說明

⚠️ **此版本為展示用**，已移除登入驗證功能。所有功能可直接使用。

---

## 本地開發

### 安裝套件

```bash
pip install -r requirements.txt
```

### 啟動系統

```bash
python run.py
```

或在 Windows 上執行 `start.bat`

系統將啟動於 http://127.0.0.1:8989

---

## Zeabur 雲端部署

### 方法一：透過 GitHub 部署（推薦）

1. **初始化 Git 並推送到 GitHub**
   ```bash
   cd swim
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/swim-receipt.git
   git push -u origin main
   ```

2. **登入 Zeabur**
   - 前往 https://dash.zeabur.com
   - 使用 GitHub 帳號登入

3. **建立新專案**
   - 點擊「New Project」
   - 選擇「Deploy from GitHub」
   - 選擇您的 `swim-receipt` Repository
   - Zeabur 會自動偵測為 Python 專案並開始部署

4. **產生公開網址**
   - 部署完成後，點擊您的服務
   - 前往「Networking」標籤
   - 點擊「Generate Domain」
   - 即可取得 `*.zeabur.app` 網址

### 方法二：透過 Zeabur CLI 部署

```bash
# 安裝 Zeabur CLI
npm install -g zeabur

# 登入
zeabur login

# 部署
zeabur deploy
```

### 環境變數（可選）

在 Zeabur Dashboard 的「Variables」中可設定：

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| SECRET_KEY | Flask 密鑰 | 自動生成 |
| FLASK_ENV | 執行環境 | production |

---

## 收費項目

系統預設包含以下收費項目：

### 入場券
- 學生: $50
- 教職員: $80
- 校外人士: $150
- 敬老/愛心優惠: $50

### 票券
- 月票-學生: $800
- 月票-教職員: $600
- 月票-校外人士: $2,000
- 季票-學生: $2,000
- 10次券-學生: $400

### 租借
- 水道租借: $500/時
- 置物櫃: $50

可在「系統管理」→「收費項目管理」中自行調整

---

## 技術架構

- **Backend**: Python Flask 3.0
- **Database**: SQLite
- **PDF**: ReportLab
- **Excel**: openpyxl
- **WSGI**: Gunicorn (production)

## 目錄結構

```
swim/
├── app/
│   ├── __init__.py      # Flask 應用初始化
│   ├── config.py        # 配置檔
│   ├── models/          # 資料模型
│   ├── routes/          # 路由控制
│   ├── services/        # 業務邏輯
│   └── templates/       # HTML 模板
├── data/                # SQLite 資料庫
├── requirements.txt     # Python 相依套件
├── Procfile            # Zeabur 啟動指令
├── runtime.txt         # Python 版本
└── run.py              # 應用程式入口
```

---

開發日期: 2026-01-16
