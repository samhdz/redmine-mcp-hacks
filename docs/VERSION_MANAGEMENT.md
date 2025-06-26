# 版本管理指南

本文件說明如何在 Redmine MCP 專案中管理版本號。

## 📍 版本設定位置

### 主要版本來源
- **`pyproject.toml`** - 套件版本的**唯一來源**
  ```toml
  [project]
  version = "0.1.0"
  ```

### 動態版本讀取
- **`src/redmine_mcp/__init__.py`** - 自動從 `pyproject.toml` 讀取版本
  ```python
  try:
      from importlib.metadata import version
      __version__ = version("redmine-mcp")
  except ImportError:
      __version__ = "0.1.0"  # fallback
  ```

## 🔄 版本發布流程

### 1. 更新版本號
```bash
# 編輯 pyproject.toml 中的版本號
version = "0.2.0"
```

### 2. 更新 CHANGELOG.md
```markdown
## [0.2.0] - 2024-12-XX

### 新增
- 新功能描述

### 變更
- 變更描述

### 修復
- Bug 修復描述
```

### 3. 驗證版本
```bash
# 檢查版本是否正確讀取
uv run python -c "import redmine_mcp; print(redmine_mcp.__version__)"
```

### 4. 提交變更
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "bump version to 0.2.0"
```

### 5. 建立標籤
```bash
git tag v0.2.0
git push origin main --tags
```

### 6. 建置和發布（可選）
```bash
# 建置套件
uv build

# 發布到 PyPI（如果需要）
uv publish
```

## 🎯 版本號規範

本專案遵循 [語義化版本](https://semver.org/lang/zh-TW/) 規範：

- **主版本號 (MAJOR)**: 不相容的 API 變更
- **次版本號 (MINOR)**: 向下相容的功能新增
- **修訂版本號 (PATCH)**: 向下相容的 bug 修復

範例：`1.2.3`
- `1` = 主版本號
- `2` = 次版本號  
- `3` = 修訂版本號

## 📋 版本管理檢查清單

發布新版本前的檢查項目：

- [ ] 更新 `pyproject.toml` 中的版本號
- [ ] 更新 `CHANGELOG.md` 新增版本記錄
- [ ] 執行測試確保功能正常：`uv run python -m pytest`
- [ ] 驗證版本讀取：`uv run python -c "import redmine_mcp; print(redmine_mcp.__version__)"`
- [ ] 提交所有變更
- [ ] 建立 Git 標籤
- [ ] 推送到遠端倉庫

## 🛠️ 常用指令

```bash
# 查看當前版本
uv run python -c "import redmine_mcp; print(redmine_mcp.__version__)"

# 檢查 git 標籤
git tag -l

# 查看版本歷史
git log --oneline --decorate --graph

# 比較版本差異
git diff v0.1.0..v0.2.0
```

## ⚠️ 注意事項

1. **單一來源原則**: 只在 `pyproject.toml` 中設定版本號
2. **自動同步**: `__init__.py` 會自動讀取套件版本
3. **開發環境**: 在開發環境中，fallback 版本確保功能正常
4. **標籤命名**: Git 標籤使用 `v` 前綴（如：`v0.1.0`）
5. **發布前測試**: 總是在發布前執行完整測試

## 🔗 相關資源

- [語義化版本規範](https://semver.org/lang/zh-TW/)
- [Keep a Changelog](https://keepachangelog.com/zh-TW/)
- [Python 套件版本管理](https://packaging.python.org/guides/single-sourcing-package-version/)