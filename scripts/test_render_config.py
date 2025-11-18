#!/usr/bin/env python
"""
Render Configuration Validator
"""

import os
import sys
import subprocess
from pathlib import Path

# Try to import yaml with fallback
try:
    import yaml
except ImportError:
    print("ℹ️  pyyaml not installed. Skipping YAML validation.")
    yaml = None

BASE_DIR = Path(__file__).resolve().parent

def validate_render_yaml():
    """Validate render.yaml structure"""
    print("🔍 Validating render.yaml...")
    
    yaml_path = BASE_DIR / 'render.yaml'
    if not yaml_path.exists():
        print("❌ render.yaml not found!")
        return False
    
    # Skip deep validation if yaml not installed
    if not yaml:
        print("✅ render.yaml exists (pyyaml not installed for deep validation)")
        return True
    
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate required fields at root level
    if 'services' not in config:
        print("❌ Missing top-level 'services' field")
        return False
        
    services = config['services']
    if not isinstance(services, list) or len(services) == 0:
        print("❌ 'services' must be a non-empty list")
        return False
    
    # Validate required fields in first service
    required = ['type', 'name', 'env', 'buildCommand', 'startCommand']
    first_service = services[0]
    for field in required:
        if field not in first_service:
            print(f"❌ Missing field in service: {field}")
            return False
    
    print("✅ render.yaml structure is valid")
    return True

def test_build_script():
    """Test build.sh execution"""
    print("\n🧪 Testing build.sh...")
    
    build_path = BASE_DIR / 'build.sh'
    if not build_path.exists():
        print("❌ build.sh not found!")
        return False
    
    try:
        # Use PowerShell on Windows
        shell = sys.platform.startswith('win')
        command = [str(build_path)] if not shell else ['powershell', '-Command', f'& "{build_path}"']
        
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            shell=shell
        )
        
        if result.returncode != 0:
            print(f"❌ Build failed with exit code {result.returncode}")
            print(f"Error output:\n{result.stderr}")
            return False
        
        print(result.stdout)
        
        # Verify static files were collected
        static_media = BASE_DIR / 'staticfiles' / 'media'
        if not static_media.exists():
            print("❌ staticfiles/media not created!")
            return False
            
        print(f"✅ Found {len(list(static_media.glob('**/*')))} files in staticfiles/media")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🚀 Render Configuration Validator")
    print("="*50)
    
    yaml_valid = validate_render_yaml()
    build_valid = test_build_script()
    
    print("\n📊 Validation Results:")
    print(f"- render.yaml: {'✅' if yaml_valid else '❌'}")
    print(f"- build.sh: {'✅' if build_valid else '❌'}")
    
    if yaml_valid and build_valid:
        print("\n🎉 Configuration is ready for Render deployment!")
    else:
        print("\n❌ Issues found. Please fix before deploying.")

if __name__ == "__main__":
    main()