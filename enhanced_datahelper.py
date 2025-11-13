"""
增强版数据分析助手
支持对话历史、代码生成、错误纠正和自然语言解释
"""

import os
import re
import sys
import traceback
from io import StringIO
from typing import Dict, List, Tuple, Any, Optional

import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# 兼容不同版本的LangChain消息类型导入路径
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
except Exception:  # pragma: no cover
    from langchain.schema import HumanMessage, AIMessage, SystemMessage

load_dotenv()


class DataAnalyzer:
    """增强版数据分析器,支持对话历史和代码纠错"""
    
    def __init__(self, csv_path: str, llm_provider: str = "gemini"):
        """
        初始化数据分析器
        
        Args:
            csv_path: CSV文件路径
            llm_provider: LLM提供商 (gemini, gpt, claude, deepseek, qwen3)
        """
        self.csv_path = csv_path
        self.df = self._load_csv(csv_path)
        self.llm = self._init_llm(llm_provider)
        self.conversation_history = []
        self.execution_history = []
        
    def _load_csv(self, csv_path: str) -> pd.DataFrame:
        """加载CSV文件"""
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            print(f"✓ 成功加载数据: {csv_path}")
            print(f"  - 行数: {len(df)}")
            print(f"  - 列数: {len(df.columns)}")
            print(f"  - 列名: {', '.join(df.columns.tolist())}")
            
            # 自动检测并清理常见的格式问题
            self._auto_clean_data(df)
            
            return df
        except Exception as e:
            raise Exception(f"无法加载CSV文件 {csv_path}: {str(e)}")
    
    def _init_llm(self, provider: str):
        """根据提供商名称初始化LLM客户端"""
        provider_key = provider.lower()

        if provider_key == "gemini":
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
        elif provider_key == "gpt":
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        elif provider_key == "claude":
            llm = ChatAnthropic(model_name="claude-3-opus-20240229", temperature=0)
        elif provider_key == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("未找到 DEEPSEEK_API_KEY, 请在 .env 中配置 DeepSeek API Key")
            base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
            model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, base_url=base_url)
        elif provider_key in {"qwen", "qwen3"}:
            api_key = os.getenv("QWEN_API_KEY")
            if not api_key:
                raise ValueError("未找到 QWEN_API_KEY, 请在 .env 中配置 Qwen API Key")
            base_url = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            model_name = os.getenv("QWEN_MODEL", "qwen-plus")
            llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key, base_url=base_url)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

        # 记录当前提供商，供错误回退判断
        self.current_provider = provider_key
        print(f"✓ 使用LLM: {provider}")
        return llm
    
    def _auto_clean_data(self, df: pd.DataFrame):
        """自动清理数据格式问题"""
        cleaned_cols = []
        
        for col in df.columns:
            # 检查是否包含货币符号
            if df[col].dtype == 'object':
                sample = str(df[col].iloc[0]) if len(df) > 0 else ""
                
                # 清理货币格式 (如 $1,000)
                if '$' in sample or ',' in sample:
                    try:
                        df[col] = df[col].astype(str).str.replace('$', '', regex=False)
                        df[col] = df[col].str.replace(',', '', regex=False)
                        df[col] = df[col].str.strip()
                        # 避免 FutureWarning: 不再传递 errors='ignore'
                        try:
                            df[col] = pd.to_numeric(df[col])
                        except Exception:
                            # 失败则采用安全降级为 NaN
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        cleaned_cols.append(f"{col} (移除$和,)")
                    except:
                        pass
                
                # 清理百分比格式 (如 75%)
                elif '%' in sample:
                    try:
                        df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                        df[col] = df[col].str.strip()
                        try:
                            df[col] = pd.to_numeric(df[col])
                        except Exception:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        cleaned_cols.append(f"{col} (移除%)")
                    except:
                        pass
        
        if cleaned_cols:
            print(f"  - 自动清理列: {', '.join(cleaned_cols)}")
    
    def get_dataset_info(self) -> str:
        """获取数据集信息（精简版，避免超长提示词）"""
        info = f"""
数据集信息:
- 文件路径: {self.csv_path}
- 行数: {len(self.df)}
- 列数: {len(self.df.columns)}
- 列名和类型:
"""
        for col in self.df.columns:
            info += f"  * {col}: {self.df[col].dtype}\n"
        
        # 仅显示前3行且限制宽度，避免超长token
        info += f"\n前5行数据示例:\n{self.df.head(5).to_string(max_cols=10, max_colwidth=30)}\n"
        
        return info
    
    def generate_code(self, question: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        生成Python代码来回答问题,支持自动纠错
        
        Args:
            question: 用户问题
            max_retries: 最大重试次数
            
        Returns:
            包含代码、执行结果、解释等信息的字典
        """
        result = {
            "question": question,
            "code": "",
            "execution_result": "",
            "explanation": "",
            "error": None,
            "retry_count": 0,
            "success": False
        }
        
        def _format_insufficient_balance(provider: str, raw_msg: str) -> str:
            return (
                f"当前模型提供商({provider})返回余额或配额不足(可能是402)。\n"
                f"请检查账户余额或更换其他模型提供商。\n"
                f"原始错误: {raw_msg}"
            )

        for attempt in range(max_retries):
            result["retry_count"] = attempt

            # 生成代码（带余额错误回退）
            try:
                code = self._generate_code_with_llm(question, attempt)
            except Exception as e:
                err_msg = str(e)
                if self._is_insufficient_balance_error(err_msg):
                    fallback = self._choose_fallback_provider(exclude=getattr(self, "current_provider", None))
                    if fallback:
                        print(f"⚠ LLM调用失败(可能余额不足)。尝试切换到备用提供商: {fallback}")
                        try:
                            self.llm = self._init_llm(fallback)
                            code = self._generate_code_with_llm(question, attempt if attempt == 0 else 0)
                            result["explanation"] = f"已自动切换到备用提供商: {fallback}"
                        except Exception as e2:
                            result["error"] = _format_insufficient_balance(fallback, str(e2))
                            result["explanation"] = result["error"]
                            return result
                    else:
                        result["error"] = _format_insufficient_balance(getattr(self, "current_provider", "当前"), err_msg)
                        result["explanation"] = result["error"]
                        return result
                else:
                    result["error"] = err_msg
                    result["explanation"] = f"LLM调用失败: {err_msg}"
                    return result

            result["code"] = code

            # 执行代码
            success, output, error = self._execute_code(code)

            if success:
                result["execution_result"] = output
                result["success"] = True
                # 生成自然语言解释
                try:
                    explanation = self._generate_explanation(question, code, output)
                except Exception as e:
                    explanation = f"结果生成成功，但解释生成失败: {str(e)}"
                result["explanation"] = explanation

                # 保存到历史记录
                self._save_to_history(question, code, output, explanation)
                return result
            else:
                # 代码执行失败,记录错误
                result["error"] = error
                print(f"\n⚠ 第 {attempt + 1} 次尝试失败: {error[:200]}")
                if attempt < max_retries - 1:
                    # 将错误反馈给LLM,让其纠错
                    print("→ 正在请求LLM纠正错误...")
                    self._add_error_to_context(code, error)

        # 所有尝试都失败
        result["explanation"] = f"抱歉,经过{max_retries}次尝试后仍无法生成正确的代码。最后的错误是: {result['error']}"
        return result
    
    def _generate_code_with_llm(self, question: str, attempt: int = 0) -> str:
        """使用LLM生成Python代码"""
        
        # 构建系统提示
        system_prompt = f"""你是一个专业的Python数据分析助手。你需要生成Python代码来回答用户的数据分析问题。

数据集信息:
{self.get_dataset_info()}

重要规则:
1. 生成的代码必须是完整的、可执行的Python代码
2. 数据框变量名必须使用 'df'
3. df已经加载好了,不需要重新读取CSV
4. 数据已经预处理过:Sales列已转为数值(移除$和,),Rating列已转为数值(移除%)
5. 代码应该打印出最终结果,使用print()函数
6. 只返回Python代码,不要包含任何解释文字
7. 代码必须放在```python 和 ``` 之间
8. 确保代码能处理可能的NaN值

示例代码格式:
```python
# 数据清理和分析代码
result = df.groupby('Category')['Sales'].sum()
print(result)
```
"""
        
        # 如果是重试,添加错误反馈
        if attempt > 0 and self.conversation_history:
            last_message = self.conversation_history[-1]
            if isinstance(last_message, dict) and "error" in last_message:
                system_prompt += f"\n\n上一次代码执行失败,错误信息:\n{last_message['error']}\n\n请修正错误,生成正确的代码。"
        
        # 添加对话历史上下文
        if self.execution_history:
            system_prompt += "\n\n对话历史:\n"
            for i, hist in enumerate(self.execution_history[-3:], 1):  # 只保留最近3轮
                system_prompt += f"\n问题{i}: {hist['question']}\n"
                system_prompt += f"代码: {hist['code'][:200]}...\n"
                system_prompt += f"结果: {hist['result'][:200]}...\n"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请生成Python代码来回答以下问题:\n\n{question}")
        ]
        
        # 调用LLM（增加调试日志，记录提示词长度）
        prompt_length = len(system_prompt) + len(question)
        print(f"[DEBUG] 提示词总长度: {prompt_length} 字符，正在调用 {getattr(self, 'current_provider', 'unknown')} ...")
        
        response = self.llm.invoke(messages)
        code = response.content
        
        print(f"[DEBUG] LLM响应长度: {len(code) if code else 0} 字符")
        
        # 提取代码块
        code = self._extract_code(code)

        # 如果模型没有返回任何代码，抛出异常以便上层捕获并显示
        if not code.strip():
            raise RuntimeError(
                f"LLM未返回任何代码内容。可能原因: 提示词过长({prompt_length}字符)、配额限制或模型拒绝。"
                f"原始响应前200字符: {response.content[:200] if response.content else '<空>'}"
            )

        return code
    
    def _extract_code(self, text: str) -> str:
        """从LLM响应中提取Python代码"""
        # 尝试提取```python ... ```之间的代码
        pattern = r'```python\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # 如果没有代码块标记,尝试提取所有看起来像Python代码的部分
        pattern = r'```\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # 如果都没有,返回原文
        return text.strip()

    def _is_insufficient_balance_error(self, msg: str) -> bool:
        msg_low = msg.lower()
        return (
            "insufficient" in msg_low and ("balance" in msg_low or "quota" in msg_low)
        ) or (" 402" in msg_low) or ("code: 402" in msg_low) or ("payment" in msg_low and "required" in msg_low)

    def _choose_fallback_provider(self, exclude: Optional[str] = None) -> Optional[str]:
        """根据环境变量可用性选择一个后备LLM提供商，排除当前提供商"""
        candidates = []
        if os.getenv("GOOGLE_API_KEY"):
            candidates.append("gemini")
        if os.getenv("OPENAI_API_KEY"):
            candidates.append("gpt")
        if os.getenv("ANTHROPIC_API_KEY"):
            candidates.append("claude")
        if os.getenv("DEEPSEEK_API_KEY"):
            candidates.append("deepseek")
        if os.getenv("QWEN_API_KEY"):
            candidates.append("qwen3")

        # 去重并排除
        uniq = [c for c in candidates if c != exclude]
        # 简单策略: 优先 gemini -> gpt -> claude -> deepseek -> qwen3
        priority = ["gemini", "gpt", "claude", "deepseek", "qwen3"]
        for p in priority:
            if p in uniq:
                return p
        return None

    def _execute_code(self, code: str) -> Tuple[bool, str, str]:
        """
        执行Python代码

        Returns:
            (success, output, error)
        """
        # 准备执行环境
        local_vars = {
            'df': self.df.copy(),
            'pd': pd,
            'np': __import__('numpy'),
        }

        # 捕获输出
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            # 执行代码
            exec(code, local_vars)

            # 获取输出
            output = captured_output.getvalue()

            # 如果没有输出,尝试获取最后一个表达式的值
            if not output.strip():
                # 检查是否有变量被创建
                for var_name in ['result', 'output', 'answer']:
                    if var_name in local_vars:
                        output = str(local_vars[var_name])
                        break

            sys.stdout = old_stdout
            return True, output, ""

        except Exception as e:
            sys.stdout = old_stdout
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return False, "", error_msg
    
    def _generate_explanation(self, question: str, code: str, result: str) -> str:
        """生成自然语言解释"""
        
        prompt = f"""基于以下信息,用自然语言解释分析结果:

问题: {question}

执行的代码:
{code}

执行结果:
{result}

请用清晰、简洁的中文解释这个结果,回答用户的问题。不要重复代码,只需要解释结果的含义。
"""
        
        messages = [
            SystemMessage(content="你是一个数据分析助手,擅长用自然语言解释数据分析结果。"),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _save_to_history(self, question: str, code: str, result: str, explanation: str):
        """保存到历史记录"""
        self.execution_history.append({
            "question": question,
            "code": code,
            "result": result,
            "explanation": explanation
        })
        
        self.conversation_history.append(
            HumanMessage(content=question)
        )
        self.conversation_history.append(
            AIMessage(content=f"代码:\n{code}\n\n结果:\n{result}\n\n解释:\n{explanation}")
        )
    
    def _add_error_to_context(self, code: str, error: str):
        """将错误信息添加到对话上下文"""
        self.conversation_history.append({
            "code": code,
            "error": error,
            "type": "error_feedback"
        })
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self.execution_history = []
        print("✓ 对话历史已清空")


def clean_sales_data(df: pd.DataFrame, sales_column: str = 'Sales') -> pd.DataFrame:
    """清理销售数据(移除$和,符号)"""
    if sales_column in df.columns:
        df = df.copy()
        df[sales_column] = df[sales_column].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        df[sales_column] = pd.to_numeric(df[sales_column], errors='coerce')
    return df


def clean_rating_data(df: pd.DataFrame, rating_column: str = 'Rating') -> pd.DataFrame:
    """清理评分数据(移除%符号)"""
    if rating_column in df.columns:
        df = df.copy()
        df[rating_column] = df[rating_column].astype(str).str.replace('%', '').str.strip()
        df[rating_column] = pd.to_numeric(df[rating_column], errors='coerce')
    return df
