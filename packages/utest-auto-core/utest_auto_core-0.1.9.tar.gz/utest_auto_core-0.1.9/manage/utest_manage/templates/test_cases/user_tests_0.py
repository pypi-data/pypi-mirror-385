#!/usr/bin/env python3

import time
import traceback
import random
from core.test_case import TestCase, StepStatus, FailureStrategy
from ubox_py_sdk import DriverType, OSType, DeviceButton, EventHandler, Device


class GameAutomationTest(TestCase):
    """游戏自动化测试用例"""

    def __init__(self, device: Device):
        super().__init__(
            name="视频游戏自动化测试",
            description="测试游戏界面的自动化交互功能，包括元素点击和随机操作",
            device=device
        )
        # 初始化事件处理器
        self.event_handler = self.device.handler

        # 测试配置
        self.game_url = "https://s.iwan.qq.com/opengame/tenvideo/index.html?hidestatusbar=1&hidetitlebar=1&immersive=1&syswebview=1&gameid=55423&url=https://h5.xiwangame.com/initlogin/aiwan/2277/&ref_ele=10003&isFromJump=1&isDarkMode=0&uiType=REGULAR"
        self.total_run_time = 30  # 总运行时间（秒）
        self.common_buttons = ['道城', '修士', '助战', '历练', '梦道', '挑战', '跳过', '确定']
        # 为每个按钮设置偏移量 (x_offset, y_offset)
        self.button_offsets = {
            '道城': (0, -50),
            '修士': (0, -50),
            '助战': (0, -50),
            '历练': (0, -50),
            '梦道': (-200, 0),
            '挑战': (0, -50),
            '跳过': (-10, 10)
        }
        self.random_click_probability = 0.7  # 随机点击概率

        # 设置失败策略为继续执行，收集所有失败信息
        # self.failure_strategy = FailureStrategy.CONTINUE_ON_FAILURE
        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE

    def setup(self) -> None:
        """测试前置操作"""
        self.log_info("开始准备测试环境...")

        event_handler = self.event_handler
        event_handler.reset()
        event_handler.watcher("打开").with_match_mode("strict").when("打开").click()
        event_handler.watcher("确定").with_match_mode("strict").when("确定").click()
        # event_handler.watcher("允许").when("允许访问一次").click()
        # event_handler.watcher("升级").when('//*[@content-desc="关闭弹窗"]').click()
        # event_handler.watcher("同意").when("同意").click()
        # event_handler.watcher("同意并继续").when("同意并继续").click()
        # 开始后台监控
        event_handler.start(2.0)
        self.start_record()
        # 启动应用
        package_name = self.get_package_name()
        if package_name:
            self.start_step("启动应用", f"启动应用: {package_name}")
            success = self.device.start_app(package_name)
            self.assert_true(f"应用启动成功", success)
            if success:
                time.sleep(2)
                self.end_step(StepStatus.PASSED)
            else:
                self.end_step(StepStatus.FAILED)
        else:
            self.log_warning("未配置应用包名，跳过应用启动")

    def teardown(self) -> None:
        """测试后置操作"""
        self.log_info("开始清理测试环境...")
        # # 停止监控
        # self.event_handler.stop()
        # 停止应用
        package_name = self.get_package_name()
        if package_name:
            self.device.stop_app(package_name)
            self.log_info(f"应用已停止: {package_name}")

        # 返回主界面
        self.device.press(DeviceButton.HOME)
        self.log_info("已返回主界面")
        self.stop_record()

    def run_test(self) -> None:
        """执行游戏自动化测试"""
        # 进入游戏
        self.enter_game()
        self.start_perf()
        # 开始游戏自动化操作
        self.perform_game_automation()
        self.stop_perf()

    def enter_game(self) -> None:
        """进入游戏界面"""
        self.start_step("进入游戏", "通过URL进入游戏界面")

        # 使用ADB命令启动游戏URL
        cmd = f"am start -a android.intent.action.VIEW -p mark.via -d '{self.game_url}'"
        result = self.device.cmd_adb(cmd, timeout=10)
        self.log_info(f"启动游戏URL命令执行结果: {result}")

        # 等待页面加载
        time.sleep(2)
        self.device.click('//*[@content-desc="刷新网页"]')
        time.sleep(1)
        # 点击浏览器打开按钮
        self.start_step("点击浏览器打开", "查找并点击浏览器打开按钮")
        self.device.click('//*[@text="确定"]', by=DriverType.UI, timeout=10)
        self.end_step(StepStatus.PASSED)
        # # 点击"进入小游戏"按钮
        # self.start_step("点击进入小游戏", "查找并点击进入小游戏按钮")
        # # 使用OCR查找"进入小游戏"按钮
        # click_result = self.device.click("进入小游戏", by=DriverType.OCR, timeout=10)
        # if click_result:
        #     self.assert_true("点击进入小游戏按钮", click_result)
        #     self.end_step(StepStatus.PASSED)
        # else:
        #     # 尝试使用UI查找
        #     click_result = self.device.click("//*[@text='进入小游戏']", by=DriverType.UI, timeout=10)
        #     self.assert_true("成功点击进入小游戏按钮(UI)", click_result)
        #     self.end_step(StepStatus.PASSED)

        self.log_info(f"已进入游戏: {self.game_url}")
        time.sleep(6)  # 等待游戏加载

        # 处理游戏协议弹窗
        self.handle_game_agreement()

        self.end_step(StepStatus.PASSED)

    def handle_game_agreement(self) -> None:
        """处理游戏协议弹窗"""
        self.start_step("处理游戏协议", "检测并处理游戏协议弹窗")

        # 检查是否还有"进入游戏"按钮
        button_exists = self.device.find_ocr("进入游戏", timeout=5)
        if not button_exists:
            self.log_info("没有看到进入游戏尝试点击确定弹窗")
            c = self.device.click("确定", by=DriverType.OCR, timeout=10, crop_box=[0, 1, 0, 0.5])
            self.assert_true("点击确定弹窗", c)

        # 首次尝试点击进入游戏按钮
        click_result = self.device.click("进入游戏", by=DriverType.OCR, timeout=5)
        if click_result:
            self.log_info("首次点击进入游戏按钮成功")

        # 等待10秒检测是否仍在游戏界面，如果仍在则再次点击进入游戏
        time.sleep(10)
        # 检查是否还有"进入游戏"按钮
        button_exists = self.device.find_ocr("进入游戏", timeout=10)
        if button_exists:
            self.log_info("检测到进入游戏按钮，处理协议弹窗")
            # crop_box：屏蔽图片上边界0.2的高度(0, 1, 0, 0.2)，保留图片上边界0.2的区域[[0, 0.2], [1, 0.2]]
            # crop_box: 屏蔽范围或者保留范围 均为百分比
            #           保留范围: 保留矩形范围的<左上角顶点>坐标和<右下角>坐标, 示例 [[0.3, 0.3], [0.7, 0.7]]
            #           屏蔽范围: [0, 1, 0, 0.3] 屏蔽x轴 0-1, y轴0-0.3的部分
            res = self.device.get_element_ocr("我已经详细阅读并同意", by=DriverType.OCR,
                                              timeout=10, crop_box=[[0.08, 0.65], [0.9, 0.8]])
            x, y, dx, dy = res['bounds']
            h = dy - y
            center_y = y + h / 2
            click_result = self.device.click_pos([x - h, center_y])
            self.log_info(f"权限对号坐标{x - h}:{center_y}")
            if click_result:
                # 再次点击进入游戏按钮
                click_result = self.device.click("进入游戏", by=DriverType.OCR, timeout=5)
                if click_result:
                    self.log_info("协议处理后成功点击进入游戏")
        self.end_step(StepStatus.PASSED)

    def perform_game_automation(self) -> None:
        """执行游戏自动化操作"""
        self.start_step("游戏自动化操作", f"开始执行游戏自动化操作，持续 {self.total_run_time // 60} 分钟")

        start_time = time.time()
        self.log_info(f"开始循环点击页面元素，将持续 {self.total_run_time // 60} 分钟...")

        while time.time() - start_time < self.total_run_time:
            # 识别其他常见游戏按钮
            for btn_text in self.common_buttons:
                # 获取该按钮的偏移量
                offset = self.button_offsets.get(btn_text, (0, 0))
                # 应用偏移量点击
                click_result = self.device.click(btn_text, by=DriverType.OCR, offset=offset, timeout=3)
                if click_result:
                    self.log_info(f"成功点击按钮: {btn_text} (偏移量: {offset})")
                else:
                    self.log_warning(f"未识别到按钮: {btn_text}")
                time.sleep(0.5)
            # 随机点击屏幕位置作为备用方案
            self.perform_random_click()
            self.log_info("一轮元素点击遍历完成，准备开始下一轮...")

        self.log_info("已达到设定的运行时间，程序结束。")
        self.end_step(StepStatus.PASSED)

    def perform_random_click(self) -> None:
        """执行随机点击操作"""
        # 获取屏幕尺寸
        w, h = self.device.screen_size()

        # 生成随机坐标（避免边缘区域）
        x = random.randint(int(0.1 * w), int(0.9 * w))
        y = random.randint(int(0.1 * h), int(0.9 * h))

        # 执行点击
        click_result = self.device.click_pos([x / w, y / h])  # 转换为相对坐标
        if click_result:
            self.log_info(f"随机点击成功: ({x}, {y})")
        else:
            self.log_warning(f"随机点击失败: ({x}, {y})")

        time.sleep(1)

    def navigate_back_to_game_list(self) -> None:
        """导航回游戏列表"""
        self.start_step("返回游戏列表", "从游戏界面返回到游戏列表")

        # 按返回键
        self.device.press("back")
        self.log_info("已返回游戏列表")
        time.sleep(1)
        self.end_step(StepStatus.PASSED)
