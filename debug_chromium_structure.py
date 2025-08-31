#!/usr/bin/env python3
"""
Debug script to examine Chromium Headless Shell file structure
This will help us understand the correct executable path
"""

import os
import subprocess

def examine_playwright_cache():
    """Examine the Playwright cache directory structure"""
    print("🔍 Examining Playwright cache structure...")
    
    playwright_cache = os.path.expanduser("~/.cache/ms-playwright")
    print(f"📁 Cache directory: {playwright_cache}")
    
    if not os.path.exists(playwright_cache):
        print("❌ Playwright cache directory does not exist!")
        return
    
    print(f"\n📂 Contents of {playwright_cache}:")
    try:
        items = os.listdir(playwright_cache)
        for item in items:
            item_path = os.path.join(playwright_cache, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
                
                # If it's a chromium directory, examine its contents
                if item.startswith('chromium'):
                    print(f"    🔍 Examining {item}:")
                    try:
                        sub_items = os.listdir(item_path)
                        for sub_item in sub_items[:10]:  # Limit to first 10 items
                            sub_path = os.path.join(item_path, sub_item)
                            if os.path.isdir(sub_path):
                                print(f"      📁 {sub_item}/")
                                
                                # Check for executable files in subdirectories
                                try:
                                    exec_items = os.listdir(sub_path)
                                    for exec_item in exec_items[:5]:  # Limit output
                                        exec_path = os.path.join(sub_path, exec_item)
                                        if os.path.isfile(exec_path):
                                            is_executable = os.access(exec_path, os.X_OK)
                                            size = os.path.getsize(exec_path)
                                            print(f"        {'🚀' if is_executable else '📄'} {exec_item} ({size:,} bytes) {'[EXECUTABLE]' if is_executable else ''}")
                                except PermissionError:
                                    print(f"        ❌ Permission denied accessing {sub_path}")
                                except Exception as e:
                                    print(f"        ❌ Error reading {sub_path}: {e}")
                            else:
                                size = os.path.getsize(sub_path)
                                is_executable = os.access(sub_path, os.X_OK)
                                print(f"      {'🚀' if is_executable else '📄'} {sub_item} ({size:,} bytes) {'[EXECUTABLE]' if is_executable else ''}")
                    except PermissionError:
                        print(f"    ❌ Permission denied accessing {item_path}")
                    except Exception as e:
                        print(f"    ❌ Error reading {item_path}: {e}")
            else:
                size = os.path.getsize(item_path)
                print(f"  📄 {item} ({size:,} bytes)")
    except PermissionError:
        print("❌ Permission denied accessing cache directory")
    except Exception as e:
        print(f"❌ Error reading cache directory: {e}")

def find_chromium_executables():
    """Find all potential Chromium executables"""
    print("\n🔍 Searching for Chromium executables...")
    
    playwright_cache = os.path.expanduser("~/.cache/ms-playwright")
    executables = []
    
    if not os.path.exists(playwright_cache):
        print("❌ Playwright cache directory does not exist!")
        return executables
    
    # Search for common executable names
    executable_names = ['headless_shell', 'chrome', 'chromium', 'chromium-browser']
    
    for root, dirs, files in os.walk(playwright_cache):
        for file in files:
            if file in executable_names:
                file_path = os.path.join(root, file)
                if os.access(file_path, os.X_OK):
                    size = os.path.getsize(file_path)
                    executables.append((file_path, size))
                    print(f"  ✅ Found: {file_path} ({size:,} bytes)")
    
    if not executables:
        print("  ❌ No Chromium executables found")
    
    return executables

def test_playwright_launch():
    """Test Playwright launch with available executables"""
    print("\n🧪 Testing Playwright launch...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        # Test 1: Standard launch
        print("  🔄 Testing standard Chromium launch...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("  ✅ Standard Chromium launch successful!")
                return True
        except Exception as e:
            print(f"  ❌ Standard launch failed: {e}")
        
        # Test 2: Find and test executables
        executables = find_chromium_executables()
        for exec_path, size in executables:
            print(f"  🔄 Testing executable: {exec_path}")
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, executable_path=exec_path)
                    browser.close()
                    print(f"  ✅ Success with: {exec_path}")
                    return True
            except Exception as e:
                print(f"  ❌ Failed with {exec_path}: {e}")
        
        return False
        
    except ImportError:
        print("  ❌ Playwright not installed")
        return False
    except Exception as e:
        print(f"  ❌ Playwright test error: {e}")
        return False

def check_system_chrome():
    """Check if system Chrome is available"""
    print("\n🌐 Checking system Chrome installation...")
    
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome'
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path) and os.access(chrome_path, os.X_OK):
            try:
                result = subprocess.run([chrome_path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"  ✅ Found: {chrome_path}")
                    print(f"     Version: {result.stdout.strip()}")
                    return chrome_path
            except Exception as e:
                print(f"  ❌ Error testing {chrome_path}: {e}")
    
    print("  ❌ No system Chrome found")
    return None

def main():
    """Main diagnostic function"""
    print("🚀 Chromium Headless Shell Diagnostic Tool")
    print("=" * 50)
    
    examine_playwright_cache()
    find_chromium_executables()
    test_playwright_launch()
    check_system_chrome()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostic complete!")
    print("\n💡 Next steps:")
    print("   1. If no executables found: run 'playwright install chromium'")
    print("   2. If executables found but launch fails: check permissions")
    print("   3. If system Chrome available: consider using that instead")

if __name__ == "__main__":
    main()
