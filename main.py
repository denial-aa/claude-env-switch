import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, 
                             QFileDialog, QDialog, QLineEdit, QGroupBox,
                             QStatusBar, QAbstractItemView)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor
from config_manager import EnvironmentManager
from script_manager import ScriptManager


class AddEnvironmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加环境")
        self.setFixedSize(550, 280)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        name_layout = QHBoxLayout()
        name_label = QLabel("环境名称:")
        name_label.setFixedWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: work, personal")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        dir_layout = QHBoxLayout()
        dir_label = QLabel("配置目录:")
        dir_label.setFixedWidth(100)
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("选择 Claude 配置目录")
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)
        
        desc_layout = QHBoxLayout()
        desc_label = QLabel("描述 (可选):")
        desc_label.setFixedWidth(100)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("环境描述信息")
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("添加")
        self.ok_btn.setObjectName("primaryBtn")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def _browse_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择配置目录")
        if directory:
            self.dir_input.setText(directory)
    
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'config_dir': self.dir_input.text().strip(),
            'description': self.desc_input.text().strip()
        }


class CreateFromDefaultDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("从默认环境创建")
        self.setFixedSize(400, 150)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        name_layout = QHBoxLayout()
        name_label = QLabel("新环境名称:")
        name_label.setFixedWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入新环境名称")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("创建")
        self.ok_btn.setObjectName("primaryBtn")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
    
    def get_name(self):
        return self.name_input.text().strip()


class ClaudeEnvManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.env_manager = EnvironmentManager()
        self.script_manager = ScriptManager()
        
        self.setWindowTitle("Claude Code 环境管理器")
        self.resize(1000, 700)
        self.setMinimumSize(850, 600)
        
        self._setup_ui()
        self._setup_styles()
        self._refresh_env_list()
        self._update_current_env()
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        current_env_group = QGroupBox("当前环境")
        current_env_layout = QHBoxLayout(current_env_group)
        self.current_env_label = QLabel("未设置")
        self.current_env_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Weight.Bold))
        self.refresh_current_btn = QPushButton("刷新")
        self.refresh_current_btn.setFixedWidth(80)
        self.refresh_current_btn.clicked.connect(self._update_current_env)
        current_env_layout.addWidget(self.current_env_label)
        current_env_layout.addStretch()
        current_env_layout.addWidget(self.refresh_current_btn)
        main_layout.addWidget(current_env_group)
        
        env_list_group = QGroupBox("环境列表")
        env_list_layout = QVBoxLayout(env_list_group)
        
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(4)
        self.env_table.setHorizontalHeaderLabels(["环境名称", "配置目录", "描述", "最后使用"])
        self.env_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.env_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.env_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.env_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.env_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.env_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.env_table.verticalHeader().setVisible(False)
        self.env_table.setAlternatingRowColors(True)
        env_list_layout.addWidget(self.env_table)
        main_layout.addWidget(env_list_group)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加环境")
        self.btn_remove = QPushButton("删除环境")
        self.btn_switch = QPushButton("切换环境")
        self.btn_create_default = QPushButton("从默认创建")
        self.btn_reset = QPushButton("恢复默认")
        
        self.btn_add.clicked.connect(self._show_add_env_dialog)
        self.btn_remove.clicked.connect(self._remove_env)
        self.btn_switch.clicked.connect(self._switch_env)
        self.btn_create_default.clicked.connect(self._create_from_default)
        self.btn_reset.clicked.connect(self._reset_env)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_switch)
        btn_layout.addWidget(self.btn_create_default)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        script_group = QGroupBox("快速启动脚本")
        script_layout = QHBoxLayout(script_group)
        self.script_status_label = QLabel("")
        self.btn_create_script = QPushButton("创建脚本")
        self.btn_remove_script = QPushButton("删除脚本")
        self.btn_add_path = QPushButton("添加到 PATH")
        
        self.btn_create_script.clicked.connect(self._create_script)
        self.btn_remove_script.clicked.connect(self._remove_script)
        self.btn_add_path.clicked.connect(self._add_to_path)
        
        script_layout.addWidget(self.script_status_label)
        script_layout.addStretch()
        script_layout.addWidget(self.btn_create_script)
        script_layout.addWidget(self.btn_remove_script)
        script_layout.addWidget(self.btn_add_path)
        main_layout.addWidget(script_group)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        self._update_script_status()
    
    def _setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QPushButton#primaryBtn {
                background-color: #0078d4;
                color: white;
                border: 1px solid #0078d4;
            }
            QPushButton#primaryBtn:hover {
                background-color: #106ebe;
            }
            QPushButton#primaryBtn:pressed {
                background-color: #005a9e;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 6px;
                gridline-color: #e0e0e0;
                background-color: white;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #cce8ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #f8f8f8;
                border: none;
                border-bottom: 2px solid #cccccc;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QLabel {
                font-size: 13px;
            }
            QStatusBar {
                background-color: #f8f8f8;
                border-top: 1px solid #cccccc;
            }
        """)
    
    def _refresh_env_list(self):
        self.env_table.setRowCount(0)
        
        for env in self.env_manager.get_environments():
            row = self.env_table.rowCount()
            self.env_table.insertRow(row)
            self.env_table.setItem(row, 0, QTableWidgetItem(env['name']))
            self.env_table.setItem(row, 1, QTableWidgetItem(env['config_dir']))
            self.env_table.setItem(row, 2, QTableWidgetItem(env.get('description', '')))
            self.env_table.setItem(row, 3, QTableWidgetItem(env.get('last_used', '从未')))
        
        self.status_bar.showMessage(f"共 {self.env_table.rowCount()} 个环境")
    
    def _update_current_env(self):
        current = self.env_manager.get_current_env()
        if current:
            self.current_env_label.setText(f"{current['name']} - {current['config_dir']}")
        else:
            self.current_env_label.setText("未设置 (使用默认 ~/.claude)")
    
    def _update_script_status(self):
        in_path = self.script_manager.check_scripts_in_path()
        if in_path:
            self.script_status_label.setText(f"✓ 脚本目录已在 PATH 中: {self.script_manager.script_dir}")
            self.script_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.script_status_label.setText(f"✗ 脚本目录未在 PATH 中: {self.script_manager.script_dir}")
            self.script_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def _get_selected_env(self):
        selected = self.env_table.selectedItems()
        if not selected:
            return None
        return selected[0].text()
    
    def _show_add_env_dialog(self):
        dialog = AddEnvironmentDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            
            if not data['name']:
                QMessageBox.warning(self, "错误", "请输入环境名称")
                return
            
            if not data['config_dir']:
                QMessageBox.warning(self, "错误", "请选择配置目录")
                return
            
            try:
                self.env_manager.add_environment(data['name'], data['config_dir'], data['description'])
                self._refresh_env_list()
                QMessageBox.information(self, "成功", f"环境 '{data['name']}' 添加成功")
                self.status_bar.showMessage(f"环境 '{data['name']}' 已添加")
            except ValueError as e:
                QMessageBox.critical(self, "错误", str(e))
    
    def _remove_env(self):
        env_name = self._get_selected_env()
        if not env_name:
            QMessageBox.warning(self, "警告", "请先选择要删除的环境")
            return
        
        reply = QMessageBox.question(self, "确认删除", 
                                     f"确定要删除环境 '{env_name}' 吗？\n（仅删除记录，不会删除实际文件）",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.env_manager.remove_environment(env_name)
            self.script_manager.remove_startup_script(env_name)
            self._refresh_env_list()
            self._update_script_status()
            QMessageBox.information(self, "成功", f"环境 '{env_name}' 已删除")
            self.status_bar.showMessage(f"环境 '{env_name}' 已删除")
    
    def _switch_env(self):
        env_name = self._get_selected_env()
        if not env_name:
            QMessageBox.warning(self, "警告", "请先选择要切换的环境")
            return
        
        try:
            self.env_manager.switch_environment(env_name)
            self._update_current_env()
            self._refresh_env_list()
            QMessageBox.information(self, "成功", 
                                   f"已切换到环境 '{env_name}'\n\n环境变量已持久化到系统设置，新终端将自动使用此环境。")
            self.status_bar.showMessage(f"已切换到环境 '{env_name}'")
        except ValueError as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def _reset_env(self):
        try:
            self.env_manager.clear_environment()
            self._update_current_env()
            QMessageBox.information(self, "成功", "已恢复默认环境（使用 ~/.claude）\n\n新终端将使用默认配置。")
            self.status_bar.showMessage("已恢复默认环境")
        except RuntimeError as e:
            QMessageBox.critical(self, "错误", str(e))
    
    def _create_from_default(self):
        dialog = CreateFromDefaultDialog(self)
        if dialog.exec():
            name = dialog.get_name()
            
            if not name:
                QMessageBox.warning(self, "错误", "请输入环境名称")
                return
            
            try:
                self.env_manager.create_default_environment(name)
                self._refresh_env_list()
                QMessageBox.information(self, "成功", f"环境 '{name}' 创建成功")
                self.status_bar.showMessage(f"环境 '{name}' 已创建")
            except ValueError as e:
                QMessageBox.critical(self, "错误", str(e))
    
    def _create_script(self):
        env_name = self._get_selected_env()
        if not env_name:
            QMessageBox.warning(self, "警告", "请先选择要创建脚本的环境")
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
            QMessageBox.information(self, "成功", f"脚本已创建: {script_path}\n\n将脚本目录添加到 PATH 后即可使用。")
            self.status_bar.showMessage(f"脚本 '{env_name}.bat' 已创建")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建脚本失败: {str(e)}")
    
    def _remove_script(self):
        env_name = self._get_selected_env()
        if not env_name:
            QMessageBox.warning(self, "警告", "请先选择要删除脚本的环境")
            return
        
        if self.script_manager.remove_startup_script(env_name):
            self._update_script_status()
            QMessageBox.information(self, "成功", f"脚本 '{env_name}.bat' 已删除")
            self.status_bar.showMessage(f"脚本 '{env_name}.bat' 已删除")
        else:
            QMessageBox.warning(self, "警告", f"脚本 '{env_name}.bat' 不存在")
    
    def _add_to_path(self):
        success, message = self.script_manager.add_scripts_to_path()
        self._update_script_status()
        if success:
            QMessageBox.information(self, "成功", message)
            self.status_bar.showMessage("脚本目录已添加到 PATH")
        else:
            QMessageBox.critical(self, "错误", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ClaudeEnvManagerApp()
    window.show()
    sys.exit(app.exec())
