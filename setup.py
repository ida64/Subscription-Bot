import os
import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("discord")
install("pymongo")
install("python-dotenv")

print("Installed dependencies!")