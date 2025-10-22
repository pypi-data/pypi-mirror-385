# -*- coding: utf-8 -*-
"""
utest-manage CLI 实现（已与根仓库解耦）

子命令：
- init：初始化脚本目录（从模板复制、创建虚拟环境并安装依赖）
- new-case：在 test_cases 下创建新用例
- build：构建包（优先 uv build）
- clean：清理构建产物
"""

import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path
import importlib.metadata
import tempfile
import urllib.request
import zipfile


class CommandLineTool:
    """命令行管理工具主类"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="UTest 自动化测试框架管理工具",
            epilog="""
使用示例：
  # 查看版本信息
  utest-manage --version

  # 初始化（从远程模板直接解压到目标目录；失败回退本地模板）
  utest-manage init my_test_project
  utest-manage init ./my_test_project --force

  # 在框架目录中创建测试用例
  cd my_test_project
  utest-manage new-case MyTestCase

  # 更新核心文件（默认更新全部核心项）
  utest-manage update-core
  # 仅更新部分核心项（多次 --files 或逗号分隔）
  utest-manage update-core --files uv.toml --files start_test
  utest-manage update-core --files "uv.toml,run.sh,internal"
  # 指定目标目录并强制覆盖
  utest-manage update-core /path/to/project --force

  # 清理构建产物
  utest-manage clean
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # 动态获取版本号
        try:
            # 尝试从已安装的包中获取版本号
            version = importlib.metadata.version('utest-auto-manage')
        except importlib.metadata.PackageNotFoundError:
            # 如果包未安装，尝试从 pyproject.toml 读取
            try:
                import tomllib
                pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
                with open(pyproject_path, 'rb') as f:
                    data = tomllib.load(f)
                version = data['project']['version']
            except (FileNotFoundError, KeyError, ImportError):
                # 如果都失败了，使用默认版本号
                version = '0.1.15'

        # 添加版本参数
        self.parser.add_argument(
            '--version', '-V',
            action='version',
            version=f'%(prog)s {version}',
            help='显示版本信息并退出'
        )
        subparsers = self.parser.add_subparsers(dest="command", help="可用子命令")

        case_parser = subparsers.add_parser(
            "new-case",
            help="创建新的测试用例文件（需在框架目录中执行）",
            description="""在 test_cases 目录下创建完整的测试用例模板文件，包含：
• setup/teardown 前置后置操作示例
• 性能监控、录制、logcat 收集功能
• 多种断言方法使用示例
• 日志记录和截图功能
• 异常处理策略
• 性能数据记录

注意：必须在已初始化的框架目录中执行此命令。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        case_parser.add_argument("name", help="测试用例文件名（不含 .py 扩展名，会自动转换为类名）")
        case_parser.set_defaults(func=self.new_case)


        clean_parser = subparsers.add_parser(
            "clean",
            help="清理构建产物和临时文件（需在框架目录中执行）",
            description="""清理项目中的临时文件和构建产物，包括：
• 构建目录（dist/、build/）
• 测试结果目录（test_result/）
• Python 缓存文件（__pycache__/、*.pyc、*.pyo）
• 日志文件（*.log）
• 压缩包文件（*.zip、*.whl）
• 包信息目录（*.egg-info/）

注意：必须在已初始化的框架目录中执行此命令。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        clean_parser.set_defaults(func=self.clean)

        # init 命令
        init_parser = subparsers.add_parser(
            "init",
            help="初始化新的测试框架项目（可在任何目录执行）",
            description="""从模板创建完整的测试框架项目，包括：
• 远程模板ZIP下载并直接解压到目标目录（失败回退本地模板）
• 复制所有模板文件（配置文件、测试用例、脚本等）
• 自动安装 uv 工具（如果未安装）
• 创建 Python 3.10.12 虚拟环境
• 安装项目依赖
• 提供虚拟环境激活命令

参数说明：
• 目标可以是【路径】或【项目名】
  - 若为相对/绝对路径：将在该路径创建/覆盖项目
  - 若为纯项目名：将在当前目录下创建同名子目录

此命令可在任何目录执行，会在指定目录创建新的框架项目。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        init_parser.add_argument("target", nargs="?", default=".", help="目标路径或项目名（默认：当前目录）。支持相对/绝对路径；若仅为名称，将在当前目录下创建同名项目目录。")
        init_parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件（默认：检查冲突后退出）")
        init_parser.set_defaults(func=self.init_only_scripts)

        # update-core 命令：更新核心文件
        update_parser = subparsers.add_parser(
            "update-core",
            help="更新当前目录或指定目录的核心文件（支持指定文件或全部）",
            description=(
                "从远程模板（失败回退本地模板）更新以下核心文件：\n"
                "- uv.toml\n- update_config.py\n- start_test.py\n- run.sh\n- requirements.txt\n- build.py\n- test_cases/internal/ 目录包\n\n"
                "支持：\n"
                "- 默认更新全部核心项\n"
                "- 使用 --files 选择部分项（可多次传入或用逗号分隔）\n"
                "- 使用 --force 强制覆盖\n\n"
                "示例：\n"
                "  utest-manage update-core\n"
                "  utest-manage update-core --files uv.toml --files start_test\n"
                "  utest-manage update-core --files 'uv.toml,run.sh,internal'\n"
                "  utest-manage update-core /path/to/project --force\n"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        update_parser.add_argument("target", nargs="?", default=".", help="目标路径（默认：当前目录）")
        update_parser.add_argument(
            "--files",
            action="append",
            help=(
                "指定需要更新的文件/目录，支持多次传入或逗号分隔。"
                "可用别名：uv.toml|uvtoml, update_config, start_test, run.sh|run_sh, requirements|requirements.txt, build|build.py, internal"
            )
        )
        update_parser.add_argument("--force", action="store_true", help="强制覆盖目标文件/目录")
        update_parser.set_defaults(func=self.update_core)

    # ----------------- 子命令实现 -----------------

    def _check_framework_directory(self) -> bool:
        """检查当前目录是否为有效的框架目录"""
        required_files = ["config.yml", "start_test.py", "requirements.txt", "run.sh", "update_config.py", "uv.toml"]
        required_dirs = ["test_cases"]

        for file in required_files:
            if not Path(file).exists():
                print(f"❌ 当前目录不是有效的框架目录，缺少文件：{file}")
                print("请先使用 'init' 命令初始化框架，或切换到正确的框架目录")
                return False

        for dir_name in required_dirs:
            if not Path(dir_name).exists() or not Path(dir_name).is_dir():
                print(f"❌ 当前目录不是有效的框架目录，缺少目录：{dir_name}")
                print("请先使用 'init' 命令初始化框架，或切换到正确的框架目录")
                return False

        return True

    def init_only_scripts(self, args) -> None:
        """初始化脚本工程：
        1) 从远程模板包下载并解压到目标目录（优先远程，其次本地回退）；
        2) 在目标目录创建虚拟环境：uv venv --python 3.10.12；
        3) 打印平台对应的激活命令；
        4) 使用虚拟环境安装 requirements.txt 依赖。
        """
        target_dir = Path(args.target).resolve()

        # 远程模板ZIP下载地址（由用户提供）
        TEMPLATE_ZIP_URL = (
            "https://lab-paas-apk-1254257443.cos.ap-nanjing.myqcloud.com/utestAutoScriptTemp/ubox-script-temp-master.zip"
        )

        def download_and_extract_template(url: str, extract_to: Path) -> bool:
            """下载远程模板并解压到指定目录。

            Args:
                url: 模板ZIP下载链接
                extract_to: 解压目标路径
            Returns:
                bool: 是否成功下载并解压
            """
            try:
                extract_to.mkdir(parents=True, exist_ok=True)
                # 使用临时文件保存ZIP
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_path = Path(tmpdir) / "template.zip"
                    print(f"正在从远程下载模板: {url}")
                    # 下载ZIP（内置urllib，避免新增依赖）
                    urllib.request.urlretrieve(url, zip_path.as_posix())
                    print("模板下载完成，开始解压...")
                    # 解压ZIP
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(extract_to)
                    print(f"模板解压完成: {extract_to}")
                return True
            except Exception as e:
                print(f"⚠️ 远程模板下载或解压失败：{e}")
                return False

        def copy_from_local_templates(dest: Path) -> bool:
            """从本地 manage/templates 拷贝模板（远程失败时回退）。"""
            # 模板路径：优先使用包内的模板，如果不存在则使用开发环境的模板
            tpl_root = Path(__file__).parent / "templates"
            if not tpl_root.exists():
                tpl_root = Path(__file__).resolve().parents[1] / "templates"
            if not tpl_root.exists():
                print("未找到本地模板目录：manage/templates。")
                return False
            for item in tpl_root.iterdir():
                dst = dest / item.name
                if item.is_dir():
                    shutil.copytree(item, dst, dirs_exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)
            return True

        # 防护：存在关键文件且未 --force 时不覆盖
        if target_dir.exists() and not args.force:
            key_files = [target_dir / "config.yml", target_dir / "start_test.py"]
            if any(p.exists() for p in key_files):
                print(f"目标目录 {target_dir} 已存在，并包含关键文件。使用 --force 覆盖。")
                return

        target_dir.mkdir(parents=True, exist_ok=True)

        # 先清空（在 --force 时）
        if any(target_dir.iterdir()) and args.force:
            for child in list(target_dir.iterdir()):
                try:
                    if child.is_dir():
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
                except Exception as e:
                    print(f"⚠️ 清理目标目录项失败 {child}: {e}")

        # 1) 优先远程下载模板
        extracted_ok = False
        tmp_extract_dir = target_dir / "._tpl_tmp_extract"
        if download_and_extract_template(TEMPLATE_ZIP_URL, tmp_extract_dir):
            # 远程包通常会带一个根目录，尝试探测并将其内容搬运到目标目录
            try:
                # 找到唯一根目录，否则就用当前解压目录
                subdirs = [p for p in tmp_extract_dir.iterdir() if p.is_dir()]
                copy_root = subdirs[0] if len(subdirs) == 1 else tmp_extract_dir
                for item in copy_root.iterdir():
                    dst = target_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst, dirs_exist_ok=True)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dst)
                extracted_ok = True
            except Exception as e:
                print(f"⚠️ 远程模板拷贝失败：{e}")
            finally:
                # 清理临时解压目录
                shutil.rmtree(tmp_extract_dir, ignore_errors=True)

        # 2) 若远程失败，回退本地模板
        if not extracted_ok:
            print("正在回退到本地模板...")
            if not copy_from_local_templates(target_dir):
                print("❌ 初始化失败：无法获取模板（远程与本地均不可用）")
                return
            else:
                print("✅ 已从本地模板完成初始化")

        # 检查并安装 uv
        def check_uv_installed() -> bool:
            """检查 uv 是否已安装"""
            try:
                subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False

        def install_uv() -> bool:
            """根据操作系统安装 uv"""
            print("检测到未安装 uv，正在自动安装...")

            if os.name == "nt":  # Windows
                print("在 Windows 上安装 uv...")
                try:
                    cmd = [
                        "powershell", "-ExecutionPolicy", "ByPass", "-c",
                        "irm https://astral.sh/uv/install.ps1 | iex"
                    ]
                    subprocess.check_call(cmd)
                    print("✅ uv 安装完成")
                    return True
                except Exception as e:
                    print(f"❌ Windows 上安装 uv 失败：{e}")
                    print(
                        "请手动安装：powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
                    return False
            else:  # Linux/macOS
                print("在 Linux/macOS 上安装 uv...")
                try:
                    # 尝试 curl
                    try:
                        cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"]
                        subprocess.check_call("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True)
                        print("✅ uv 安装完成（使用 curl）")
                        return True
                    except:
                        # 如果 curl 失败，尝试 wget
                        cmd = ["wget", "-qO-", "https://astral.sh/uv/install.sh", "|", "sh"]
                        subprocess.check_call("wget -qO- https://astral.sh/uv/install.sh | sh", shell=True)
                        print("✅ uv 安装完成（使用 wget）")
                        return True
                except Exception as e:
                    print(f"❌ Linux/macOS 上安装 uv 失败：{e}")
                    print("请手动安装：")
                    print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
                    print("  或")
                    print("  wget -qO- https://astral.sh/uv/install.sh | sh")
                    return False

        # 检查 uv 是否已安装
        if not check_uv_installed():
            if not install_uv():
                print("❌ 无法安装 uv，请手动安装后重试")
                return
        else:
            print("✅ 检测到 uv 已安装")

        # 创建虚拟环境：uv venv --python 3.10.12
        def run(cmd, cwd=None, capture_output=False, shell=False) -> bool:
            """运行外部命令，失败时返回 False。"""
            try:
                if isinstance(cmd, str):
                    print("执行：" + cmd)
                else:
                    print("执行：" + " ".join(cmd))

                if capture_output:
                    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=shell)
                    if result.returncode != 0:
                        print(f"命令失败，返回码：{result.returncode}")
                        if result.stdout:
                            print(f"标准输出：{result.stdout}")
                        if result.stderr:
                            print(f"错误输出：{result.stderr}")
                        return False
                    return True
                else:
                    subprocess.check_call(cmd, cwd=cwd, shell=shell)
                    return True
            except Exception as e:
                print(f"命令失败：{e}")
                return False

        created = run(["uv", "venv", "--python", "3.10.12"], cwd=str(target_dir))
        if not created:
            print("❌ 未能创建虚拟环境，请检查 Python 3.10.12 是否可用")

        # 计算 venv 内 Python 路径（不要求已激活）
        if os.name == "nt":
            venv_python = target_dir / ".venv" / "Scripts" / "python.exe"
            activate_hint = ".\\.venv\\Scripts\\Activate.ps1"
        else:
            venv_python = target_dir / ".venv" / "bin" / "python"
            activate_hint = "source .venv/bin/activate"

        # 安装依赖：激活虚拟环境后使用 uv pip 安装
        req_file = target_dir / "requirements.txt"
        if req_file.exists():
            # 根据操作系统选择激活脚本
            if os.name == "nt":  # Windows
                # 优先尝试使用批处理文件激活（更稳定）
                activate_bat = target_dir / ".venv" / "Scripts" / "activate.bat"
                if activate_bat.exists():
                    # 使用正确的引号转义
                    install_cmd = f"call \"{activate_bat}\" && uv pip install -r requirements.txt"
                    print(f"尝试使用 CMD 激活虚拟环境并安装依赖...")
                    # 直接使用字符串而不是列表，避免引号问题
                    installed = run(f'cmd /c "{install_cmd}"', cwd=str(target_dir), capture_output=True, shell=True)
                else:
                    # 如果批处理文件不存在，尝试 PowerShell（需要设置执行策略）
                    activate_script = target_dir / ".venv" / "Scripts" / "Activate.ps1"
                    if activate_script.exists():
                        # 使用 -ExecutionPolicy Bypass 绕过执行策略限制
                        install_cmd = f"& '{activate_script}'; uv pip install -r requirements.txt"
                        print(f"尝试使用 PowerShell 激活虚拟环境并安装依赖...")
                        installed = run(f'powershell -ExecutionPolicy Bypass -Command "{install_cmd}"',
                                        cwd=str(target_dir), capture_output=True, shell=True)
                    else:
                        print("未找到虚拟环境激活脚本，跳过依赖安装。")
                        installed = False
            else:  # Linux/macOS
                activate_script = target_dir / ".venv" / "bin" / "activate"
                if activate_script.exists():
                    # 在 bash 中激活虚拟环境并安装依赖
                    install_cmd = f"source {activate_script} && uv pip install -r requirements.txt"
                    print(f"尝试使用 bash 激活虚拟环境并安装依赖...")
                    installed = run(f'bash -c "{install_cmd}"', cwd=str(target_dir), capture_output=True, shell=True)
                else:
                    print("未找到虚拟环境激活脚本，跳过依赖安装。")
                    installed = False

            if not installed:
                print("依赖安装失败，可手动在激活环境后执行：")
                if os.name == "nt":
                    print(
                        "  Windows CMD: .venv\\Scripts\\activate.bat && uv pip install -r requirements.txt --index-strategy unsafe-best-match")
                    print(
                        "  Windows PowerShell: .venv\\Scripts\\Activate.ps1 && uv pip install -r requirements.txt --index-strategy unsafe-best-match")
                else:
                    print(
                        "  Linux/macOS: source .venv/bin/activate && uv pip install -r requirements.txt --index-strategy unsafe-best-match")
        else:
            print("未找到 requirements.txt，跳过依赖安装。")

        # 打印激活提示（区分平台）
        print("虚拟环境已创建在目标目录下的 .venv")
        if os.name == "nt":
            print(f"PowerShell 激活命令：{activate_hint}")
            print("若使用 CMD：.\\.venv\\Scripts\\activate.bat")
        else:
            print(f"bash/zsh 激活命令：{activate_hint}")

        print(f"已初始化脚本工程：{target_dir}")

    def update_core(self, args) -> None:
        """更新核心文件/目录到目标路径。

        行为：
        1) 优先从远程模板ZIP获取最新文件，失败则回退本地 manage/templates。
        2) 默认更新全部核心项；若提供 --files 则仅更新所选项。
        3) --force 时无条件覆盖；否则仅在不存在时写入，存在则提示跳过。
        """
        target_dir = Path(args.target).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        # 远程模板ZIP下载地址
        TEMPLATE_ZIP_URL = (
            "https://lab-paas-apk-1254257443.cos.ap-nanjing.myqcloud.com/utestAutoScriptTemp/ubox-script-temp-master.zip"
        )

        # 定义核心文件映射（模板内的相对路径 -> 目标内的相对路径）
        # 这里源与目标相同命名，若模板结构不同可在此调整映射
        core_map = {
            "uv.toml": "uv.toml",
            "update_config.py": "update_config.py",
            "start_test.py": "start_test.py",
            "run.sh": "run.sh",
            "requirements.txt": "requirements.txt",
            "build.py": "build.py",
            "test_cases/internal": "test_cases/internal",
        }

        # 别名支持，便于 --files 传入
        alias_map = {
            "uv.toml": "uv.toml",
            "update_config": "update_config.py",
            "start_test": "start_test.py",
            "run.sh": "run.sh",
            "run_sh": "run.sh",
            "requirements": "requirements.txt",
            "requirements.txt": "requirements.txt",
            "build": "build.py",
            "build.py": "build.py",
            "internal": "test_cases/internal",
        }

        # 解析 --files 选择；为空则表示全部
        selected_relpaths = set()
        if args.files:
            for entry in args.files:
                for token in str(entry).split(','):
                    name = token.strip()
                    if not name:
                        continue
                    # 映射到真实相对路径
                    if name in alias_map:
                        selected_relpaths.add(alias_map[name])
                    elif name in core_map:
                        selected_relpaths.add(name)
                    else:
                        print(f"⚠️ 未识别的文件别名/路径：{name}，已忽略")
        else:
            # 默认全部
            selected_relpaths = set(core_map.keys())

        # 下载远程模板到临时目录，并确定源根目录
        def fetch_source_root() -> Path:
            """获取模板源根目录：优先远程，失败回退本地 manage/templates。"""
            # 1) 远程
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_extract = Path(tmpdir) / "extract"
                tmp_extract.mkdir(parents=True, exist_ok=True)
                try:
                    print(f"正在下载远程模板：{TEMPLATE_ZIP_URL}")
                    zip_path = Path(tmpdir) / "tpl.zip"
                    urllib.request.urlretrieve(TEMPLATE_ZIP_URL, zip_path.as_posix())
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(tmp_extract)
                    # 检测是否单根目录
                    entries = [p for p in tmp_extract.iterdir() if p.name != "__MACOSX"]
                    if len(entries) == 1 and entries[0].is_dir():
                        # 只有一个根目录，进入它
                        src_root = entries[0]
                    else:
                        src_root = tmp_extract
                    # 将远程源复制到一个持久目录再返回（避免with结束被删除）
                    persist_dir = Path(tempfile.mkdtemp(prefix="utest_tpl_src_"))
                    # 仅复制，不过滤，以便后续匹配路径
                    for item in src_root.iterdir():
                        if item.name == "__MACOSX":
                            continue
                        dst = persist_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dst)
                    print("✅ 已获取远程模板")
                    return persist_dir
                except Exception as e:
                    print(f"⚠️ 远程模板获取失败，回退本地模板：{e}")

            # 2) 本地回退
            tpl_root = Path(__file__).parent / "templates"
            if not tpl_root.exists():
                tpl_root = Path(__file__).resolve().parents[1] / "templates"
            if not tpl_root.exists():
                raise RuntimeError("未找到本地模板目录：manage/templates")
            print("✅ 使用本地模板目录")
            return tpl_root

        try:
            source_root = fetch_source_root()
        except Exception as e:
            print(f"❌ 无法获取模板源：{e}")
            return

        def copy_entry(relpath: str) -> None:
            """复制单个映射项（文件或目录）。"""
            src = source_root / relpath
            dst = target_dir / core_map.get(relpath, relpath)
            if not src.exists():
                print(f"⚠️ 模板中缺少项：{relpath}，已跳过")
                return
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    # 目录复制：force 则先删再拷；否则增量覆盖
                    if dst.exists() and args.force:
                        shutil.rmtree(dst, ignore_errors=True)
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    if dst.exists() and not args.force:
                        print(f"⏭ 已存在且未使用 --force，跳过：{dst}")
                        return
                    shutil.copy2(src, dst)
                print(f"✓ 已更新：{relpath} -> {dst}")
            except Exception as e:
                print(f"⚠️ 更新失败：{relpath} -> {dst}，原因：{e}")

        # 执行复制
        for rel in sorted(selected_relpaths):
            copy_entry(rel)

        print(f"✅ 核心文件更新完成，目标目录：{target_dir}")

    def new_case(self, args) -> None:
        """在 test_cases 目录下创建一个完整的示例用例文件"""
        # 检查是否在框架目录中
        if not self._check_framework_directory():
            return

        name = args.name
        tc_dir = Path("test_cases")
        tc_dir.mkdir(parents=True, exist_ok=True)
        file_path = tc_dir / f"{name}.py"
        if file_path.exists():
            print(f"文件已存在：{file_path}")
            return

        content = (
            "# -*- coding: utf-8 -*-\n"
            "\"\"\"\n"
            "测试用例示例：{cls}\n"
            "\n"
            "本文件展示了完整的测试用例编写模式，包括：\n"
            "- setup/teardown 前置后置操作\n"
            "- 性能监控和录制功能\n"
            "- 多种断言方法\n"
            "- 日志记录和截图\n"
            "- 错误处理策略\n"
            "\"\"\"\n"
            "import time\n"
            "from core import TestCase, StepStatus, FailureStrategy\n"
            "\n"
            "\n"
            "class {cls}(TestCase):\n"
            "    \"\"\"{cls} 测试用例类\"\"\"\n"
            "\n"
            "    def __init__(self, device):\n"
            "        super().__init__(\n"
            "            name='{cls}',\n"
            "            description='完整的测试用例示例，展示各种功能用法',\n"
            "            device=device\n"
            "        )\n"
            "        # 配置测试用例参数\n"
            "        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE  # 失败时停止\n"
            "        self.timeout = 300  # 5分钟超时\n"
            "        self.retry_count = 1  # 失败时重试1次\n"
            "        self.screenshot_on_failure = True  # 失败时截图\n"
            "        self.screenshot_on_success = False  # 成功时不截图\n"
            "\n"
            "    def setup(self):\n"
            "        \"\"\"测试前置操作\"\"\"\n"
            "        self.log_info(\"开始执行测试前置操作\")\n"
            "        \n"
            "        # 启动性能监控（可选）\n"
            "        self.log_info(\"启动性能监控\")\n"
            "        if self.start_perf(sub_process_name='com.example.app', case_name=self.name):\n"
            "            self.log_info(\"性能监控启动成功\")\n"
            "        else:\n"
            "            self.log_warning(\"性能监控启动失败\")\n"
            "        \n"
            "        # 启动录制（可选）\n"
            "        self.log_info(\"启动屏幕录制\")\n"
            "        if self.start_record():\n"
            "            self.log_info(\"屏幕录制启动成功\")\n"
            "        else:\n"
            "            self.log_warning(\"屏幕录制启动失败\")\n"
            "        \n"
            "        # 启动logcat收集（可选）\n"
            "        self.log_info(\"启动logcat收集\")\n"
            "        logcat_task = self.start_logcat(clear=True)\n"
            "        if logcat_task:\n"
            "            self.log_info(\"logcat收集启动成功\")\n"
            "        else:\n"
            "            self.log_warning(\"logcat收集启动失败\")\n"
            "        \n"
            "        # 等待设备稳定\n"
            "        self.log_info(\"等待设备稳定...\")\n"
            "        time.sleep(2)\n"
            "\n"
            "    def teardown(self):\n"
            "        \"\"\"测试后置操作\"\"\"\n"
            "        self.log_info(\"开始执行测试后置操作\")\n"
            "        \n"
            "        # 停止性能监控\n"
            "        if hasattr(self, '_perf_task'):\n"
            "            self.log_info(\"停止性能监控\")\n"
            "            if self.stop_perf():\n"
            "                self.log_info(\"性能监控停止成功\")\n"
            "            else:\n"
            "                self.log_warning(\"性能监控停止失败\")\n"
            "        \n"
            "        # 停止录制\n"
            "        self.log_info(\"停止屏幕录制\")\n"
            "        if self.stop_record():\n"
            "            self.log_info(\"屏幕录制停止成功\")\n"
            "        else:\n"
            "            self.log_warning(\"屏幕录制停止失败\")\n"
            "        \n"
            "        # 清理临时数据（可选）\n"
            "        self.log_info(\"清理测试数据\")\n"
            "        # 这里可以添加清理逻辑，比如删除临时文件等\n"
            "\n"
            "    def run_test(self):\n"
            "        \"\"\"执行测试用例主逻辑\"\"\"\n"
            "        \n"
            "        # 步骤1：基础功能验证\n"
            "        self.start_step('基础功能验证', '验证基本断言功能')\n"
            "        \n"
            "        # 基础断言示例\n"
            "        self.assert_true('True应该为真', True)\n"
            "        self.assert_false('False应该为假', False)\n"
            "        self.assert_equal('数字相等验证', 1 + 1, 2)\n"
            "        self.assert_not_equal('数字不等验证', 1, 2)\n"
            "        self.assert_contains('字符串包含验证', 'Hello World', 'World')\n"
            "        self.assert_not_contains('字符串不包含验证', 'Hello', 'Python')\n"
            "        self.assert_none('None值验证', None)\n"
            "        self.assert_not_none('非None值验证', 'Hello')\n"
            "        self.assert_greater_than('大于比较', 10, 5)\n"
            "        self.assert_less_than('小于比较', 3, 7)\n"
            "        \n"
            "        # 记录日志\n"
            "        self.log_info(\"基础断言验证完成\")\n"
            "        \n"
            "        # 截图示例\n"
            "        screenshot_path = self.take_screenshot('basic_verification')\n"
            "        if screenshot_path:\n"
            "            self.log_info(f\"截图已保存: {{screenshot_path}}\")\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        # 步骤2：设备信息获取\n"
            "        self.start_step('设备信息获取', '获取并验证设备相关信息')\n"
            "        \n"
            "        # 获取设备信息\n"
            "        device_serial = self.get_device_serial()\n"
            "        package_name = self.get_package_name()\n"
            "        \n"
            "        self.log_info(f\"设备序列号: {{device_serial}}\")\n"
            "        self.log_info(f\"测试包名: {{package_name}}\")\n"
            "        \n"
            "        # 验证设备信息不为空\n"
            "        self.assert_not_none('设备序列号不应为空', device_serial)\n"
            "        \n"
            "        # 等待一段时间模拟测试操作\n"
            "        self.log_info(\"模拟测试操作，等待3秒...\")\n"
            "        time.sleep(3)\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        # 步骤3：异常处理示例\n"
            "        self.start_step('异常处理测试', '测试异常情况的处理')\n"
            "        \n"
            "        try:\n"
            "            # 模拟可能出错的操作\n"
            "            result = 10 / 2  # 正常操作\n"
            "            self.assert_equal('除法运算结果', result, 5)\n"
            "            \n"
            "            # 模拟异常情况（注释掉，避免真的出错）\n"
            "            # result = 10 / 0  # 这会引发异常\n"
            "            \n"
            "            self.log_info(\"异常处理测试完成\")\n"
            "            \n"
            "        except Exception as e:\n"
            "            self.log_error(f\"捕获到异常: {{e}}\")\n"
            "            # 根据失败策略，这里会抛出异常或继续执行\n"
            "            self.assert_true('异常处理验证', False)  # 这会触发失败策略\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        # 步骤4：性能数据记录\n"
            "        self.start_step('性能数据记录', '记录测试过程中的性能数据')\n"
            "        \n"
            "        # 记录自定义性能数据\n"
            "        performance_data = {{\n"
            "            'test_duration': 10.5,\n"
            "            'memory_usage': 128.5,\n"
            "            'cpu_usage': 15.2,\n"
            "            'custom_metric': 'test_value'\n"
            "        }}\n"
            "        \n"
            "        self.record_performance_data(performance_data)\n"
            "        self.log_info(\"性能数据记录完成\")\n"
            "        \n"
            "        # 最终截图\n"
            "        self.take_screenshot('test_completion')\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        self.log_info(\"测试用例执行完成\")\n"
        ).format(cls=name[:1].upper() + name[1:])

        file_path.write_text(content, encoding="utf-8")
        print(f"已创建完整示例用例：{file_path}")
        print("该示例包含：")
        print("- setup/teardown 前置后置操作")
        print("- 性能监控、录制、logcat收集")
        print("- 多种断言方法示例")
        print("- 日志记录和截图功能")
        print("- 异常处理策略")
        print("- 性能数据记录")

    def clean(self, args) -> None:
        """清理构建产物和临时文件"""
        # 检查是否在框架目录中
        if not self._check_framework_directory():
            return

        print("开始清理构建产物和临时文件...")

        # 需要清理的目录和文件
        cleanup_items = [
            "dist/",
            "build/",
            "test_result/",
            "*.egg-info/",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.log",
            "*.zip",
        ]

        cleaned_count = 0

        # 清理目录
        for pattern in cleanup_items:
            if pattern.endswith('/'):
                # 目录模式
                dir_name = pattern[:-1]
                if Path(dir_name).exists() and Path(dir_name).is_dir():
                    try:
                        shutil.rmtree(dir_name, ignore_errors=True)
                        print(f"  ✓ 已删除目录：{dir_name}")
                        cleaned_count += 1
                    except Exception as e:
                        print(f"  ⚠ 删除目录失败：{dir_name} - {e}")
            else:
                # 文件模式
                for item in Path('.').glob(pattern):
                    if item.is_file():
                        try:
                            item.unlink()
                            print(f"  ✓ 已删除文件：{item}")
                            cleaned_count += 1
                        except Exception as e:
                            print(f"  ⚠ 删除文件失败：{item} - {e}")
                    elif item.is_dir():
                        try:
                            shutil.rmtree(item, ignore_errors=True)
                            print(f"  ✓ 已删除目录：{item}")
                            cleaned_count += 1
                        except Exception as e:
                            print(f"  ⚠ 删除目录失败：{item} - {e}")

        # 清理 test_cases 下的 __pycache__
        test_cases_dir = Path("test_cases")
        if test_cases_dir.exists():
            for pycache_dir in test_cases_dir.rglob("__pycache__"):
                try:
                    shutil.rmtree(pycache_dir, ignore_errors=True)
                    print(f"  ✓ 已删除：{pycache_dir}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ⚠ 删除失败：{pycache_dir} - {e}")

        if cleaned_count > 0:
            print(f"✅ 清理完成，共清理了 {cleaned_count} 个项目")
        else:
            print("ℹ️ 没有找到需要清理的文件或目录")


def main() -> None:
    tool = CommandLineTool()
    args = tool.parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        tool.parser.print_help()


if __name__ == "__main__":
    main()
