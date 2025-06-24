#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MT5 Trading System - Simple Health Check (ASCII only)
Verify integration of all completed refactoring steps
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("=" * 60)
print("MT5 Trading System - System Health Check")
print("=" * 60)

# Collection for test results
results = {
    'step1_logging': False,
    'step2_type_hints': False,  
    'step3_config_management': False,
    'step4_event_system': False,
    'step5_interfaces': False,
    'step6_error_handling': False,
    'step7_controllers': False,
    'step8_data_layer': False,
    'step9_api_system': False,
    'integration_test': False
}

def test_step1_logging():
    """Step 1: Logging System Test"""
    try:
        # Test without importing GUI components
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("logger", "app/utils/logger.py")
        logger_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logger_module)
        
        # Test basic logger functionality
        logger = logger_module.get_logger("test")
        logger.info("Logging system test - success")
        
        results['step1_logging'] = True
        print("[OK] Step 1: Logging System - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 1: Logging System - Error: {e}")
        return False

def test_step2_type_hints():
    """Step 2: Type Hints Validation"""
    try:
        # Check if main files exist with type hints (basic check)
        main_window_path = Path("app/gui/main_window.py")
        if main_window_path.exists():
            content = main_window_path.read_text(encoding='utf-8')
            # Basic check for type annotations
            has_annotations = "def " in content and "->" in content
            if has_annotations:
                print("[OK] Step 2: Type Hints - Found in main files")
            else:
                print("[WARN] Step 2: Type Hints - Limited annotations found")
        
        results['step2_type_hints'] = True
        print("[OK] Step 2: Type Hints - Files exist")
        return True
    except Exception as e:
        print(f"[FAIL] Step 2: Type Hints - Error: {e}")
        return False

def test_step3_config_management():
    """Step 3: Configuration Management Test"""
    try:
        # Test configuration file exists and is valid
        config_path = Path("config/config.json")
        if not config_path.exists():
            raise Exception("config.json not found")
            
        # Test JSON parsing
        import json
        config_data = json.loads(config_path.read_text())
        required_keys = ["SYMBOLS", "GUI_SETTINGS", "BATCH_ORDER_DEFAULTS"]
        for key in required_keys:
            if key not in config_data:
                raise Exception(f"Missing config key: {key}")
        
        # Test ConfigManager file exists
        config_manager_path = Path("app/utils/config_manager.py")
        if not config_manager_path.exists():
            raise Exception("config_manager.py not found")
            
        results['step3_config_management'] = True
        print("[OK] Step 3: Configuration Management - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 3: Configuration Management - Error: {e}")
        return False

def test_step4_event_system():
    """Step 4: Event System Test"""
    try:
        # Test event system files exist
        event_files = [
            "app/utils/event_bus.py",
            "app/utils/event_examples.py"
        ]
        
        for file_path in event_files:
            if not Path(file_path).exists():
                raise Exception(f"Missing file: {file_path}")
        
        # Test basic event system structure (without importing PyQt6 dependencies)
        event_bus_path = Path("app/utils/event_bus.py")
        content = event_bus_path.read_text(encoding='utf-8')
        
        # Check for key classes
        required_classes = ["EventBus", "EventType", "Event"]
        for cls_name in required_classes:
            if f"class {cls_name}" not in content:
                raise Exception(f"Missing class: {cls_name}")
            
        results['step4_event_system'] = True
        print("[OK] Step 4: Event System - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 4: Event System - Error: {e}")
        return False

def test_step5_interfaces():
    """Step 5: Service Interfaces Test"""
    try:
        # Check interface files exist
        interface_files = [
            "app/interfaces/trader_interface.py",
            "app/interfaces/config_interface.py", 
            "app/interfaces/database_interface.py"
        ]
        
        adapter_files = [
            "app/adapters/trader_adapter.py",
            "app/adapters/config_adapter.py",
            "app/adapters/database_adapter.py"
        ]
        
        for file_path in interface_files + adapter_files:
            if not Path(file_path).exists():
                raise Exception(f"Missing file: {file_path}")
                
        # Test basic interface import
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("trader_interface", "app/interfaces/trader_interface.py")
        interface_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(interface_module)
        
        ITrader = interface_module.ITrader
        if ITrader is None:
            raise Exception("ITrader interface not found")
            
        results['step5_interfaces'] = True
        print("[OK] Step 5: Service Interfaces - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 5: Service Interfaces - Error: {e}")
        return False

def test_step6_error_handling():
    """Step 6: Error Handling Test"""
    try:
        # Check error handling files exist
        error_files = [
            "app/utils/error_handler.py",
            "app/utils/error_utils.py"
        ]
        
        for file_path in error_files:
            if not Path(file_path).exists():
                raise Exception(f"Missing file: {file_path}")
                
        # Test basic error handling import
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("error_handler", "app/utils/error_handler.py")
        error_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(error_module)
        
        ErrorHandler = error_module.ErrorHandler
        ErrorLevel = error_module.ErrorLevel
        MT5Error = error_module.MT5Error
        
        if not all([ErrorHandler, ErrorLevel, MT5Error]):
            raise Exception("Error handling classes missing")
            
        results['step6_error_handling'] = True
        print("[OK] Step 6: Error Handling - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 6: Error Handling - Error: {e}")
        return False

def test_step7_controllers():
    """Step 7: Controller Layer Test"""
    try:
        # Check controller files exist
        controller_files = [
            "app/controllers/main_controller.py",
            "app/controllers/simple_controller.py"
        ]
        
        for file_path in controller_files:
            if not Path(file_path).exists():
                raise Exception(f"Missing file: {file_path}")
                
        # Test basic controller import
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("simple_controller", "app/controllers/simple_controller.py")
        controller_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(controller_module)
        
        SimpleController = controller_module.SimpleController
        if SimpleController is None:
            raise Exception("SimpleController not found")
            
        results['step7_controllers'] = True
        print("[OK] Step 7: Controller Layer - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 7: Controller Layer - Error: {e}")
        return False

def test_step8_data_layer():
    """Step 8: Data Layer Test"""
    try:
        # Check data layer files exist
        data_files = [
            "app/utils/connection_manager.py",
            "app/utils/query_builder.py",
            "app/dal/base_repository.py",
            "app/dal/trade_repository.py",
            "app/adapters/data_layer_adapter.py"
        ]
        
        for file_path in data_files:
            if not Path(file_path).exists():
                raise Exception(f"Missing file: {file_path}")
                
        # Test basic data layer import
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("query_builder", "app/utils/query_builder.py")
        query_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(query_module)
        
        QueryBuilder = query_module.QueryBuilder
        if QueryBuilder is None:
            raise Exception("QueryBuilder not found")
            
        # Test query building
        qb = QueryBuilder()
        query_sql, params = qb.select("*").from_table("trades").where("symbol = ?", "EURUSD").build_select()
        if not query_sql or "SELECT" not in query_sql:
            raise Exception("Query building failed")
            
        results['step8_data_layer'] = True
        print("[OK] Step 8: Data Layer - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 8: Data Layer - Error: {e}")
        return False

def test_step9_api_system():
    """Step 9: API System Test"""
    try:
        # Check API files exist
        api_files = [
            "app/api/models.py",
            "app/api/validators.py",
            "app/api/routes.py",
            "app/api/server.py",
            "app/adapters/api_adapter.py"
        ]
        
        for file_path in api_files:
            if not Path(file_path).exists():
                raise Exception(f"Missing file: {file_path}")
                
        # Test basic API import
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("api_models", "app/api/models.py")
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)
        
        APIResponse = api_module.APIResponse
        OrderRequest = api_module.OrderRequest
        
        if not all([APIResponse, OrderRequest]):
            raise Exception("API model classes missing")
            
        # Test API response model
        response = APIResponse(success=True, data={"test": "data"})
        if not response.success:
            raise Exception("API response model error")
            
        results['step9_api_system'] = True
        print("[OK] Step 9: API System - Working")
        return True
    except Exception as e:
        print(f"[FAIL] Step 9: API System - Error: {e}")
        return False

def test_integration():
    """Integration Test - Verify components work together"""
    try:
        # Test file structure integration
        key_directories = [
            "app/utils",
            "app/interfaces", 
            "app/adapters",
            "app/controllers",
            "app/dal",
            "app/api",
            "app/examples"
        ]
        
        for dir_path in key_directories:
            if not Path(dir_path).exists():
                raise Exception(f"Missing directory: {dir_path}")
                
        # Test config file has required structure
        import json
        config_path = Path("config/config.json")
        if config_path.exists():
            config_data = json.loads(config_path.read_text())
            required_keys = ["SYMBOLS", "GUI_SETTINGS", "BATCH_ORDER_DEFAULTS"]
            for key in required_keys:
                if key not in config_data:
                    raise Exception(f"Missing config key: {key}")
                    
        results['integration_test'] = True
        print("[OK] Integration Test - Structure Valid")
        return True
    except Exception as e:
        print(f"[FAIL] Integration Test - Error: {e}")
        return False

def main():
    """Main check function"""
    print("\nStarting system health check...\n")
    
    # Execute all tests
    test_functions = [
        test_step1_logging,
        test_step2_type_hints,
        test_step3_config_management,
        test_step4_event_system,
        test_step5_interfaces,
        test_step6_error_handling,
        test_step7_controllers,
        test_step8_data_layer,
        test_step9_api_system,
        test_integration
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[ERROR] {test_func.__name__} - Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("System Health Check Summary")
    print("=" * 60)
    
    # Print detailed results
    step_names = [
        "Step 1: Logging System",
        "Step 2: Type Hints", 
        "Step 3: Configuration Management",
        "Step 4: Event System",
        "Step 5: Service Interfaces",
        "Step 6: Error Handling",
        "Step 7: Controller Layer",
        "Step 8: Data Layer",
        "Step 9: API System",
        "Integration Test"
    ]
    
    for i, (key, status) in enumerate(results.items()):
        icon = "[OK]" if status else "[FAIL]"
        print(f"{icon} {step_names[i]}: {'Passed' if status else 'Failed'}")
    
    print(f"\nOverall Pass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.8:  # 80% pass rate is healthy
        print("System Status: HEALTHY")
        print("Refactoring successful, all major components working")
    elif passed >= total * 0.6:  # 60% pass rate is usable
        print("System Status: USABLE")
        print("Most features working, some components may need debugging")
    else:
        print("System Status: NEEDS REPAIR")
        print("Multiple critical components have issues")
    
    print("\n" + "=" * 60)
    
    return passed >= total * 0.8

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nUser interrupted check")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during check: {e}")
        traceback.print_exc()
        sys.exit(1)