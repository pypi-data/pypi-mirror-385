#!/usr/bin/env python3

import sys
import os
from evileye.core.logging_config import setup_evileye_logging
from evileye.core.logger import get_module_logger
sys.path.append('.')

# Инициализация логирования для тестов
logger = setup_evileye_logging(log_level="INFO", log_to_console=True, log_to_file=True)
test_logger = get_module_logger("test")

def test_journal_mapping():
    """Test journal data mapping"""
    
    test_logger.info("=== Journal Mapping Test ===")
    
    try:
        from evileye.visualization_modules.journal_data_source_json import JsonLabelJournalDataSource
        
        ds = JsonLabelJournalDataSource('EvilEyeData')
        
        # Test raw data loading
        test_logger.info("\n1. Raw Data Loading:")
        ds._load_cache()
        test_logger.info(f"   Cache size: {len(ds._cache)}")
        
        # Check for None values in ts field
        none_ts_count = 0
        for ev in ds._cache:
            if ev.get('ts') is None:
                none_ts_count += 1
                test_logger.info(f"   Found None ts in event: {ev.get('event_id')}")
        
        test_logger.info(f"   Events with None ts: {none_ts_count}")
        
        # Test mapping with sample data
        test_logger.info("\n2. Sample Data Mapping:")
        
        # Sample found event
        found_item = {
            "object_id": 1,
            "frame_id": 95,
            "timestamp": "2025-09-01T15:14:56.790676",
            "image_filename": "detected_frames/test_found.jpeg",
            "bounding_box": {"x": 298, "y": 1, "width": 234, "height": 509},
            "source_id": 4,
            "source_name": "Cam5",
            "class_id": 0,
            "class_name": "person"
        }
        
        mapped_found = ds._map_item(found_item, 'found', '2025_09_01', 0)
        test_logger.info(f"   Found event mapping:")
        test_logger.info(f"     ts: {mapped_found.get('ts')}")
        test_logger.info(f"     event_type: {mapped_found.get('event_type')}")
        test_logger.info(f"     image_filename: {mapped_found.get('image_filename')}")
        
        # Sample lost event
        lost_item = {
            "object_id": 1,
            "frame_id": 93,
            "detected_timestamp": "2025-09-01T15:14:56.790676",
            "lost_timestamp": "2025-09-01T15:14:58.555991",
            "image_filename": "lost_frames/test_lost.jpeg",
            "bounding_box": {"x": 319, "y": 1, "width": 234, "height": 407},
            "source_id": 4,
            "source_name": "Cam5",
            "class_id": 0,
            "class_name": "person"
        }
        
        mapped_lost = ds._map_item(lost_item, 'lost', '2025_09_01', 0)
        test_logger.info(f"   Lost event mapping:")
        test_logger.info(f"     ts: {mapped_lost.get('ts')}")
        test_logger.info(f"     event_type: {mapped_lost.get('event_type')}")
        test_logger.info(f"     image_filename: {mapped_lost.get('image_filename')}")
        
        # Test sorting
        test_logger.info("\n3. Sorting Test:")
        test_items = [
            {'ts': '2025-09-01T15:24:30.977061', 'event_type': 'found'},
            {'ts': None, 'event_type': 'lost'},
            {'ts': '2025-09-01T15:24:29.807639', 'event_type': 'found'},
        ]
        
        sorted_items = ds._apply_sort(test_items, [('ts', 'desc')])
        test_logger.info(f"   Sorted items:")
        for i, item in enumerate(sorted_items):
            test_logger.info(f"     {i+1}. ts={item.get('ts')}, type={item.get('event_type')}")
        
        ds.close()
        
    except Exception as e:
        test_logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_journal_mapping()



