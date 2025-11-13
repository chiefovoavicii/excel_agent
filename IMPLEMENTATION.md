# 代码实现文档

## 架构概览

本项目采用 **三层架构** 设计:

1. **核心引擎层**: `data_analyzer.py` - 数据分析与LLM交互
2. **界面层**: `app.py` (Streamlit Web) / `cli_analyzer.py` (命令行)
3. **测试层**: `test_analyzer.py` / `test_providers.py`

---

## 核心模块

### 1. DataAnalyzer 类 (`data_analyzer.py`)

**主要功能**: CSV加载、代码生成、执行、纠错、解释

#### 核心方法

##### `__init__(csv_path, llm_provider)`
- 加载CSV并自动清理数据(移除$、%等符号)
- 初始化LLM客户端(支持5种模型)
- 配置matplotlib支持中文显示

##### `_init_llm(provider)`
**支持模型**:
- `gemini`: Google Gemini (ChatGoogleGenerativeAI)
- `gpt`: OpenAI GPT (ChatOpenAI)
- `claude`: Anthropic Claude (ChatAnthropic)
- `deepseek`: DeepSeek (通过OpenAI兼容接口)
- `qwen3`: 阿里通义千问 (通过OpenAI兼容接口)

**配置**: 从 `.env` 读取对应API密钥

##### `generate_code(question, max_retries=3)`
**核心流程**:
```
1. 调用 _generate_code_with_llm() 生成代码
2. 调用 _execute_code() 执行代码
3. 成功 → _generate_explanation() 生成解释
4. 失败 → 将错误反馈给LLM重试(最多3次)
```

**返回结构**:
```python
{
    "question": str,           # 用户问题
    "code": str,              # 生成的Python代码
    "execution_result": str,  # 执行输出
    "explanation": str,       # AI解释
    "success": bool,          # 是否成功
    "retry_count": int,       # 重试次数
    "figure": matplotlib.Figure | None  # 图形对象
}
```

##### `_execute_code(code)`
**执行环境**:
```python
local_vars = {
    'df': self.df.copy(),  # 数据副本
    'pd': pd,              # pandas
    'plt': plt,            # matplotlib
    'st': st               # streamlit(如果可用)
}
```

**图形处理**:
- Streamlit环境下自动移除 `plt.show()`
- 捕获matplotlib图形对象返回给Web界面
- 支持中文标签显示

##### 余额不足自动切换
- 检测402错误或"insufficient balance"关键词
- 自动尝试切换到其他可用的LLM
- 优先级: gemini → gpt → claude → deepseek → qwen3

---

### 2. Streamlit Web界面 (`app.py`)

#### 会话状态
```python
st.session_state:
  - analyzer: DataAnalyzer实例
  - chat_history: 对话记录
  - data_loaded: 加载状态
```

#### 界面布局

**侧边栏**:
- 数据源选择(上传文件/指定路径)
- LLM模型选择
- 加载数据/清空历史按钮

**主界面**(双列):
- **左列**: 数据概览(基本信息、前10行、统计、类型)
- **右列**: 对话历史 + 输入框

#### 图表显示
- 图表显示在解释之后
- 使用列布局控制宽度(占60%)
- 自动适应容器宽度

---

### 3. 命令行工具 (`cli_analyzer.py`)

**运行模式**:
- **交互模式**: 持续接收用户输入
- **批处理模式**: 运行预设测试问题

**特殊命令**:
- `quit/exit`: 退出
- `clear`: 清空历史
- `history`: 查看历史

---

### 4. 测试脚本

**test_analyzer.py**: 运行3个关联问题测试对话历史功能

**test_providers.py**: 测试DeepSeek和Qwen API可用性

---

## 关键技术实现

### 1. matplotlib中文支持
```python
matplotlib.use('Agg')  # 非交互式后端
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', ...]
plt.rcParams['axes.unicode_minus'] = False
```

### 2. Streamlit图形显示
```python
# 移除AI生成代码中的plt.show()
code = re.sub(r'plt\s*\.\s*show\s*\(\s*\)', '# removed', code)

# 捕获图形对象
if plt.get_fignums():
    figure = plt.gcf()
    
# 在Web界面显示
st.pyplot(figure, use_container_width=True)
```

### 3. 安全代码执行
```python
old_stdout = sys.stdout
sys.stdout = StringIO()
try:
    exec(code, local_vars)
    output = sys.stdout.getvalue()
finally:
    sys.stdout = old_stdout
```

### 4. 数据自动清理
```python
# 清理货币格式: $1,000 → 1000
df[col] = df[col].str.replace('$', '').str.replace(',', '')
df[col] = pd.to_numeric(df[col], errors='coerce')

# 清理百分比: 75% → 75
df[col] = df[col].str.replace('%', '')
```

---

## 数据流

```
用户输入
  ↓
构建提示词(数据信息 + 历史 + 规则)
  ↓
LLM生成代码
  ↓
exec()执行 + 捕获输出
  ↓
成功 → LLM生成解释 → 返回结果
失败 → 重试(最多3次)
```

---

## 依赖清单

核心依赖:
- `streamlit` - Web界面
- `pandas` - 数据处理
- `matplotlib` - 图表生成
- `langchain` + 各provider包 - LLM接口
- `python-dotenv` - 环境变量

详见 `requirements.txt`

---

## 扩展建议

1. 支持更多图表类型(plotly交互式图表)
2. 添加数据导出功能(Excel/PDF报告)
3. 代码沙箱增强(禁止文件操作等危险代码)
4. 支持多文件分析
5. 添加分析模板库
