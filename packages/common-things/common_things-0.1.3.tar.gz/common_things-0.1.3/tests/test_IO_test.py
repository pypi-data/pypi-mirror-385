import time

from src.common_things.IO_test import *
from src.common_things.IO_test import _OutputMonitor


class TestMonitorPrint:
    """测试monitor_print装饰器"""

    def test_monitor_print_captures_output(self):
        """测试装饰器能正确捕获打印输出"""

        @monitor_print()
        def test_function():
            print("Hello, World!")
            return 42

        result = test_function()
        captured = output_monitor.get_output

        assert result == 42
        assert "Hello, World!" in captured

    def test_monitor_print_multiple_prints(self):
        """测试装饰器捕获多次打印"""

        @monitor_print()
        def multi_print_function():
            print("First line")
            print("Second line")
            return "done"

        multi_print_function()
        captured = output_monitor.get_output
        assert "Second line" == captured
        captured = output_monitor.get_output
        assert "First line" == captured

    def test_monitor_print_with_arguments(self):
        """测试带参数的函数"""

        @monitor_print()
        def function_with_args(a, b):
            print(f"Sum: {a + b}")
            return a + b

        result = function_with_args(3, 4)
        captured = output_monitor.get_output

        assert result == 7
        assert "Sum: 7" in captured


class TestTimer:
    """测试timer装饰器"""

    def test_timer_as_decorator(self):
        """测试timer作为装饰器使用"""

        @timer()
        def slow_function():
            time.sleep(0.1)
            return "completed"

        result = slow_function()
        elapsed_time = get_used_time()

        assert result == "completed"
        assert elapsed_time is not None
        assert elapsed_time >= 0.1

    def test_timer_as_function(self):
        """测试timer作为函数使用"""

        def fast_function():
            return "quick result"

        result = timer(fast_function)
        elapsed_time = get_used_time()

        assert result == "quick result"
        assert elapsed_time is not None
        assert elapsed_time < 0.1  # 应该很快

    def test_timer_with_arguments(self):
        """测试带参数的函数计时"""

        @timer()
        def function_with_args(x, y):
            time.sleep(0.05)
            return x * y

        result = function_with_args(5, 6)
        elapsed_time = get_used_time()

        assert result == 30
        assert elapsed_time >= 0.05


class TestOutputMonitor:
    """测试_OutputMonitor上下文管理器"""

    def test_output_monitor_context(self):
        """测试上下文管理器基本功能"""
        with _OutputMonitor() as monitor:
            print("Captured text")
            print("Another line")

        captured = monitor.get_output
        assert "Another line" == captured
        captured = monitor.get_output
        assert "Captured text" == captured

    def test_output_monitor_capture_length(self):
        """测试捕获长度限制"""
        with _OutputMonitor(capture_length=2) as monitor:
            print("Line 1")
            print("Line 2")
            print("Line 3")  # 应该挤掉Line 1

        captured = [monitor.get_output for _ in range(2)]
        assert "Line 1" in captured
        assert "Line 2" not in captured
        assert "Line 3" in captured

    def test_output_monitor_reset(self):
        """测试重置功能"""
        monitor = _OutputMonitor()
        with monitor:
            print("First capture")

        captured1 = monitor.get_output
        monitor.reset()

        with monitor:
            print("Second capture")

        captured2 = monitor.get_output

        assert "First capture" in captured1
        assert "Second capture" in captured2
        assert captured1 != captured2


class TestIPrint:
    """测试iprint函数"""

    def test_iprint_escapes_monitoring(self):
        """测试iprint能绕过监测"""

        @monitor_print()
        def test_function():
            print("This should be captured")
            iprint("This should NOT be captured")
            return True

        test_function()
        captured = output_monitor.get_output

        assert "This should be captured" in captured
        assert "This should NOT be captured" not in captured

    def test_iprint_restores_monitoring(self):
        """测试iprint后监测恢复正常"""

        @monitor_print()
        def test_function():
            iprint("Bypass")
            print("Back to normal")
            return True

        test_function()
        captured = output_monitor.get_output

        assert "Bypass" not in captured
        assert "Back to normal" in captured


class TestEdgeCases:
    """测试边界情况和异常"""

    def test_empty_function(self):
        """测试无打印的函数"""

        @monitor_print()
        def empty_function():
            return "no output"

        result = empty_function()
        # captured = output_monitor.get_output

        assert result == "no output"
        # assert captured == "" or captured is None

    # TODO: 嵌套支持
    def test_nested_monitoring(self):
        """测试嵌套的监测装饰器"""

        @monitor_print()
        def outer_function():
            @monitor_print()
            def inner_function():
                print("Inner print")
                return "inner"

            result = inner_function()
            print("Outer print")
            return result

        # outer_function()
        # captured = output_monitor.get_output
        # assert "Inner print" == captured
        # captured = output_monitor.get_output
        # assert "Outer print" == captured

    def test_exception_handling(self):
        """测试异常情况下的监测"""

        @monitor_print()
        def function_with_error():
            print("Before error")
            raise ValueError("Test error")

        try:
            function_with_error()
        except ValueError:
            pass

        captured = output_monitor.get_output
        assert "Before error" in captured

    def test_unicode_support(self):
        """测试Unicode字符支持"""

        @monitor_print()
        def unicode_function():
            print("中文测试")
            print("🎉 Emoji test")
            return "unicode"

        result = unicode_function()

        assert result == "unicode"
        captured = output_monitor.get_output
        assert "🎉 Emoji test" == captured
        captured = output_monitor.get_output
        assert "中文测试" == captured


class TestIntegration:
    """测试集成功能"""

    def test_timer_and_monitor_together(self):
        """测试计时器和监测器同时使用"""

        @timer()
        @monitor_print()
        def integrated_function():
            print("Starting work")
            time.sleep(0.05)
            print("Work completed")
            return "success"

        result = integrated_function()
        elapsed_time = get_used_time()

        assert result == "success"
        assert elapsed_time >= 0.05

        captured = output_monitor.get_output
        assert "Work completed" == captured
        captured = output_monitor.get_output
        assert "Starting work" == captured

    def test_multiple_calls(self):
        """测试多次函数调用"""

        @monitor_print()
        def simple_function():
            print(f"Call at {time.time()}")
            return True

        # 第一次调用
        simple_function()
        captured1 = output_monitor.get_output

        # 第二次调用
        simple_function()
        captured2 = output_monitor.get_output

        assert captured1 != captured2  # 应该不同
        assert "Call at" in captured1
        assert "Call at" in captured2