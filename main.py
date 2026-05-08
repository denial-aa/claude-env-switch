import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from config_manager import EnvironmentManager
from script_manager import ScriptManager

class ClaudeEnvManagerApp:
    """Claude Code 环境管理工具的主界面"""
    
    def __init__(self):
        self.env_manager = EnvironmentManager()
        self.script_manager = ScriptManager()
        
        self.root = tk.Tk()
        self.root.title("Claude Code 环境管理器")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        self._setup_ui()
        self._refresh_env_list()
        self._update_current_env()
    
    def _setup_ui(self):
        """设置用户界面"""
        self.root.configure(bg='#f0f0f0')
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', rowheight=30, font=('Microsoft YaHei UI', 10))
        style.configure('Treeview.Heading', font=('Microsoft YaHei UI', 10, 'bold'))
        style.configure('TButton', font=('Microsoft YaHei UI', 10), padding=5)
        style.configure('TLabel', font=('Microsoft YaHei UI', 10), background='#f0f0f0')
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        current_env_frame = ttk.LabelFrame(main_frame, text="当前环境", padding="10")
        current_env_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_env_label = ttk.Label(current_env_frame, text="未设置", font=('Microsoft YaHei UI', 12, 'bold'))
        self.current_env_label.pack(side=tk.LEFT)
        
        self.refresh_current_btn = ttk.Button(current_env_frame, text="刷新", command=self._update_current_env)
        self.refresh_current_btn.pack(side=tk.RIGHT)
        
        env_list_frame = ttk.LabelFrame(main_frame, text="环境列表", padding="10")
        env_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ('name', 'config_dir', 'description', 'last_used')
        self.env_tree = ttk.Treeview(env_list_frame, columns=columns, show='headings', selectmode='browse')
        
        self.env_tree.heading('name', text='环境名称')
        self.env_tree.heading('config_dir', text='配置目录')
        self.env_tree.heading('description', text='描述')
        self.env_tree.heading('last_used', text='最后使用')
        
        self.env_tree.column('name', width=150, minwidth=100)
        self.env_tree.column('config_dir', width=300, minwidth=200)
        self.env_tree.column('description', width=200, minwidth=150)
        self.env_tree.column('last_used', width=150, minwidth=100)
        
        scrollbar = ttk.Scrollbar(env_list_frame, orient=tk.VERTICAL, command=self.env_tree.yview)
        self.env_tree.configure(yscrollcommand=scrollbar.set)
        
        self.env_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.env_tree.bind('<<TreeviewSelect>>', self._on_env_select)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_add = ttk.Button(button_frame, text="添加环境", command=self._show_add_env_dialog)
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_remove = ttk.Button(button_frame, text="删除环境", command=self._remove_env)
        btn_remove.pack(side=tk.LEFT, padx=5)
        
        btn_switch = ttk.Button(button_frame, text="切换环境", command=self._switch_env)
        btn_switch.pack(side=tk.LEFT, padx=5)
        
        btn_create_default = ttk.Button(button_frame, text="从默认创建", command=self._create_from_default)
        btn_create_default.pack(side=tk.LEFT, padx=5)
        
        script_frame = ttk.LabelFrame(main_frame, text="快速启动脚本", padding="10")
        script_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.script_status_label = ttk.Label(script_frame, text="")
        self.script_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn_create_script = ttk.Button(script_frame, text="创建脚本", command=self._create_script)
        btn_create_script.pack(side=tk.RIGHT, padx=5)
        
        btn_remove_script = ttk.Button(script_frame, text="删除脚本", command=self._remove_script)
        btn_remove_script.pack(side=tk.RIGHT, padx=5)
        
        btn_add_path = ttk.Button(script_frame, text="添加到 PATH", command=self._add_to_path)
        btn_add_path.pack(side=tk.RIGHT, padx=5)
        
        self._update_script_status()
    
    def _refresh_env_list(self):
        """刷新环境列表"""
        for item in self.env_tree.get_children():
            self.env_tree.delete(item)
        
        for env in self.env_manager.get_environments():
            self.env_tree.insert('', tk.END, values=(
                env['name'],
                env['config_dir'],
                env.get('description', ''),
                env.get('last_used', '从未')
            ))
    
    def _update_current_env(self):
        """更新当前环境显示"""
        current = self.env_manager.get_current_env()
        if current:
            self.current_env_label.config(text=f"{current['name']} - {current['config_dir']}")
        else:
            self.current_env_label.config(text="未设置 (使用默认 ~/.claude)")
    
    def _update_script_status(self):
        """更新脚本状态显示"""
        in_path = self.script_manager.check_scripts_in_path()
        if in_path:
            self.script_status_label.config(text=f"✓ 脚本目录已在 PATH 中: {self.script_manager.script_dir}")
        else:
            self.script_status_label.config(text=f"✗ 脚本目录未在 PATH 中: {self.script_manager.script_dir}")
    
    def _on_env_select(self, event):
        """环境选择事件"""
        pass
    
    def _get_selected_env(self):
        """获取选中的环境"""
        selection = self.env_tree.selection()
        if not selection:
            return None
        
        item = self.env_tree.item(selection[0])
        return item['values'][0]
    
    def _show_add_env_dialog(self):
        """显示添加环境对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加环境")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.configure(bg='#f0f0f0')
        
        ttk.Label(dialog, text="环境名称:", font=('Microsoft YaHei UI', 10)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=40, font=('Microsoft YaHei UI', 10))
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="配置目录:", font=('Microsoft YaHei UI', 10)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        
        dir_frame = ttk.Frame(dialog)
        dir_frame.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        dir_entry = ttk.Entry(dir_frame, width=30, font=('Microsoft YaHei UI', 10))
        dir_entry.pack(side=tk.LEFT)
        
        def browse_dir():
            directory = filedialog.askdirectory(title="选择配置目录")
            if directory:
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, directory)
        
        ttk.Button(dir_frame, text="浏览", command=browse_dir).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text="描述 (可选):", font=('Microsoft YaHei UI', 10)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        desc_entry = ttk.Entry(dialog, width=40, font=('Microsoft YaHei UI', 10))
        desc_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def add_env():
            name = name_entry.get().strip()
            config_dir = dir_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name:
                messagebox.showerror("错误", "请输入环境名称", parent=dialog)
                return
            
            if not config_dir:
                messagebox.showerror("错误", "请选择配置目录", parent=dialog)
                return
            
            try:
                self.env_manager.add_environment(name, config_dir, description)
                self._refresh_env_list()
                messagebox.showinfo("成功", f"环境 '{name}' 添加成功", parent=dialog)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("错误", str(e), parent=dialog)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="添加", command=add_env).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.grid_columnconfigure(1, weight=1)
    
    def _remove_env(self):
        """删除选中的环境"""
        env_name = self._get_selected_env()
        if not env_name:
            messagebox.showwarning("警告", "请先选择要删除的环境")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除环境 '{env_name}' 吗？\n（仅删除记录，不会删除实际文件）"):
            self.env_manager.remove_environment(env_name)
            self.script_manager.remove_startup_script(env_name)
            self._refresh_env_list()
            self._update_script_status()
            messagebox.showinfo("成功", f"环境 '{env_name}' 已删除")
    
    def _switch_env(self):
        """切换选中的环境"""
        env_name = self._get_selected_env()
        if not env_name:
            messagebox.showwarning("警告", "请先选择要切换的环境")
            return
        
        try:
            self.env_manager.switch_environment(env_name)
            self._update_current_env()
            self._refresh_env_list()
            messagebox.showinfo("成功", f"已切换到环境 '{env_name}'\n\n注意：此设置仅对当前进程有效。\n请使用快速启动脚本在新终端中启动。")
        except ValueError as e:
            messagebox.showerror("错误", str(e))
    
    def _create_from_default(self):
        """从默认环境创建"""
        dialog = tk.Toplevel(self.root)
        dialog.title("从默认环境创建")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.configure(bg='#f0f0f0')
        
        ttk.Label(dialog, text="新环境名称:", font=('Microsoft YaHei UI', 10)).pack(pady=10)
        name_entry = ttk.Entry(dialog, width=30, font=('Microsoft YaHei UI', 10))
        name_entry.pack(pady=5)
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入环境名称", parent=dialog)
                return
            
            try:
                self.env_manager.create_default_environment(name)
                self._refresh_env_list()
                messagebox.showinfo("成功", f"环境 '{name}' 创建成功", parent=dialog)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("错误", str(e), parent=dialog)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="创建", command=create).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _create_script(self):
        """为选中的环境创建快速启动脚本"""
        env_name = self._get_selected_env()
        if not env_name:
            messagebox.showwarning("警告", "请先选择要创建脚本的环境")
            return
        
        env = None
        for e in self.env_manager.get_environments():
            if e['name'] == env_name:
                env = e
                break
        
        if not env:
            return
        
        try:
            script_path = self.script_manager.create_startup_script(env_name, env['config_dir'])
            self._update_script_status()
            messagebox.showinfo("成功", f"脚本已创建: {script_path}\n\n将脚本目录添加到 PATH 后即可使用。")
        except Exception as e:
            messagebox.showerror("错误", f"创建脚本失败: {str(e)}")
    
    def _remove_script(self):
        """删除选中环境的快速启动脚本"""
        env_name = self._get_selected_env()
        if not env_name:
            messagebox.showwarning("警告", "请先选择要删除脚本的环境")
            return
        
        if self.script_manager.remove_startup_script(env_name):
            self._update_script_status()
            messagebox.showinfo("成功", f"脚本 '{env_name}.bat' 已删除")
        else:
            messagebox.showwarning("警告", f"脚本 '{env_name}.bat' 不存在")
    
    def _add_to_path(self):
        """将脚本目录添加到系统 PATH"""
        success, message = self.script_manager.add_scripts_to_path()
        self._update_script_status()
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == '__main__':
    app = ClaudeEnvManagerApp()
    app.run()
