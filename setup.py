import os
import sys
import subprocess

def install(package):
    subprocess.check_call(['python3', "-m", "pip", "install", package])    

install("discord")
install("pymongo")
install("python-dotenv")

print("Installed dependencies!")