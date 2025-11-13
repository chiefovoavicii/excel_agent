# GitHub 上传指南

## 前置准备

1. **清理敏感文件**
   ```bash
   # 确保 .env 文件已在 .gitignore 中
   # 删除或移除包含真实API密钥的文件
   ```

2. **安装Git** (如未安装)
   - 下载: https://git-scm.com/downloads
   - 配置用户信息:
     ```bash
     git config --global user.name "Your Name"
     git config --global user.email "your.email@example.com"
     ```

---

## 上传步骤

### 1. 初始化本地仓库

```bash
cd d:\ms_project\data_analyzer_app_with_llm_agents-main
git init
git add .
git commit -m "Initial commit: 智能数据分析助手"
```

### 2. 在GitHub创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息:
   - **Repository name**: `data-analyzer-llm` (或自定义名称)
   - **Description**: `基于大语言模型的智能数据分析系统`
   - **Visibility**: Public 或 Private
   - **不要** 勾选 "Add a README file"(已有README.md)
3. 点击 **Create repository**

### 3. 关联远程仓库并推送

```bash
# 替换 YOUR_USERNAME 为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/data-analyzer-llm.git
git branch -M main
git push -u origin main
```

### 4. 推送后验证

访问 `https://github.com/YOUR_USERNAME/data-analyzer-llm` 确认文件已上传。

---

## 后续更新

```bash
# 修改代码后提交
git add .
git commit -m "描述你的更改"
git push
```

---

## 注意事项

✅ **已包含在仓库中**:
- README.md (项目说明)
- IMPLEMENTATION.md (代码实现文档)
- LICENSE (MIT许可证)
- .gitignore (忽略敏感文件)
- .env.example (环境变量模板)
- requirements.txt (依赖清单)
- 所有源代码文件

❌ **已排除**:
- `.env` (真实API密钥)
- `venv/` (虚拟环境)
- `__pycache__/` (Python缓存)
- `大模型实习生测试项目.pdf` (可选,如需包含请移除.gitignore规则)

---

## 仓库展示建议

1. **添加主题标签** (在GitHub仓库页面 Settings → Topics):
   - `llm`, `data-analysis`, `streamlit`, `langchain`, `python`

2. **启用GitHub Pages** (可选,展示项目文档):
   - Settings → Pages → Source 选择 `main` 分支

3. **添加徽章** (可选,在README.md顶部):
   ```markdown
   ![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
   ![License](https://img.shields.io/badge/license-MIT-green.svg)
   ```

---

## 常见问题

**Q: push时要求输入用户名密码?**  
A: GitHub已禁用密码认证,需使用Personal Access Token:
   1. GitHub → Settings → Developer settings → Personal access tokens → Generate new token
   2. 勾选 `repo` 权限
   3. 复制token作为密码使用

**Q: 如何修改LICENSE中的版权信息?**  
A: 编辑 `LICENSE` 文件,将 `[Your Name]` 替换为你的真实姓名。

**Q: 大文件无法推送?**  
A: 确保 `venv/` 和大型PDF已在 `.gitignore` 中;如需上传大文件考虑使用Git LFS。

---

完成上传后,记得更新 README.md 中的仓库链接!
