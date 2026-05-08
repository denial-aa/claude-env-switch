import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config_manager import EnvironmentManager
from script_manager import ScriptManager

def test_environment_manager():
    """测试环境管理器"""
    print("=" * 50)
    print("测试环境管理器")
    print("=" * 50)
    
    manager = EnvironmentManager()
    
    print("\n1. 获取当前环境列表:")
    envs = manager.get_environments()
    print(f"   当前有 {len(envs)} 个环境")
    
    test_dir = Path.home() / ".claude-test-env"
    test_dir.mkdir(exist_ok=True)
    
    print("\n2. 添加测试环境:")
    try:
        manager.add_environment("test-env", str(test_dir), "测试环境")
        print("   ✓ 环境添加成功")
    except ValueError as e:
        print(f"   ! {e}")
    
    print("\n3. 更新环境列表:")
    envs = manager.get_environments()
    for env in envs:
        print(f"   - {env['name']}: {env['config_dir']}")
    
    print("\n4. 切换环境:")
    try:
        manager.switch_environment("test-env")
        print(f"   ✓ 已切换，CLAUDE_CONFIG_DIR = {os.environ.get('CLAUDE_CONFIG_DIR')}")
    except ValueError as e:
        print(f"   ✗ {e}")
    
    print("\n5. 删除测试环境:")
    manager.remove_environment("test-env")
    envs = manager.get_environments()
    print(f"   ✓ 删除后剩余 {len(envs)} 个环境")
    
    test_dir.rmdir()
    
    print("\n✓ 环境管理器测试完成")

def test_script_manager():
    """测试脚本管理器"""
    print("\n" + "=" * 50)
    print("测试脚本管理器")
    print("=" * 50)
    
    manager = ScriptManager()
    
    print("\n1. 创建测试脚本:")
    script_path = manager.create_startup_script("test-env", "D:\\test-config")
    print(f"   ✓ 脚本创建成功: {script_path}")
    
    print("\n2. 检查脚本是否存在:")
    exists = manager.script_exists("test-env")
    print(f"   {'✓' if exists else '✗'} 脚本{'存在' if exists else '不存在'}")
    
    print("\n3. 获取所有脚本:")
    scripts = manager.get_all_scripts()
    for script in scripts:
        print(f"   - {script['name']}: {script['path']}")
    
    print("\n4. 删除测试脚本:")
    manager.remove_startup_script("test-env")
    exists = manager.script_exists("test-env")
    print(f"   {'✓' if not exists else '✗'} 脚本{'已删除' if not exists else '仍存在'}")
    
    print("\n5. 检查 PATH 状态:")
    in_path = manager.check_scripts_in_path()
    print(f"   {'✓' if in_path else '✗'} 脚本目录{'已' if in_path else '未'}在 PATH 中")
    
    print("\n✓ 脚本管理器测试完成")

if __name__ == '__main__':
    test_environment_manager()
    test_script_manager()
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)
