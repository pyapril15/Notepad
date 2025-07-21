#!/usr/bin/env python3
"""
Debug Test Script for Modern Notepad
This will help identify exactly where the "expected integer but got ''" error occurs

Run this before running the main application: python debug_test.py
"""

import os
import sys
import tkinter as tk

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_basic_tkinter():
    """Test basic tkinter functionality"""
    print("Testing basic tkinter...")
    try:
        root = tk.Tk()
        root.withdraw()

        # Test IntVar with different values
        int_var = tk.IntVar()
        int_var.set(12)  # Should work
        print(f"✅ IntVar with integer: {int_var.get()}")

        # This should cause the error if we pass empty string
        try:
            int_var.set("")  # This might cause the error
            print(f"❌ IntVar with empty string: '{int_var.get()}'")
        except tk.TclError as e:
            print(f"❌ Error with empty string: {e}")

        try:
            int_var.set(None)  # This might cause the error
            print(f"❌ IntVar with None: {int_var.get()}")
        except (tk.TclError, TypeError) as e:
            print(f"❌ Error with None: {e}")

        root.destroy()
        print("✅ Basic tkinter test passed")

    except Exception as e:
        print(f"❌ Basic tkinter test failed: {e}")
        return False

    return True


def test_config_loader():
    """Test configuration loader"""
    print("\nTesting configuration loader...")
    try:
        from utils.config_loader import ConfigLoader
        config = ConfigLoader()

        # Test getting values
        font_size = config.get('font_size', 12)
        print(f"Font size: {font_size} (type: {type(font_size)})")

        autosave_interval = config.get('autosave_interval', 300)
        print(f"Autosave interval: {autosave_interval} (type: {type(autosave_interval)})")

        # Test problematic cases
        empty_value = config.get('nonexistent_key', "")
        print(f"Empty value: '{empty_value}' (type: {type(empty_value)})")

        print("✅ Configuration loader test passed")
        return True

    except Exception as e:
        print(f"❌ Configuration loader test failed: {e}")
        return False


def test_settings_window_creation():
    """Test settings window creation"""
    print("\nTesting settings window creation...")
    try:
        # Create a minimal version to test
        root = tk.Tk()
        root.withdraw()

        # Test creating IntVar variables like in settings window
        auto_save_interval_var = tk.IntVar()
        font_size_var = tk.IntVar()
        max_recent_var = tk.IntVar()
        tab_size_var = tk.IntVar()

        # Test setting values
        auto_save_interval_var.set(300)
        font_size_var.set(12)
        max_recent_var.set(10)
        tab_size_var.set(4)

        print("✅ IntVar creation and setting passed")

        # Test with empty string (this might cause the error)
        try:
            test_var = tk.IntVar()
            test_var.set("")  # This is likely causing the error
            print(f"❌ This shouldn't work: {test_var.get()}")
        except tk.TclError as e:
            print(f"❌ Expected error with empty string: {e}")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Settings window test failed: {e}")
        return False


def test_editor_window_minimal():
    """Test minimal editor window creation"""
    print("\nTesting minimal editor window...")
    try:
        from utils.config_loader import ConfigLoader

        config = ConfigLoader()

        # Test the exact values that might be causing issues
        font_size = config.get('font_size', 12)
        print(f"Font size from config: {font_size} (type: {type(font_size)})")

        if font_size == "":
            print("❌ Found empty string font_size!")
            return False

        autosave_interval = config.get('autosave_interval', 300)
        print(f"Autosave interval from config: {autosave_interval} (type: {type(autosave_interval)})")

        if autosave_interval == "":
            print("❌ Found empty string autosave_interval!")
            return False

        print("✅ Editor window values test passed")
        return True

    except Exception as e:
        print(f"❌ Editor window test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Modern Notepad Debug Test")
    print("=" * 50)

    tests = [
        test_basic_tkinter,
        test_config_loader,
        test_settings_window_creation,
        test_editor_window_minimal
    ]

    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! The application should work.")
        print("🚀 Try running: python main.py")
    else:
        print("❌ Some tests failed. Check the output above.")
        print("💡 Try running: python fix_config.py")

    print("\nPress Enter to continue...")
    input()


if __name__ == "__main__":
    main()
