"""
Setup Script for Travel News System
Run this to create the project structure
"""

import os
from pathlib import Path

def create_project_structure():
    """Create all necessary folders and files"""
    
    # Define structure
    folders = [
        'config',
        'core',
        'data/raw',
        'data/processed',
        'data/archive',
        'translations',
        'logs',
        'utils',
        'ui',
    ]
    
    print("Creating project structure...")
    print("="*60)
    
    # Create folders
    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {folder}/")
        
        # Create __init__.py for Python packages
        if folder in ['config', 'core', 'utils', 'ui']:
            init_file = path / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                print(f"  └─ Created: {folder}/__init__.py")
    
    print("\n" + "="*60)
    print("✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Copy the provided Python files into their respective folders:")
    print("   - config/settings.py")
    print("   - utils/logger.py")
    print("   - core/scraper.py")
    print("   - core/scheduler.py")
    print("   - app.py (in root)")
    print("   - requirements.txt (in root)")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Run the application:")
    print("   streamlit run app.py")
    print("\n" + "="*60)


if __name__ == "__main__":
    create_project_structure()