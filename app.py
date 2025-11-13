"""
增强版数据分析应用
支持对话历史、代码生成、错误纠正和自然语言解释
"""

import streamlit as st
import pandas as pd
from data_analyzer import DataAnalyzer

# 页面配置
st.set_page_config(page_title="智能数据分析助手 🤖", layout="wide")

# 标题
st.title("🤖 智能数据分析助手 (增强版)")
st.markdown("支持对话历史、自动代码生成、错误纠正和自然语言解释")
st.divider()

# 初始化session state
if "analyzer" not in st.session_state:
    st.session_state.analyzer = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# 侧边栏 - 数据加载
with st.sidebar:
    st.header("📁 数据加载")
    st.divider()
    
    # 选择数据源
    data_source = st.radio(
        "选择数据源:",
        ["上传文件", "指定路径"]
    )
    
    csv_path = None
    
    if data_source == "上传文件":
        uploaded_file = st.file_uploader("上传CSV文件", type="csv")
        if uploaded_file:
            csv_path = uploaded_file
    else:
        csv_path_input = st.text_input(
            "CSV文件路径:",
            value=r"d:\ms_project\大模型实习项目测试.csv"
        )
        if csv_path_input:
            csv_path = csv_path_input
    
    st.divider()
    st.header("🤖 LLM设置")
    llm_provider = st.selectbox(
        "选择LLM:",
        ["gemini", "gpt", "claude", "deepseek", "qwen3"],
        index=0
    )

    if st.session_state.get("analyzer") is not None:
        current_active = getattr(st.session_state.analyzer, "current_provider", "unknown")
        if current_active != llm_provider:
            st.info(f"当前使用: {current_active}，已选择: {llm_provider}")
            if st.button("🔁 切换模型", key="switch_llm_btn"):
                try:
                    st.session_state.analyzer.llm = st.session_state.analyzer._init_llm(llm_provider)
                    st.success(f"已切换为: {llm_provider}")
                except Exception as e:
                    st.error(f"切换失败: {e}")
    
    if st.button("🚀 加载数据", width='stretch'):
        if csv_path:
            try:
                with st.spinner("正在加载数据..."):
                    st.session_state.analyzer = DataAnalyzer(
                        csv_path=csv_path,
                        llm_provider=llm_provider
                    )
                    st.session_state.data_loaded = True
                    st.session_state.chat_history = []
                st.success("✓ 数据加载成功!")
            except Exception as e:
                st.error(f"❌ 加载失败: {str(e)}")
        else:
            st.warning("⚠ 请先选择或输入CSV文件路径")
    
    if st.session_state.data_loaded:
        st.divider()
        if st.button("🗑️ 清空对话历史", width='stretch'):
            st.session_state.chat_history = []
            if st.session_state.analyzer:
                st.session_state.analyzer.clear_history()
            st.rerun()

# 主界面
if st.session_state.data_loaded and st.session_state.analyzer:
    analyzer = st.session_state.analyzer
    
    # 创建两列布局
    col_data, col_chat = st.columns([1, 2])
    
    # 左侧 - 数据概览
    with col_data:
        st.header("📊 数据概览")
        
        with st.expander("数据集信息", expanded=True):
            df = analyzer.df
            st.write(f"**行数:** {len(df)}")
            st.write(f"**列数:** {len(df.columns)}")
            st.write(f"**列名:** {', '.join(df.columns.tolist())}")
        
        with st.expander("前10行数据"):
            st.dataframe(df.head(10), width='stretch')
        
        with st.expander("数据统计"):
            st.dataframe(df.describe(), width='stretch')
        
        with st.expander("数据类型"):
            dtype_df = pd.DataFrame({
                '列名': df.columns,
                '数据类型': df.dtypes.values
            })
            # 避免 Arrow 转换错误: 将 dtype 对象转为字符串
            if '数据类型' in dtype_df.columns:
                dtype_df['数据类型'] = dtype_df['数据类型'].astype(str)
            st.dataframe(dtype_df, width='stretch')
    
    # 右侧 - 对话界面
    with col_chat:
        st.header("💬 智能对话分析")
        
        # 显示对话历史
        chat_container = st.container()
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                # 用户问题
                with st.chat_message("user"):
                    st.write(chat["question"])
                
                # AI回答
                with st.chat_message("assistant"):
                    if chat.get("success", False):
                        st.success("✓ 分析完成")
                        
                        # 显示生成的代码
                        with st.expander("📝 生成的代码", expanded=False):
                            st.code(chat["code"], language="python")
                        
                        # 显示执行结果
                        with st.expander("📊 执行结果", expanded=True):
                            st.text(chat["execution_result"])
                        
                        # 显示自然语言解释
                        st.markdown("**💡 分析解释:**")
                        st.info(chat["explanation"])
                        
                        if chat.get("figure") is not None:
                            st.markdown("**📈 生成的图表:**")
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col2:
                                st.pyplot(chat["figure"], use_container_width=True)
                            import matplotlib.pyplot as plt
                            plt.close(chat["figure"])
                        
                        if chat.get("retry_count", 0) > 0:
                            st.caption(f"ℹ️ 经过 {chat['retry_count'] + 1} 次尝试后成功")
                    else:
                        st.error("❌ 分析失败")
                        explanation_text = chat.get("explanation", "未知错误")
                        st.error(explanation_text)
                        if any(k in explanation_text for k in ["余额", "402", "quota", "配额"]):
                            st.warning("检测到余额或配额不足，请在侧边栏更换其它LLM提供商。")
                        if chat.get("code"):
                            with st.expander("尝试的代码"):
                                st.code(chat["code"], language="python")
        
        # 输入框
        st.divider()
        
        # 用户输入
        user_question = st.text_area(
            "输入您的数据分析问题:",
            height=100,
            placeholder="例如: 分析Clothing随时间变化的总销售额趋势"
        )
        
        # 提交按钮
        col_submit, col_clear = st.columns([3, 1])
        with col_submit:
            submit_btn = st.button("🔍 分析", width='stretch', type="primary")
        with col_clear:
            clear_btn = st.button("🗑️ 清空", width='stretch')
        
        if clear_btn:
            st.session_state.chat_history = []
            analyzer.clear_history()
            st.rerun()
        
        if submit_btn and user_question.strip():
            with st.spinner("🤔 正在分析..."):
                try:
                    result = analyzer.generate_code(user_question)
                except Exception as e:
                    import traceback
                    err_text = f"代码生成异常: {e}\n{traceback.format_exc()[:800]}"
                    result = {
                        "question": user_question,
                        "success": False,
                        "code": "",
                        "execution_result": "",
                        "explanation": err_text,
                        "error": str(e),
                        "retry_count": 0
                    }
                
                if result.get("success") and not result.get("code", "").strip():
                    result["success"] = False
                    result["explanation"] = "代码为空，请重试或缩短问题。"
                
                if not result.get("success") and "current_provider" in getattr(analyzer, '__dict__', {}):
                    provider = getattr(analyzer, 'current_provider', 'unknown')
                    if "LLM调用失败" in result.get("explanation", "") and "provider=" not in result["explanation"]:
                        result["explanation"] += f"\n(provider={provider})"
                
                st.session_state.chat_history.append(result)
                st.rerun()

else:
    # 未加载数据时的提示
    st.info("👈 请先在左侧加载CSV数据文件")
    
    # 显示使用说明
    st.markdown("""
    ## 📖 使用说明
    
    ### 功能特性:
    1. **灵活的数据加载**: 支持上传文件或指定文件路径
    2. **智能代码生成**: 使用大模型自动生成Python分析代码
    3. **自动错误纠正**: 代码执行失败时自动重试并纠错
    4. **对话历史管理**: 支持基于历史上下文的连续对话
    5. **自然语言解释**: 将分析结果转换为易懂的自然语言
    6. **多LLM支持**: 可选择Gemini、GPT、Claude、DeepSeek、Qwen3
    
    ### 使用步骤:
    1. 在左侧选择数据源(上传文件或指定路径)
    2. 选择要使用的LLM模型
    3. 点击"加载数据"按钮
    4. 在右侧输入您的数据分析问题
    5. 查看生成的代码、执行结果和自然语言解释
    
    ### 示例问题:
    - 分析Clothing随时间变化的总销售额趋势
    - 对Bikes进行同样的分析
    - 哪些年份Components比Accessories的总销售额高?
    - 找出销售额最高的产品类别
    - 分析评分和销售额之间的关系
    
    ### 注意事项:
    - 确保已设置相应的API密钥(GOOGLE_API_KEY, OPENAI_API_KEY等)
    - 问题可以连续提问,系统会记住之前的分析历史
    - 如果分析失败,系统会自动重试最多3次
    """)

# 页脚
st.divider()
st.caption("🤖 智能数据分析助手 | 基于LangChain和大语言模型 | 支持对话历史和自动纠错")
