import os
import subprocess
from pathlib import Path

class ScriptManager:
    """管理快速启动脚本"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent / "scripts"
        self.script_dir.mkdir(exist_ok=True)
    
    def create_startup_script(self, env_name, config_dir):
        """为指定环境创建快速启动脚本"""
        script_path = self.script_dir / f"{env_name}.bat"
        
        bat_content = f"""@echo off
set CLAUDE_CONFIG_DIR={config_dir}
claude %*
"""
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        return str(script_path)
    
    def remove_startup_script(self, env_name):
        """删除快速启动脚本"""
        script_path = self.script_dir / f"{env_name}.bat"
        if script_path.exists():
            script_path.unlink()
            return True
        return False
    
    def get_script_path(self, env_name):
        """获取脚本路径"""
        return str(self.script_dir / f"{env_name}.bat")
    
    def script_exists(self, env_name):
        """检查脚本是否存在"""
        return (self.script_dir / f"{env_name}.bat").exists()
    
    def add_scripts_to_path(self):
        """将脚本目录添加到系统 PATH"""
        script_dir_str = str(self.script_dir)
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 f'[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;{script_dir_str}", "User")'],
                capture_output=True,
                text=True,
                check=True
            )
            
            os.environ['PATH'] = f"{os.environ.get('PATH', '')};{script_dir_str}"
            return True, "已添加到系统 PATH"
        except subprocess.CalledProcessError as e:
            return False, f"添加失败: {e.stderr}"
    
    def check_scripts_in_path(self):
        """检查脚本目录是否在 PATH 中"""
        path_env = os.environ.get('PATH', '')
        return str(self.script_dir) in path_env
    
    def get_all_scripts(self):
        """获取所有脚本"""
        scripts = []
        for bat_file in self.script_dir.glob("*.bat"):
            scripts.append({
                'name': bat_file.stem,
                'path': str(bat_file)
            })
        return scripts
