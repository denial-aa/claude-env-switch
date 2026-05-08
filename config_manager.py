import os
import json
import shutil
import winreg
import ctypes
import subprocess
from pathlib import Path
from datetime import datetime

class EnvironmentManager:
    """管理 Claude Code 研发环境的核心类"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "environments.json"
        self.environments = self._load_environments()
    
    def _load_environments(self):
        """从配置文件加载环境列表"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_environments(self):
        """保存环境列表到配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.environments, f, indent=2, ensure_ascii=False)
    
    def get_environments(self):
        """获取所有环境"""
        return self.environments
    
    def add_environment(self, name, config_dir, description=""):
        """添加新环境"""
        if any(env['name'] == name for env in self.environments):
            raise ValueError(f"环境 '{name}' 已存在")
        
        if not Path(config_dir).exists():
            raise ValueError(f"配置目录不存在: {config_dir}")
        
        env = {
            'name': name,
            'config_dir': str(Path(config_dir).resolve()),
            'description': description,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_used': None
        }
        
        self.environments.append(env)
        self._save_environments()
        return env
    
    def remove_environment(self, name):
        """删除环境（仅删除记录，不删除实际文件）"""
        self.environments = [env for env in self.environments if env['name'] != name]
        self._save_environments()
    
    def update_environment(self, old_name, name=None, config_dir=None, description=None):
        """更新环境信息"""
        for env in self.environments:
            if env['name'] == old_name:
                if name is not None:
                    env['name'] = name
                if config_dir is not None:
                    env['config_dir'] = str(Path(config_dir).resolve())
                if description is not None:
                    env['description'] = description
                self._save_environments()
                return env
        raise ValueError(f"环境 '{old_name}' 不存在")
    
    def switch_environment(self, name):
        """切换到指定环境（设置系统环境变量）"""
        for env in self.environments:
            if env['name'] == name:
                # 设置当前进程的环境变量
                os.environ['CLAUDE_CONFIG_DIR'] = env['config_dir']
                
                # 使用 setx 设置用户级别的环境变量（持久化）
                try:
                    result = subprocess.run(
                        ['setx', 'CLAUDE_CONFIG_DIR', env['config_dir']],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    # 广播环境变量变更
                    self._broadcast_env_change()
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"设置系统环境变量失败: {e.stderr}")
                
                env['last_used'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._save_environments()
                return env
        raise ValueError(f"环境 '{name}' 不存在")
    
    def clear_environment(self):
        """清除 CLAUDE_CONFIG_DIR 环境变量（恢复默认）"""
        # 清除当前进程的环境变量
        if 'CLAUDE_CONFIG_DIR' in os.environ:
            del os.environ['CLAUDE_CONFIG_DIR']
        
        # 使用 setx 清除用户级别的环境变量
        try:
            subprocess.run(
                ['setx', 'CLAUDE_CONFIG_DIR', ''],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 广播环境变量变更
            self._broadcast_env_change()
            
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"清除系统环境变量失败: {e.stderr}")
    
    def get_current_env(self):
        """获取当前激活的环境"""
        # 优先从系统用户环境变量获取（持久化的值）
        try:
            current_dir = winreg.QueryValueEx(
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment'),
                'CLAUDE_CONFIG_DIR'
            )[0]
        except FileNotFoundError:
            current_dir = os.environ.get('CLAUDE_CONFIG_DIR')
        
        if not current_dir:
            return None
        
        for env in self.environments:
            if env['config_dir'] == current_dir:
                return env
        
        return {
            'name': 'Unknown',
            'config_dir': current_dir,
            'description': '当前环境变量设置，但未在管理中注册'
        }
    
    def create_default_environment(self, name):
        """创建默认环境（从 ~/.claude 复制）"""
        home = Path.home()
        default_claude_dir = home / ".claude"
        
        if not default_claude_dir.exists():
            raise ValueError("默认的 ~/.claude 目录不存在，请先安装并运行 Claude Code")
        
        new_env_dir = home / ".claude-envs" / name
        
        if new_env_dir.exists():
            raise ValueError(f"环境目录已存在: {new_env_dir}")
        
        shutil.copytree(default_claude_dir, new_env_dir)
        
        return self.add_environment(
            name=name,
            config_dir=str(new_env_dir),
            description=f"从默认环境创建"
        )
