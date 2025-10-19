"""
Тесты для рефакторинга GUI EvilEye

Проверяют основную функциональность WindowManager, BaseWindow и диалогов.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt
    pyqt_version = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt
    pyqt_version = 5

# Добавляем путь к модулям
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from evileye.visualization_modules.window_manager import WindowManager, WindowState
from evileye.visualization_modules.base_window import BaseWindow
from evileye.visualization_modules.dialogs import SaveConfirmationDialog, SaveAsDialog


class TestWindowManager(unittest.TestCase):
    """Тесты для WindowManager"""
    
    def setUp(self):
        """Настройка тестов"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        self.manager = WindowManager()
        self.test_widget = QWidget()
        self.test_widget.setWindowTitle("Test Window")
    
    def tearDown(self):
        """Очистка после тестов"""
        # Очищаем все окна
        for window_id in list(self.manager._windows.keys()):
            self.manager.unregister_window(window_id)
    
    def test_register_window(self):
        """Тест регистрации окна"""
        # Регистрируем окно
        result = self.manager.register_window(
            window_id="test_window",
            window_type="test",
            window_instance=self.test_widget
        )
        
        self.assertTrue(result)
        self.assertIn("test_window", self.manager._windows)
        
        # Проверяем информацию об окне
        window_info = self.manager.get_window("test_window")
        self.assertIsNotNone(window_info)
        self.assertEqual(window_info.window_type, "test")
        self.assertEqual(window_info.state, WindowState.OPEN)
    
    def test_unregister_window(self):
        """Тест отмены регистрации окна"""
        # Регистрируем окно
        self.manager.register_window(
            window_id="test_window",
            window_type="test",
            window_instance=self.test_widget
        )
        
        # Отменяем регистрацию
        result = self.manager.unregister_window("test_window")
        self.assertTrue(result)
        self.assertNotIn("test_window", self.manager._windows)
    
    def test_window_state_management(self):
        """Тест управления состоянием окна"""
        # Регистрируем окно
        self.manager.register_window(
            window_id="test_window",
            window_type="test",
            window_instance=self.test_widget
        )
        
        # Изменяем состояние
        self.manager.set_window_state("test_window", WindowState.MINIMIZED)
        window_info = self.manager.get_window("test_window")
        self.assertEqual(window_info.state, WindowState.MINIMIZED)
    
    def test_unsaved_changes_tracking(self):
        """Тест отслеживания несохраненных изменений"""
        # Регистрируем окно
        self.manager.register_window(
            window_id="test_window",
            window_type="test",
            window_instance=self.test_widget
        )
        
        # Устанавливаем флаг изменений
        self.manager.set_unsaved_changes("test_window", True)
        self.assertTrue(self.manager.has_unsaved_changes("test_window"))
        
        # Получаем список окон с изменениями
        windows_with_changes = self.manager.get_windows_with_unsaved_changes()
        self.assertIn("test_window", windows_with_changes)
    
    def test_get_windows_by_type(self):
        """Тест получения окон по типу"""
        # Регистрируем несколько окон разных типов
        widget1 = QWidget()
        widget2 = QWidget()
        
        self.manager.register_window("window1", "type1", widget1)
        self.manager.register_window("window2", "type1", widget2)
        self.manager.register_window("window3", "type2", QWidget())
        
        # Получаем окна типа "type1"
        type1_windows = self.manager.get_windows_by_type("type1")
        self.assertEqual(len(type1_windows), 2)
        
        # Получаем окна типа "type2"
        type2_windows = self.manager.get_windows_by_type("type2")
        self.assertEqual(len(type2_windows), 1)
    
    def test_status_summary(self):
        """Тест получения сводки о состоянии"""
        # Регистрируем несколько окон
        self.manager.register_window("window1", "type1", QWidget())
        self.manager.register_window("window2", "type1", QWidget())
        self.manager.set_unsaved_changes("window1", True)
        
        # Получаем сводку
        status = self.manager.get_status_summary()
        
        self.assertEqual(status['total_windows'], 2)
        self.assertEqual(status['unsaved_changes_count'], 1)
        self.assertIn('type1', status['windows_by_type'])
        self.assertEqual(status['windows_by_type']['type1'], 2)


class TestBaseWindow(unittest.TestCase):
    """Тесты для BaseWindow"""
    
    def setUp(self):
        """Настройка тестов"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def test_base_window_creation(self):
        """Тест создания BaseWindow"""
        # Создаем тестовый класс, наследующий BaseWindow
        class TestWindow(BaseWindow):
            def get_config_data(self):
                return {"test": "data"}
            
            def apply_config_data(self, config_data):
                return True
        
        window = TestWindow(
            window_id="test_window",
            window_type="test",
            config_file="test.json"
        )
        
        self.assertEqual(window.window_id, "test_window")
        self.assertEqual(window.window_type, "test")
        self.assertEqual(window.config_file, "test.json")
    
    def test_unsaved_changes_tracking(self):
        """Тест отслеживания несохраненных изменений в BaseWindow"""
        class TestWindow(BaseWindow):
            def get_config_data(self):
                return {"test": "data"}
            
            def apply_config_data(self, config_data):
                return True
            
            def on_config_changed(self, config_file):
                pass
        
        window = TestWindow("test_window", "test")
        
        try:
            # Проверяем начальное состояние
            self.assertFalse(window.has_unsaved_changes())
            
            # Устанавливаем изменения
            window.set_unsaved_changes(True)
            self.assertTrue(window.has_unsaved_changes())
            
            # Проверяем, что заголовок обновился
            self.assertTrue(window.windowTitle().endswith('*'))
        finally:
            # Очищаем окно
            window.close()
    
    def test_config_save_load(self):
        """Тест сохранения и загрузки конфигурации"""
        class TestWindow(BaseWindow):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.data = {"initial": "value"}
            
            def get_config_data(self):
                return self.data
            
            def apply_config_data(self, config_data):
                self.data = config_data
                return True
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            window = TestWindow("test_window", "test", temp_file)
            
            # Изменяем данные
            window.data = {"modified": "value"}
            
            # Сохраняем
            result = window.save_config()
            self.assertTrue(result)
            
            # Проверяем, что файл создан
            self.assertTrue(os.path.exists(temp_file))
            
            # Загружаем в новое окно
            new_window = TestWindow("test_window2", "test", temp_file)
            result = new_window.load_config(temp_file)
            self.assertTrue(result)
            self.assertEqual(new_window.data, {"modified": "value"})
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestDialogs(unittest.TestCase):
    """Тесты для диалогов"""
    
    def setUp(self):
        """Настройка тестов"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def test_save_confirmation_dialog(self):
        """Тест диалога подтверждения сохранения"""
        dialog = SaveConfirmationDialog("Test Window", "test.json")
        
        # Проверяем, что диалог создался
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.window_title, "Test Window")
        self.assertEqual(dialog.config_file, "test.json")
        
        # Проверяем начальное состояние
        self.assertEqual(dialog.get_selected_action().value, "cancel")
    
    def test_save_as_dialog(self):
        """Тест диалога 'Сохранить как'"""
        dialog = SaveAsDialog("test.json")
        
        # Проверяем, что диалог создался
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.current_file, "test.json")


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        """Настройка тестов"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def test_window_manager_integration(self):
        """Тест интеграции WindowManager с BaseWindow"""
        class TestWindow(BaseWindow):
            def get_config_data(self):
                return {"test": "data"}
            
            def apply_config_data(self, config_data):
                return True
        
        # Создаем окно
        window = TestWindow("test_window", "test")
        
        # Проверяем, что окно зарегистрировалось в WindowManager
        manager = window._window_manager
        self.assertIsNotNone(manager)
        
        window_info = manager.get_window("test_window")
        self.assertIsNotNone(window_info)
        self.assertEqual(window_info.window_type, "test")
    
    def test_global_window_manager(self):
        """Тест глобального WindowManager"""
        from evileye.visualization_modules.window_manager import get_window_manager
        
        # Получаем глобальный менеджер
        global_manager = get_window_manager()
        self.assertIsInstance(global_manager, WindowManager)
        
        # Проверяем, что это singleton
        new_manager = get_window_manager()
        self.assertEqual(global_manager, new_manager)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()
