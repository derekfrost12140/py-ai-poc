#!/usr/bin/env python3
"""
Test script for MCP Agent Orchestration System
Tests individual components without requiring API keys
"""

import json
import sqlite3
from pathlib import Path

def test_manifest_loading():
    """Test loading the tool manifest"""
    print("🧪 Testing manifest loading...")
    try:
        with open('app/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        tools = manifest.get('tools', [])
        print(f"✅ Manifest loaded successfully with {len(tools)} tools:")
        
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        return True
    except Exception as e:
        print(f"❌ Manifest loading failed: {e}")
        return False

def test_database():
    """Test database connectivity and queries"""
    print("\n🧪 Testing database...")
    try:
        conn = sqlite3.connect('db/test.db')
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        print(f"✅ Database connected. Found {count} users")
        
        # Test user listing
        cursor.execute('SELECT name, email FROM users LIMIT 3')
        users = cursor.fetchall()
        print("✅ Sample users:")
        for user in users:
            print(f"  - {user[0]} ({user[1]})")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_tool_executor():
    """Test tool executor (without API calls)"""
    print("\n🧪 Testing tool executor...")
    try:
        # Import and test basic functionality
        import sys
        sys.path.append('.')
        
        from app.tools import ToolExecutor
        
        executor = ToolExecutor()
        print("✅ ToolExecutor initialized successfully")
        
        # Test SQL tool (should work without API keys)
        result = executor.sql_tool("SELECT COUNT(*) FROM users")
        print(f"✅ SQL tool test: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Tool executor test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app structure"""
    print("\n🧪 Testing FastAPI app...")
    try:
        import sys
        sys.path.append('.')
        
        from app.main import app
        
        # Check if app has required endpoints
        routes = [route.path for route in app.routes]
        required_routes = ['/', '/health', '/query', '/tools']
        
        print("✅ FastAPI app loaded successfully")
        print(f"✅ Available routes: {routes}")
        
        missing_routes = [route for route in required_routes if route not in routes]
        if missing_routes:
            print(f"⚠️  Missing routes: {missing_routes}")
        else:
            print("✅ All required routes present")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/agent.py',
        'app/tools.py',
        'app/manifest.json',
        'db/__init__.py',
        'db/init_db.py',
        'db/test.db',
        'requirements.txt',
        'README.md',
        'frontend.html',
        'start.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🤖 MCP Agent System - Component Tests")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_manifest_loading,
        test_database,
        test_tool_executor,
        test_fastapi_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The system is ready to run.")
        print("\nNext steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python3 start.py")
        print("3. Open frontend.html in your browser")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 