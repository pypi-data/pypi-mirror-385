def pytest_runtest_setup(item):
    """pytest钩子：每个测试用例执行前调用"""
    # item是测试用例对象，item.name是测试用例函数名
    print(f"\n👋 开始执行测试：{item.name}")