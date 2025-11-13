# 运行步骤指南

## 📋 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / macOS / Linux
- **必需工具**: PowerShell (Windows) 或 Bash (Linux/macOS)

---

## 🚀 快速开始

### 1. 下载项目

```bash
# 克隆仓库
git clone https://github.com/yourusername/data_analyzer_app_with_llm_agents.git
cd excel_agent

# 或直接下载ZIP并解压
```

### 2. 配置环境

#### Windows (PowerShell)

```powershell
# 运行自动安装脚本
.\setup.ps1
```

#### Linux / macOS

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件,填入你的API密钥
```

**`.env` 文件示例**:
```env
# 至少配置一个模型的API密钥
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
QWEN_API_KEY=your_qwen_api_key_here
```

---

## 🖥️ 运行方式

### 方式一: Web界面 (推荐)

#### Windows
```powershell
.\start_web.ps1
```

#### Linux / macOS
```bash
source venv/bin/activate
streamlit run app.py
```

**访问地址**: 浏览器自动打开 `http://localhost:8501`

---

### 方式二: 命令行交互

#### Windows
```powershell
venv\Scripts\activate
python cli_analyzer.py "数据文件路径.csv" --llm qwen3
```

#### Linux / macOS
```bash
source venv/bin/activate
python cli_analyzer.py "数据文件路径.csv" --llm qwen3
```

**可选参数**:
- `--llm`: 选择模型 (`gemini`, `gpt`, `claude`, `deepseek`, `qwen3`)
- `--mode`: 运行模式 (`interactive` 或 `batch`)
- `--test`: 运行预设测试问题

---

### 方式三: 批量测试

#### Windows
```powershell
.\run_test.ps1
```

#### Linux / macOS
```bash
source venv/bin/activate
python test_analyzer.py
```

---

## 📖 使用指南

### Web界面操作

1. **加载数据**
   - 侧边栏选择"上传文件"或"指定路径"
   - 选择LLM模型
   - 点击"🚀 加载数据"

2. **提问分析**
   - 在输入框输入自然语言问题
   - 点击"🔍 分析"
   - 查看生成的代码、结果和解释

3. **查看图表**
   - AI生成图表会自动显示在解释下方
   - 支持中文标签

4. **切换模型**
   - 在侧边栏选择不同的LLM
   - 点击"🔁 切换模型"

### 命令行操作

**交互模式**:
```
>>> 分析Clothing的销售趋势
>>> 绘制Category销售额柱状图
>>> quit  # 退出
```

**特殊命令**:
- `clear`: 清空对话历史
- `history`: 查看历史记录
- `quit` / `exit`: 退出程序

---

## 💡 示例问题

**数据分析**:
- "分析Clothing随时间变化的销售额趋势"
- "哪些年份Components比Accessories的销售额高?"
- "找出评分最高的前10个产品"

**数据可视化**:
- "绘制不同Category的销售额扇形图"
- "绘制Sales和Rating的散点图"
- "绘制各年份销售额的折线图"

**统计分析**:
- "计算各Category的平均评分"
- "分析Sales的分布情况"
- "找出销售额异常的数据点"

---

## 🔧 常见问题

**Q: Web界面打不开?**
```bash
# 检查端口是否被占用
netstat -ano | findstr :8501

# 使用其他端口
streamlit run app.py --server.port 8502
```

**Q: 提示API密钥错误?**
- 检查 `.env` 文件是否正确配置
- 确认API密钥有效且有余额
- 尝试切换其他LLM模型

**Q: 图表显示乱码?**
- 已自动配置中文字体支持
- 如仍有问题,检查系统是否安装SimHei/Microsoft YaHei字体

**Q: 代码执行失败?**
- 检查CSV数据格式是否正确
- 尝试简化问题描述
- 查看生成的代码是否有明显错误

---

## 📝 测试API密钥

运行以下命令测试API配置:

```bash
# Windows
venv\Scripts\activate
python test_providers.py

# Linux/macOS
source venv/bin/activate
python test_providers.py
```

---

## 🛑 停止运行

**Web界面**: 在终端按 `Ctrl + C`

**命令行**: 输入 `quit` 或按 `Ctrl + C`

---

## 📚 更多信息

- **实现文档**: 查看 `IMPLEMENTATION.md`
- **项目说明**: 查看 `README.md`
- **许可证**: 查看 `LICENSE`

---

## 🆘 获取帮助

遇到问题? 请检查:
1. Python版本是否 >= 3.8
2. 依赖是否完整安装
3. API密钥是否配置正确
4. CSV文件路径是否正确

---

**祝使用愉快! 🎉**
