#!/usr/bin/env python3
"""
更新配置文件中的任务参数
"""

import sys
import os
from pathlib import Path

# 添加框架路径
sys.path.insert(0, str(Path(__file__).parent))

from core.config_manager import ConfigManager
from ubox_py_sdk import RunMode


def update_task_config(job_id, serial_num, os_type, app_name, auth_code=None):
    """
    更新配置文件中的任务参数
    
    Args:
        job_id: 任务ID
        serial_num: 设备序列号
        os_type: 操作系统类型
        app_name: 应用包名
        auth_code: 设备认证码（可选）
    """
    # 配置文件路径
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')

    try:
        # 使用ConfigManager更新config
        config_manager = ConfigManager(config_path)
        config_manager.update_config(job_id, serial_num, os_type, app_name, RunMode.NORMAL, auth_code)

        print(
            f"配置文件已更新: job_id={job_id}, serial_num={serial_num}, os_type={os_type}, app_name={app_name}, mode=normal")
        return True

    except Exception as e:
        print(f"更新配置文件失败: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("用法: uv run update_config.py <job_id> <serial_num> <os_type> <app_name> [auth_code]")
        sys.exit(1)

    job_id = sys.argv[1]
    serial_num = sys.argv[2]
    os_type = sys.argv[3]
    app_name = sys.argv[4]
    auth_code = sys.argv[5] if len(sys.argv) > 5 else None

    success = update_task_config(job_id, serial_num, os_type, app_name, auth_code)
    sys.exit(0 if success else 1)
