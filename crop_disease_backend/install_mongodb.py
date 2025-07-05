# install_mongodb.py
"""
MongoDB Installation and Setup Script for Windows
Run this script to install MongoDB Community Edition
"""

import subprocess
import sys
import os
import requests
import zipfile
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_mongodb_installed():
    """Check if MongoDB is already installed"""
    success, stdout, stderr = run_command("mongod --version")
    return success

def install_mongodb_windows():
    """Install MongoDB on Windows"""
    print("Installing MongoDB Community Edition for Windows...")
    
    # Download MongoDB Community Edition
    mongodb_url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.4.zip"
    download_path = "mongodb.zip"
    
    print("Downloading MongoDB...")
    try:
        response = requests.get(mongodb_url, stream=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download completed!")
    except Exception as e:
        print(f"Download failed: {e}")
        return False
    
    # Extract MongoDB
    print("Extracting MongoDB...")
    try:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Find the extracted folder
        extracted_folder = None
        for item in os.listdir("."):
            if item.startswith("mongodb-windows") and os.path.isdir(item):
                extracted_folder = item
                break
        
        if extracted_folder:
            # Move to C:\mongodb
            mongodb_path = Path("C:/mongodb")
            if not mongodb_path.exists():
                os.makedirs(mongodb_path)
            
            # Copy files
            import shutil
            shutil.copytree(extracted_folder, mongodb_path, dirs_exist_ok=True)
            
            # Create data directory
            data_path = Path("C:/data/db")
            if not data_path.exists():
                os.makedirs(data_path)
            
            print("MongoDB installed successfully!")
            print("MongoDB installed at: C:/mongodb")
            print("Data directory created at: C:/data/db")
            
            # Clean up
            os.remove(download_path)
            shutil.rmtree(extracted_folder)
            
            return True
        else:
            print("Failed to find extracted MongoDB folder")
            return False
            
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def setup_mongodb_service():
    """Setup MongoDB as a Windows service"""
    print("Setting up MongoDB service...")
    
    # Create MongoDB config file
    config_content = """
systemLog:
    destination: file
    path: C:\\data\\log\\mongod.log
storage:
    dbPath: C:\\data\\db
net:
    port: 27017
    bindIp: 127.0.0.1
"""
    
    config_path = Path("C:/mongodb/mongod.cfg")
    log_path = Path("C:/data/log")
    
    try:
        # Create log directory
        if not log_path.exists():
            os.makedirs(log_path)
        
        # Write config file
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Install MongoDB service
        service_command = f'C:\\mongodb\\bin\\mongod.exe --config "C:\\mongodb\\mongod.cfg" --install'
        success, stdout, stderr = run_command(service_command)
        
        if success:
            print("MongoDB service installed successfully!")
            
            # Start the service
            start_command = "net start MongoDB"
            success, stdout, stderr = run_command(start_command)
            
            if success:
                print("MongoDB service started successfully!")
                return True
            else:
                print(f"Failed to start MongoDB service: {stderr}")
                return False
        else:
            print(f"Failed to install MongoDB service: {stderr}")
            return False
            
    except Exception as e:
        print(f"Service setup failed: {e}")
        return False

def install_with_chocolatey():
    """Install MongoDB using Chocolatey (if available)"""
    print("Trying to install MongoDB using Chocolatey...")
    
    # Check if chocolatey is installed
    success, stdout, stderr = run_command("choco --version")
    if not success:
        print("Chocolatey not found. Please install Chocolatey first or use manual installation.")
        return False
    
    # Install MongoDB
    success, stdout, stderr = run_command("choco install mongodb -y")
    if success:
        print("MongoDB installed successfully using Chocolatey!")
        return True
    else:
        print(f"Chocolatey installation failed: {stderr}")
        return False

def main():
    """Main installation function"""
    print("MongoDB Installation Script for KhetAI")
    print("=" * 50)
    
    # Check if MongoDB is already installed
    if check_mongodb_installed():
        print("MongoDB is already installed!")
        return
    
    print("MongoDB not found. Starting installation...")
    
    # Try different installation methods
    methods = [
        ("Chocolatey", install_with_chocolatey),
        ("Manual Installation", install_mongodb_windows)
    ]
    
    for method_name, method_func in methods:
        print(f"\nTrying {method_name}...")
        try:
            if method_func():
                print(f"✅ MongoDB installed successfully using {method_name}!")
                break
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
            continue
    else:
        print("\n❌ All installation methods failed.")
        print("\nManual Installation Instructions:")
        print("1. Download MongoDB Community Edition from: https://www.mongodb.com/try/download/community")
        print("2. Run the installer and follow the setup wizard")
        print("3. Make sure to install MongoDB as a service")
        print("4. Restart your computer after installation")
        return
    
    # Verify installation
    if check_mongodb_installed():
        print("\n✅ MongoDB installation verified!")
        print("\nNext steps:")
        print("1. Restart your backend server: python run.py")
        print("2. Test the health endpoint: http://localhost:8000/health")
        print("3. Try the crop analysis again!")
    else:
        print("\n❌ MongoDB installation could not be verified.")
        print("Please restart your computer and try again.")

if __name__ == "__main__":
    main()