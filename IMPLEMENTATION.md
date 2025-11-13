# 代码实现文档

## 架构概览

本项目采用 **三层架构** 设计:

1. **核心引擎层**: `enhanced_datahelper.py` - 封装数据分析逻辑
2. **界面层**: `enhanced_app.py` (Web) / `cli_analyzer.py` (CLI)
3. **测试层**: `test_analyzer.py` / `test_providers.py`

---

## 核心模块详解

### 1. DataAnalyzer 类 (`enhanced_datahelper.py`)

**职责**: 数据加载、代码生成、执行、纠错、解释

#### 关键方法

##### `__init__(csv_path, llm_provider)`
- 加载CSV文件到 `self.df`
- 初始化指定的LLM客户端 (`_init_llm`)
- 创建对话历史容器 (`conversation_history`, `execution_history`)

##### `_init_llm(provider)`
- **支持模型**: Gemini, GPT-3.5, Claude, DeepSeek, Qwen3
- **实现方式**:
  - Gemini: `ChatGoogleGenerativeAI`
  - GPT/DeepSeek/Qwen: `ChatOpenAI` (通过 `base_url` 切换端点)
  - Claude: `ChatAnthropic`
- **环境变量**: 从 `.env` 读取对应的 API Key
- **错误处理**: 密钥缺失时抛出 `ValueError`

##### `generate_code(question, max_retries=3)`
核心流程:
```
循环最多3次:
  1. 调用 _generate_code_with_llm(question, attempt)
     - 构建系统提示词(包含数据集信息、历史上下文)
     - 调用 LLM.invoke(messages)
     - 提取代码块(```python...```)
  
  2. 调用 _execute_code(code)
     - 在隔离环境 exec() 执行
     - 捕获 stdout 输出
  
  3. 如果成功:
     - 调用 _generate_explanation() 生成中文解释
     - 保存到历史 _save_to_history()
     - 返回结果字典
  
  4. 如果失败:
     - 调用 _add_error_to_context() 保存错误
     - 下次尝试时将错误反馈给LLM
```

**返回格式**:
```python
{
    "question": str,        # 用户问题
    "code": str,            # 生成的代码
    "execution_result": str,# 执行输出
    "explanation": str,     # 中文解释
    "error": str | None,    # 错误信息
    "retry_count": int,     # 重试次数
    "success": bool         # 是否成功
}
```

##### `_generate_code_with_llm(question, attempt)`
- **系统提示词**: 包含数据集信息(`get_dataset_info`)、规则说明、对话历史(最近3轮)
- **提示词优化**: 限制数据示例为前5行,避免超长token
- **调试日志**: 打印提示词长度与LLM响应长度
- **空响应检测**: 若LLM未返回代码,抛出 `RuntimeError`

##### `_execute_code(code)`
- **执行环境**:
  ```python
  local_vars = {
      'df': self.df.copy(),  # 数据框副本
      'pd': pd,              # pandas
      'np': numpy            # numpy
  }
  ```
- **输出捕获**: 重定向 `sys.stdout` 到 `StringIO`
- **异常处理**: 捕获所有异常并返回错误堆栈

##### 余额不足自动切换

**检测逻辑** (`_is_insufficient_balance_error`):
```python
关键词匹配:
- "insufficient" + "balance/quota"
- "402"
- "payment required"
```

**回退策略** (`_choose_fallback_provider`):
```python
优先级: gemini → gpt → claude → deepseek → qwen3
排除当前失败的provider
根据环境变量可用性选择
```

---

### 2. Streamlit Web界面 (`enhanced_app.py`)

#### 会话状态管理
```python
st.session_state:
  - analyzer: DataAnalyzer 实例
  - chat_history: 对话记录列表
  - data_loaded: 数据加载标志
```

#### 界面布局

**侧边栏**:
- 数据源选择(上传/路径)
- LLM模型选择(下拉框)
- 模型不匹配提示(当选择与当前不同时)
- 加载数据按钮
- 清空历史按钮

**主界面** (双列布局):
- **左列**: 数据概览(行数、列名、前10行、统计、类型)
- **右列**: 对话界面(历史消息 + 输入框 + 分析/清空按钮)

#### 关键逻辑

**模型切换**:
```python
if current_active != llm_provider:
    st.info("模型不匹配提示")
    if st.button("仅切换模型"):
        analyzer.llm = analyzer._init_llm(llm_provider)
```

**提交分析**:
```python
if submit_btn and user_question.strip():
    with st.spinner("正在分析..."):
        try:
            result = analyzer.generate_code(user_question)
        except Exception as e:
            # 构建失败结果字典
        
        # 检测空代码
        if result["success"] and not result["code"].strip():
            result["success"] = False
        
        # 附加provider调试信息
        st.session_state.chat_history.append(result)
        st.rerun()
```

**错误提示增强**:
```python
if "余额/402/quota/配额" in explanation:
    st.warning("检测到配额不足,建议更换模型")
```

---

### 3. 命令行工具 (`cli_analyzer.py`)

**参数**:
- `--csv`: CSV文件路径(必填)
- `--llm`: 模型选择(可选,默认gemini)
- `--question`: 单次查询问题(可选,无则进入交互模式)

**交互模式**:
```python
while True:
    question = input("您的问题: ")
    if question in ["退出", "exit", "quit"]:
        break
    result = analyzer.generate_code(question)
    print_result(result)
```

**输出格式化**:
- 使用 `tabulate` 库美化表格
- 彩色输出(成功/失败标记)

---

### 4. 测试脚本

#### `test_analyzer.py`
- 运行3个预设问题(关联问题,测试对话历史)
- 打印详细日志(代码、结果、解释、重试次数)
- 生成测试总结(成功/失败数)

#### `test_providers.py`
- 测试 DeepSeek 和 Qwen API密钥可用性
- 使用最简提示词("请只回复: OK")减少计费
- 输出状态、延迟、错误信息

---

## 数据流图

```
用户输入 → DataAnalyzer.generate_code()
         ↓
    构建系统提示词(数据信息 + 历史 + 规则)
         ↓
    LLM.invoke(messages) → 返回代码文本
         ↓
    提取代码块(正则匹配 ```python...```)
         ↓
    exec(code) 在隔离环境执行
         ↓
    捕获 stdout 输出
         ↓
    [成功] → LLM生成解释 → 保存历史 → 返回结果
    [失败] → 保存错误 → 重试(最多3次)
```

---

## 关键技术点

### 1. LangChain消息类型兼容
```python
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
except:
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
```

### 2. 数据自动清理
```python
if '$' in sample or ',' in sample:
    df[col] = df[col].str.replace('$', '').str.replace(',', '')
    df[col] = pd.to_numeric(df[col], errors='coerce')
```

### 3. 代码提取正则
```python
pattern = r'```python\s*(.*?)\s*```'
matches = re.findall(pattern, text, re.DOTALL)
```

### 4. Streamlit状态持久化
```python
if "key" not in st.session_state:
    st.session_state.key = default_value
```

### 5. 安全代码执行
```python
local_vars = {'df': self.df.copy(), 'pd': pd, 'np': np}
old_stdout = sys.stdout
sys.stdout = StringIO()
try:
    exec(code, local_vars)
    output = sys.stdout.getvalue()
finally:
    sys.stdout = old_stdout
```

---

## 扩展建议

1. **支持更多模型**: 添加 Llama3、Mistral 等开源模型
2. **可视化增强**: 自动生成图表(matplotlib/plotly)
3. **导出功能**: 支持导出分析报告(Markdown/PDF)
4. **权限控制**: 添加代码审核白名单,禁止危险操作
5. **缓存优化**: 相同问题复用结果,减少API调用

---

## 依赖清单

核心依赖(详见 `requirements.txt`):
- `streamlit>=1.28.0` - Web界面
- `pandas>=2.0.0` - 数据处理
- `langchain>=0.1.0` - LLM接口
- `langchain-openai` - OpenAI/兼容模型
- `langchain-google-genai` - Gemini
- `langchain-anthropic` - Claude
- `python-dotenv` - 环境变量管理
- `tabulate` - CLI表格美化

---

## 版本历史

- **v1.0.0**: 初始版本,支持基础分析与5种LLM
- **v1.1.0**: 增加余额保护与自动切换
- **v1.2.0**: 优化提示词长度,修复快捷按钮bug
