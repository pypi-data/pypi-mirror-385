#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def build_frontend():
    frontend_dir = Path(__file__).parent.parent / "thinagents" / "frontend"
    build_output = Path(__file__).parent.parent / "thinagents" / "web" / "ui" / "build"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        sys.exit(1)
    
    print("🔨 Building ThinAgents Web UI...")
    
    try:
        print("📦 Installing dependencies...")
        result = subprocess.run(
            ["pnpm", "install"],
            cwd=frontend_dir,
            check=True,
            capture_output=False,
        )
        
        print("🏗️  Building frontend...")
        result = subprocess.run(
            ["pnpm", "run", "build"],
            cwd=frontend_dir,
            check=True,
            capture_output=False,
        )
        
        if build_output.exists():
            print(f"✅ Build successful: {build_output}")
            file_count = sum(1 for _ in build_output.rglob('*') if _.is_file())
            print(f"📁 Generated {file_count} files")
        else:
            print("⚠️  Build directory not found at expected location")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 'pnpm' not found. Install: npm install -g pnpm")
        sys.exit(1)


if __name__ == "__main__":
    build_frontend()

