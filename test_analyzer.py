"""
测试脚本 - 运行三个关联问题
"""

from data_analyzer import DataAnalyzer


def main():
    print("="*80)
    print("🧪 数据分析系统测试")
    print("="*80)
    
    # CSV文件路径
    csv_path = r".\data\大模型实习项目测试.csv"
    
    # 测试问题(三个关联问题)
    test_questions = [
        "分析Clothing随时间变化的总销售额趋势",
        "对Bikes进行同样的分析", 
        "哪些年份Components比Accessories的总销售额高?",
        "请绘制category的总销售额柱状图"
    ]
    
    print(f"\nCSV文件: {csv_path}")
    print(f"测试问题数量: {len(test_questions)}")
    print("\n" + "="*80 + "\n")
    
    try:
        # 初始化分析器
        print("正在初始化分析器...")
        analyzer = DataAnalyzer(csv_path=csv_path, llm_provider="qwen3")
        
        print("\n" + "="*80)
        print("开始测试")
        print("="*80 + "\n")
        
        # 依次处理每个问题
        for i, question in enumerate(test_questions, 1):
            print("\n" + "█"*80)
            print(f"问题 {i}/{len(test_questions)}")
            print("█"*80)
            print(f"\n📝 问题: {question}\n")
            print("-"*80)
            
            # 生成代码并执行
            print("🤔 正在生成代码...")
            result = analyzer.generate_code(question, max_retries=3)
            
            # 打印结果
            print("\n" + "="*80)
            if result['success']:
                print("✅ 状态: 成功")
                if result['retry_count'] > 0:
                    print(f"🔄 重试次数: {result['retry_count']}")
            else:
                print("❌ 状态: 失败")
            print("="*80)
            
            print("\n📋 生成的代码:")
            print("-"*80)
            print(result['code'])
            print("-"*80)
            
            if result['success']:
                print("\n📊 执行结果:")
                print("-"*80)
                print(result['execution_result'])
                print("-"*80)
                
                print("\n💡 AI解释:")
                print("-"*80)
                print(result['explanation'])
                print("-"*80)
            else:
                print("\n❌ 错误信息:")
                print("-"*80)
                print(result.get('error', '未知错误'))
                print("-"*80)
            
            print("\n" + "█"*80 + "\n")
            
            # 简短暂停
            import time
            time.sleep(2)
        
        # 打印总结
        print("\n" + "="*80)
        print("📊 测试总结")
        print("="*80)
        print(f"总问题数: {len(test_questions)}")
        print(f"成功: {sum(1 for h in analyzer.execution_history if h.get('result'))}")
        print(f"失败: {len(test_questions) - len(analyzer.execution_history)}")
        print("="*80)
        
        # 打印对话历史
        print("\n📜 完整对话历史:")
        print("="*80)
        for i, hist in enumerate(analyzer.execution_history, 1):
            print(f"\n{i}. 问题: {hist['question']}")
            print(f"   代码行数: {len(hist['code'].split(chr(10)))}")
            print(f"   结果预览: {hist['result'][:100]}...")
            print(f"   解释预览: {hist['explanation'][:100]}...")
        print("="*80)
        
        print("\n✅ 测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
