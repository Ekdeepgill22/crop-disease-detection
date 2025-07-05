# start_mongodb.py
"""
MongoDB Startup Script
Run this to start MongoDB manually if it's not running as a service
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, shell=True, wait=False):
    """Run a command"""
    try:
        if wait:
            result = subprocess.run(command, shell=shell, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            subprocess.Popen(command, shell=shell)
            return True, "", ""
    except Exception as e:
        return False, "", str(e)

def check_mongodb_running():
    """Check if MongoDB is running"""
    try:
        # Try to connect using mongosh or mongo
        success, stdout, stderr = run_command("mongosh --eval \"db.adminCommand('ping')\"", wait=True)
        if success:
            return True
        
        # Try with legacy mongo client
        success, stdout, stderr = run_command("mongo --eval \"db.adminCommand('ping')\"", wait=True)
        return success
    except:
        return False

def start_mongodb_service():
    """Start MongoDB as a Windows service"""
    print("Starting MongoDB service...")
    success, stdout, stderr = run_command("net start MongoDB", wait=True)
    
    if success:
        print("✅ MongoDB service started successfully!")
        return True
    else:
        print(f"❌ Failed to start MongoDB service: {stderr}")
        return False

def start_mongodb_manual():
    """Start MongoDB manually"""
    print("Starting MongoDB manually...")
    
    # Common MongoDB installation paths
    possible_paths = [
        "C:/Program Files/MongoDB/Server/7.0/bin/mongod.exe",
        "C:/Program Files/MongoDB/Server/6.0/bin/mongod.exe",
        "C:/Program Files/MongoDB/Server/5.0/bin/mongod.exe",
        "C:/mongodb/bin/mongod.exe",
        "mongod"  # If in PATH
    ]
    
    mongod_path = None
    for path in possible_paths:
        if path == "mongod" or Path(path).exists():
            mongod_path = path
            break
    
    if not mongod_path:
        print("❌ MongoDB executable not found!")
        print("Please install MongoDB or add it to your PATH")
        return False
    
    # Create data directory if it doesn't exist
    data_dir = Path("C:/data/db")
    if not data_dir.exists():
        print(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # Start MongoDB
    command = f'"{mongod_path}" --dbpath "C:/data/db"'
    print(f"Running: {command}")
    
    success, stdout, stderr = run_command(command, wait=False)
    
    if success:
        print("✅ MongoDB started manually!")
        print("MongoDB is running on port 27017")
        print("Data directory: C:/data/db")
        print("\n⚠️  Keep this terminal window open to keep MongoDB running")
        return True
    else:
        print(f"❌ Failed to start MongoDB: {stderr}")
        return False

def main():
    """Main function"""
    print("MongoDB Startup Script for KhetAI")
    print("=" * 40)
    
    # Check if MongoDB is already running
    if check_mongodb_running():
        print("✅ MongoDB is already running!")
        return
    
    print("MongoDB is not running. Attempting to start...")
    
    # Try to start as service first
    if start_mongodb_service():
        time.sleep(2)
        if check_mongodb_running():
            print("✅ MongoDB service is now running!")
            return
    
    # If service start failed, try manual start
    print("\nService start failed. Trying manual start...")
    if start_mongodb_manual():
        time.sleep(3)
        if check_mongodb_running():
            print("✅ MongoDB is now running manually!")
            print("\nYou can now:")
            print("1. Restart your backend server: python run.py")
            print("2. Test the health endpoint: http://localhost:8000/health")
            print("3. Try the crop analysis again!")
        else:
            print("❌ MongoDB started but connection test failed")
    else:
        print("❌ Failed to start MongoDB")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is installed")
        print("2. Check if port 27017 is available")
        print("3. Run as administrator if needed")
        print("4. Check Windows services for MongoDB")

if __name__ == "__main__":
    main()