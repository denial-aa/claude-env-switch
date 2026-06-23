import os
import shlex
import subprocess
from pathlib import Path


class ScriptManager:
    """管理快速启动脚本"""

    def __init__(self):
        self.script_dir = Path(__file__).parent / "scripts"
        self.script_dir.mkdir(exist_ok=True)
        self.bash_profile = Path.home() / ".bash_profile"

    def _bash_profile_contains(self, text: str) -> bool:
        """检查 ~/.bash_profile 是否包含某段文本"""
        if not self.bash_profile.exists():
            return False
        return text in self.bash_profile.read_text()

    def create_startup_script(self, env_name, config_dir):
        """为指定环境创建快速启动脚本"""
        script_path = self.script_dir / f"{env_name}.sh"

        sh_content = f"""#!/bin/bash
export CLAUDE_CONFIG_DIR={shlex.quote(config_dir)}
exec claude "$@"
"""

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(sh_content)
        os.chmod(script_path, 0o755)

        return str(script_path)

    def remove_startup_script(self, env_name):
        """删除快速启动脚本"""
        script_path = self.script_dir / f"{env_name}.sh"
        if script_path.exists():
            script_path.unlink()
            return True
        return False

    def get_script_path(self, env_name):
        """获取脚本路径"""
        return str(self.script_dir / f"{env_name}.sh")

    def script_exists(self, env_name):
        """检查脚本是否存在"""
        return (self.script_dir / f"{env_name}.sh").exists()

    def add_scripts_to_path(self):
        """将脚本目录添加到 ~/.bash_profile 的 PATH"""
        script_dir_str = str(self.script_dir)

        # 检查是否已添加
        if self._bash_profile_contains(f"$PATH:{script_dir_str}"):
            return True, "已在 PATH 中"

        line = f'export PATH="$PATH:{script_dir_str}"'
        with open(self.bash_profile, 'a', encoding='utf-8') as f:
            f.write(line + "\n")

        os.environ['PATH'] = f"{os.environ.get('PATH', '')}:{script_dir_str}"
        return True, "已添加到 PATH（新终端窗口生效）"

    def check_scripts_in_path(self):
        """检查脚本目录是否在 PATH 中"""
        path_env = os.environ.get('PATH', '')
        return str(self.script_dir) in path_env

    def get_all_scripts(self):
        """获取所有脚本"""
        scripts = []
        for sh_file in self.script_dir.glob("*.sh"):
            scripts.append({
                'name': sh_file.stem,
                'path': str(sh_file)
            })
        return scripts
