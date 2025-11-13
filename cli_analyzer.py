"""
命令行交互式数据分析工具
支持对话历史、代码生成、错误纠正
"""

import sys
from data_analyzer import DataAnalyzer


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def print_result(result: dict):
    """格式化打印分析结果"""
    print_separator("=")
    print(f"📝 问题: {result['question']}")
    print_separator("-")
    
    if result['success']:
        print("\n✓ 分析成功!")
        
        print("\n" + "=" * 80)
        print("📋 生成的代码:")
        print("=" * 80)
        print(result['code'])
        
        print("\n" + "=" * 80)
        print("📊 执行结果:")
        print("=" * 80)
        print(result['execution_result'])
        
        print("\n" + "=" * 80)
        print("💡 AI解释:")
        print("=" * 80)
        print(result['explanation'])
        
        if result['retry_count'] > 0:
            print(f"\nℹ️  经过 {result['retry_count'] + 1} 次尝试后成功")
    else:
        print("\n❌ 分析失败!")
        print(f"错误: {result['explanation']}")
        if result.get('code'):
            print("\n尝试的代码:")
            print(result['code'])
    
    print_separator("=")


def run_interactive_mode(csv_path: str, llm_provider: str = "gemini"):
    """运行交互式模式"""
    print_separator("=")
    print("🤖 智能数据分析助手 - 命令行版")
    print_separator("=")
    print(f"CSV文件: {csv_path}")
    print(f"LLM: {llm_provider}")
    print_separator("=")
    
    try:
        # 初始化分析器
        analyzer = DataAnalyzer(csv_path, llm_provider)
        print("\n✓ 数据加载成功!\n")
        
        # 显示数据集信息
        print(analyzer.get_dataset_info())
        print_separator("=")
        
        print("\n使用说明:")
        print("- 输入数据分析问题,系统将自动生成代码并执行")
        print("- 输入 'quit' 或 'exit' 退出")
        print("- 输入 'clear' 清空对话历史")
        print("- 输入 'history' 查看对话历史")
        print_separator("=")
        
        # 交互循环
        question_count = 0
        while True:
            print(f"\n问题 #{question_count + 1}:")
            question = input(">>> ").strip()
            
            if not question:
                continue
            
            # 处理特殊命令
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见!")
                break
            
            if question.lower() == 'clear':
                analyzer.clear_history()
                question_count = 0
                print("\n✓ 对话历史已清空")
                continue
            
            if question.lower() == 'history':
                print("\n对话历史:")
                for i, hist in enumerate(analyzer.execution_history, 1):
                    print(f"\n{i}. {hist['question']}")
                    print(f"   结果: {hist['result'][:100]}...")
                continue
            
            # 执行分析
            print("\n🤔 正在分析...\n")
            result = analyzer.generate_code(question)
            
            # 打印结果
            print_result(result)
            
            question_count += 1
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_batch_mode(csv_path: str, questions: list, llm_provider: str = "gemini"):
    """运行批处理模式(用于测试)"""
    print_separator("=")
    print("🤖 智能数据分析助手 - 批处理模式")
    print_separator("=")
    print(f"CSV文件: {csv_path}")
    print(f"LLM: {llm_provider}")
    print(f"问题数量: {len(questions)}")
    print_separator("=")
    
    try:
        # 初始化分析器
        analyzer = DataAnalyzer(csv_path, llm_provider)
        print("\n✓ 数据加载成功!\n")
        
        # 依次处理每个问题
        for i, question in enumerate(questions, 1):
            print(f"\n\n{'='*80}")
            print(f"处理问题 {i}/{len(questions)}")
            print('='*80)
            
            result = analyzer.generate_code(question)
            print_result(result)
            
            # 简短暂停
            import time
            time.sleep(1)
        
        print("\n\n" + "="*80)
        print("✓ 所有问题处理完成!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能数据分析助手")
    parser.add_argument("csv_path", help="CSV文件路径")
    parser.add_argument(
        "--llm",
        default="qwen3",
        choices=["gemini", "gpt", "claude", "deepseek", "qwen3"],
        help="LLM提供商 (默认: qwen3)",
    )
    parser.add_argument("--mode", default="interactive", choices=["interactive", "batch"],
                        help="运行模式 (默认: interactive)")
    parser.add_argument("--test", action="store_true",
                        help="运行测试问题")
    
    args = parser.parse_args()
    
    if args.test or args.mode == "batch":
        # 测试问题
        test_questions = [
            "分析Clothing随时间变化的总销售额趋势",
            "对Bikes进行同样的分析",
            "哪些年份Components比Accessories的总销售额高?"
        ]
        run_batch_mode(args.csv_path, test_questions, args.llm)
    else:
        run_interactive_mode(args.csv_path, args.llm)


if __name__ == "__main__":
    main()
