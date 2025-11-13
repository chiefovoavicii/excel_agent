# AI驱动的CSV数据分析助手

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/langchain-0.1+-green.svg)](https://github.com/langchain-ai/langchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

中文文档 | [English](README.md)

基于 LangChain 和大语言模型的智能数据分析工具，将自然语言问题转换为 Python 代码，自动执行分析并提供解释。

## ✨ 功能特性

- **多模型支持**: Gemini、GPT-4、Claude、DeepSeek、通义千问
- **智能代码生成**: 自然语言 → Python分析代码
- **自动纠错**: 失败时自动重试最多3次
- **对话历史**: 支持上下文理解的多轮对话
- **双界面**: Web界面(Streamlit) + 命令行工具
- **中文图表**: matplotlib自动支持中文显示
- **智能降级**: API配额不足时自动切换模型

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 至少一个LLM的API密钥

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/data_analyzer_app_with_llm_agents.git
cd data_analyzer_app_with_llm_agents-main

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

### 启动Web界面

```bash
streamlit run app.py
```

访问 `http://localhost:8501`

### 启动命令行

```bash
python cli_analyzer.py 数据.csv --llm qwen3
```

## 📖 使用示例

**数据分析**:
```
分析Clothing随时间的销售趋势
哪些年份Components的销售额高于Accessories?
```

**数据可视化**:
```
绘制不同Category的销售额扇形图
创建Sales和Rating的散点图
```

**统计分析**:
```
计算各Category的平均评分
找出销售额异常值
```

## 🏗️ 系统架构

```
用户输入 → LangChain (统一LLM接口)
         ↓
    系统提示词 + 历史对话
         ↓
    LLM生成Python代码
         ↓
    exec()隔离环境执行
         ↓
    成功 → LLM生成解释
    失败 → 重试(最多3次)
```

## 📁 项目结构

```
├── data_analyzer.py    # 核心引擎
├── app.py             # Streamlit网页界面
├── cli_analyzer.py    # 命令行工具
├── test_analyzer.py   # 测试脚本
├── requirements.txt   # Python依赖
└── .env.example      # API密钥模板
```

## 🔑 API密钥配置

编辑 `.env` 文件 (至少配置一个):

```env
GOOGLE_API_KEY=你的gemini密钥
OPENAI_API_KEY=你的openai密钥
ANTHROPIC_API_KEY=你的claude密钥
DEEPSEEK_API_KEY=你的deepseek密钥
QWEN_API_KEY=你的通义千问密钥
```

## 🛠️ 技术栈

- **LangChain**: 统一的LLM调用接口
- **Streamlit**: Web界面框架
- **Pandas**: 数据处理
- **Matplotlib**: 图表生成(支持中文)

## 📝 文档

- [实现细节](IMPLEMENTATION.md)
- [使用指南](运行步骤.md)

## 🤝 贡献

欢迎提交 Pull Request！

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)

---

**⭐ 觉得有用的话，请给个Star支持一下！**
