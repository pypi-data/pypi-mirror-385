from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
#!/usr/bin/env python3
"""
Тесты для системы атрибутов: ROI, ассоциации, тайминги, FSM.
"""

import unittest
import time
from unittest.mock import Mock, patch

# Импорты для тестирования
from evileye.attributes_detection.roi_feeder import RoiFeeder
from evileye.attributes_detection.attribute_classifier import AttributeClassifier
from evileye.objects_handler.attribute_state import AttributeState
from evileye.objects_handler.attribute_manager import AttributeManager
from evileye.objects_handler.objects_handler import ObjectsHandler
from evileye.core.frame import Frame


class TestAttributeState(unittest.TestCase):
    """Тесты структуры состояния атрибута."""
    
    # Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_attribute_state_creation(self):
        """Создание состояния атрибута."""
        state = AttributeState(name="hard_hat")
        self.assertEqual(state.name, "hard_hat")
        self.assertEqual(state.state, "none")
        self.assertEqual(state.confidence_smooth, 0.0)
        self.assertEqual(state.frames_present, 0)
        self.assertEqual(state.total_time_ms, 0)
        self.assertEqual(state.enter_count, 0)
        self.assertIsNone(state.enter_ts)
        self.assertIsNone(state.last_seen_ts)
    
    def test_reset_presence(self):
        """Сброс накопленных данных присутствия."""
        state = AttributeState(name="hard_hat")
        state.frames_present = 10
        state.total_time_ms = 1000
        state.enter_ts = time.time()
        
        state.reset_presence()
        
        self.assertEqual(state.frames_present, 0)
        self.assertEqual(state.total_time_ms, 0)
        self.assertIsNone(state.enter_ts)


class TestAttributeManager(unittest.TestCase):
    """Тесты менеджера атрибутов."""
    
    def setUp(self):
        """Настройка тестов."""
        self.conf_thresholds = {"hard_hat": 0.5, "backpack": 0.6}
        self.time_thresholds = {
            "hard_hat": {"min_time_ms": 600, "confirm_time_ms": 2000},
            "backpack": {"min_time_ms": 800, "confirm_time_ms": 2500}
        }
        self.manager = AttributeManager(self.conf_thresholds, self.time_thresholds, ema_alpha=0.7)
    
    def test_manager_creation(self):
        """Создание менеджера атрибутов."""
        self.assertEqual(self.manager._thr_conf, self.conf_thresholds)
        self.assertEqual(self.manager._thr_time, self.time_thresholds)
        self.assertEqual(self.manager._ema_alpha, 0.7)
    
    def test_get_states_empty(self):
        """Получение состояний для несуществующего трека."""
        states = self.manager.get_states(999)
        self.assertEqual(states, {})
    
    def test_update_new_attribute(self):
        """Обновление нового атрибута."""
        track_id = 1
        attr_name = "hard_hat"
        now_ts = time.time()
        
        # Первое обновление с детекцией
        self.manager.update(track_id, attr_name, True, 0.8, now_ts, 100)
        
        states = self.manager.get_states(track_id)
        self.assertIn(attr_name, states)
        state = states[attr_name]
        self.assertEqual(state.name, attr_name)
        self.assertEqual(state.frames_present, 1)
        self.assertEqual(state.total_time_ms, 100)
        self.assertEqual(state.state, "none")  # Ещё не достигли confirm_time_ms
    
    def test_fsm_none_to_exists(self):
        """Переход состояния none -> exists."""
        track_id = 1
        attr_name = "hard_hat"
        now_ts = time.time()
        
        # Накапливаем время до confirm_time_ms
        for i in range(25):  # 25 * 100ms = 2500ms > 2000ms
            self.manager.update(track_id, attr_name, True, 0.8, now_ts + i * 0.1, 100)
        
        states = self.manager.get_states(track_id)
        state = states[attr_name]
        self.assertEqual(state.state, "exists")
        self.assertEqual(state.enter_count, 1)
        self.assertIsNotNone(state.enter_ts)
    
    def test_fsm_exists_to_lost(self):
        """Переход состояния exists -> lost."""
        track_id = 1
        attr_name = "hard_hat"
        now_ts = time.time()
        
        # Сначала подтверждаем атрибут
        for i in range(25):
            self.manager.update(track_id, attr_name, True, 0.8, now_ts + i * 0.1, 100)
        
        # Затем перестаём детектировать
        for i in range(10):  # 10 * 100ms = 1000ms > 600ms (min_time_ms)
            self.manager.update(track_id, attr_name, False, 0.0, now_ts + 2.5 + i * 0.1, 100)
        
        states = self.manager.get_states(track_id)
        state = states[attr_name]
        self.assertEqual(state.state, "lost")
    
    def test_fsm_lost_to_none(self):
        """Переход состояния lost -> none."""
        track_id = 1
        attr_name = "hard_hat"
        now_ts = time.time()
        
        # Подтверждаем атрибут
        for i in range(25):
            self.manager.update(track_id, attr_name, True, 0.8, now_ts + i * 0.1, 100)
        
        # Переводим в lost
        for i in range(10):
            self.manager.update(track_id, attr_name, False, 0.0, now_ts + 2.5 + i * 0.1, 100)
        
        # Продолжаем отсутствие детекции до confirm_time_ms
        for i in range(20):  # 20 * 100ms = 2000ms >= 2000ms (confirm_time_ms)
            self.manager.update(track_id, attr_name, False, 0.0, now_ts + 3.5 + i * 0.1, 100)
        
        states = self.manager.get_states(track_id)
        state = states[attr_name]
        self.assertEqual(state.state, "none")
        self.assertEqual(state.frames_present, 0)  # Сброшено
        self.assertEqual(state.total_time_ms, 0)   # Сброшено
    
    def test_ema_smoothing(self):
        """Тест EMA-сглаживания confidence."""
        track_id = 1
        attr_name = "hard_hat"
        now_ts = time.time()
        
        # Первое значение
        self.manager.update(track_id, attr_name, True, 0.8, now_ts, 100)
        states = self.manager.get_states(track_id)
        state = states[attr_name]
        # EMA для первого значения: alpha * new + (1-alpha) * 0 = alpha * new
        expected_first = 0.7 * 0.8
        self.assertAlmostEqual(state.confidence_smooth, expected_first, places=5)
        
        # Второе значение с EMA
        self.manager.update(track_id, attr_name, True, 0.4, now_ts + 0.1, 100)
        # EMA: alpha * new + (1-alpha) * prev = 0.7 * 0.4 + 0.3 * (0.7 * 0.8)
        expected_ema = 0.7 * 0.4 + 0.3 * (0.7 * 0.8)
        self.assertAlmostEqual(state.confidence_smooth, expected_ema, places=5)
    
    def test_remove_track(self):
        """Удаление трека."""
        track_id = 1
        attr_name = "hard_hat"
        now_ts = time.time()
        
        # Добавляем атрибут
        self.manager.update(track_id, attr_name, True, 0.8, now_ts, 100)
        self.assertIn(track_id, self.manager._attr_by_track)
        
        # Удаляем трек
        self.manager.remove_track(track_id)
        self.assertNotIn(track_id, self.manager._attr_by_track)


class TestRoiFeeder(unittest.TestCase):
    """Тесты ROI-фидера."""
    
    def setUp(self):
        """Настройка тестов."""
        self.roi_feeder = RoiFeeder()
        self.roi_feeder.params = {
            'source_ids': [0, 1],
            'padding': 0.1,
            'size': [224, 224],
            'every_n_frames': 2
        }
        self.roi_feeder.set_params_impl()
    
    def test_roi_feeder_creation(self):
        """Создание ROI-фидера."""
        self.assertEqual(self.roi_feeder.source_ids, [0, 1])
        self.assertEqual(self.roi_feeder.padding, 0.1)
        self.assertEqual(self.roi_feeder.roi_size, (224, 224))
        self.assertEqual(self.roi_feeder.every_n_frames, 2)
    
    def test_roi_feeder_interface(self):
        """Тест интерфейса ProcessorFrame."""
        # Тест put/get
        frame = Frame()
        frame.source_id = 0
        frame.frame_id = 1
        
        result = self.roi_feeder.put(frame)
        self.assertTrue(result)
        
        # Запуск обработки
        self.roi_feeder.start()
        time.sleep(0.1)  # Даём время на обработку
        
        output_frame = self.roi_feeder.get()
        if output_frame:
            self.assertEqual(output_frame.source_id, 0)
            self.assertEqual(output_frame.frame_id, 1)
        
        self.roi_feeder.stop()
    
    def test_get_source_ids(self):
        """Получение списка source_ids."""
        source_ids = self.roi_feeder.get_source_ids()
        self.assertEqual(source_ids, [0, 1])


class TestAttributeClassifier(unittest.TestCase):
    """Тесты классификатора атрибутов."""
    
    def setUp(self):
        """Настройка тестов."""
        self.classifier = AttributeClassifier()
        self.classifier.params = {
            'source_ids': [0, 1],
            'enabled': True,
            'model': 'test_model.onnx',
            'attrs': ['hard_hat', 'backpack'],
            'confidence_thresholds': {'hard_hat': 0.5, 'backpack': 0.6},
            'time_thresholds': {
                'hard_hat': {'min_time_ms': 600, 'confirm_time_ms': 2000},
                'backpack': {'min_time_ms': 800, 'confirm_time_ms': 2500}
            },
            'ema_alpha': 0.6
        }
        self.classifier.set_params_impl()
    
    def test_classifier_creation(self):
        """Создание классификатора."""
        self.assertEqual(self.classifier.source_ids, [0, 1])
        self.assertTrue(self.classifier.enabled)
        self.assertEqual(self.classifier.model_path, 'test_model.onnx')
        self.assertEqual(self.classifier.attrs, ['hard_hat', 'backpack'])
        self.assertEqual(self.classifier.conf_thresholds, {'hard_hat': 0.5, 'backpack': 0.6})
        self.assertEqual(self.classifier.ema_alpha, 0.6)
    
    def test_classifier_interface(self):
        """Тест интерфейса ProcessorFrame."""
        # Тест put/get
        frame = Frame()
        frame.source_id = 0
        frame.frame_id = 1
        
        result = self.classifier.put(frame)
        self.assertTrue(result)
        
        # Запуск обработки
        self.classifier.start()
        time.sleep(0.1)  # Даём время на обработку
        
        output_frame = self.classifier.get()
        if output_frame:
            self.assertEqual(output_frame.source_id, 0)
            self.assertEqual(output_frame.frame_id, 1)
        
        self.classifier.stop()
    
    def test_get_source_ids(self):
        """Получение списка source_ids."""
        source_ids = self.classifier.get_source_ids()
        self.assertEqual(source_ids, [0, 1])


class TestObjectsHandlerIntegration(unittest.TestCase):
    """Интеграционные тесты ObjectsHandler с атрибутами."""
    
    def setUp(self):
        """Настройка тестов."""
        self.obj_handler = ObjectsHandler(db_controller=None, db_adapter=None)
        self.obj_handler.params = {
            'attributes_detection': {
                'classifier': {
                    'confidence_thresholds': {'hard_hat': 0.5},
                    'time_thresholds': {'hard_hat': {'min_time_ms': 600, 'confirm_time_ms': 2000}},
                    'ema_alpha': 0.6
                }
            }
        }
        self.obj_handler.set_params_impl()
    
    def test_objects_handler_attributes_config(self):
        """Конфигурация атрибутов в ObjectsHandler."""
        self.assertIsNotNone(self.obj_handler.attr_manager)
        self.assertEqual(self.obj_handler._attr_conf_thresholds, {'hard_hat': 0.5})
        self.assertEqual(self.obj_handler._attr_ema_alpha, 0.6)
    
    def test_put_attributes(self):
        """Тест метода put_attributes."""
        track_id = 1
        attrs = {'hard_hat': 0.8, 'backpack': 0.6}
        
        self.obj_handler.put_attributes(track_id, attrs)
        
        self.assertEqual(self.obj_handler._attr_pending[track_id], attrs)
    
    def test_put_attributes_empty(self):
        """Тест put_attributes с пустыми данными."""
        self.obj_handler.put_attributes(None, {})
        self.obj_handler.put_attributes(1, {})
        
        # Не должно быть записей в _attr_pending
        self.assertEqual(len(self.obj_handler._attr_pending), 0)


if __name__ == '__main__':
    unittest.main()
