# Installation Guide - Quantum Docker Engine

This guide provides detailed installation instructions for the Quantum Docker Engine across different platforms and development environments.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Docker**: Docker Desktop or Docker Engine
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **Python**: 3.9 or 3.10
- **RAM**: 16 GB for better quantum simulation performance
- **CPU**: Multi-core processor for parallel quantum operations
- **Storage**: 10 GB for development environment

## Linux Installation

### Ubuntu/Debian

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install Python 3.9 and pip
sudo apt install python3.9 python3.9-pip python3.9-venv -y

# Install Docker
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Logout and login again for Docker group changes
```

### CentOS/RHEL/Fedora

```bash
# Install Python 3.9
sudo dnf install python39 python39-pip -y

# Install Docker
sudo dnf install docker docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S python python-pip docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

## macOS Installation

### Using Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.9+
brew install python@3.9

# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop from Applications folder
```

### Using MacPorts

```bash
# Install Python
sudo port install python39 py39-pip

# Download Docker Desktop from docker.com
# Install manually from the .dmg file
```

## Windows Installation

### Using Chocolatey

```powershell
# Install Chocolatey (run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Python
choco install python3

# Install Docker Desktop
choco install docker-desktop

# Restart your computer
```

### Manual Installation

1. **Download Python**: Get Python 3.9+ from [python.org](https://python.org)
2. **Download Docker Desktop**: Get from [docker.com](https://docker.com)
3. **Install both applications** following their setup wizards
4. **Enable WSL2** for better Docker performance:
   ```powershell
   wsl --install
   ```

## Development Environment Setup

### VS Code Setup (Recommended)

1. **Install VS Code**: Download from [code.visualstudio.com](https://code.visualstudio.com)

2. **Install recommended extensions**:
   ```bash
   code --install-extension ms-python.python
   code --install-extension ms-azuretools.vscode-docker
   code --install-extension redhat.vscode-yaml
   code --install-extension ms-vscode.vscode-json
   ```

3. **Configure Python interpreter**: Open VS Code and select Python 3.9+ as interpreter

### PyCharm Setup

1. **Install PyCharm**: Download Community or Professional edition
2. **Configure Python interpreter**: Set to Python 3.9+
3. **Install Docker plugin**: Available in plugin marketplace

## Quantum Docker Engine Installation

### Quick Install (All Platforms)

```bash
# Clone the repository
git clone https://github.com/your-username/QuantumDockerEngine.git
cd QuantumDockerEngine

# Create virtual environment
python3 -m venv quantum_docker_env

# Activate virtual environment
# On Linux/macOS:
source quantum_docker_env/bin/activate
# On Windows:
quantum_docker_env\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Quantum Docker Engine
pip install -e .

# Verify installation
qdocker --help
```

### Optional extras (Qiskit)

If you need Qiskit features, install the optional extra:

```bash
pip install "quantum-docker-engine[qiskit]"
# or with pipx for CLI users
pipx install "quantum-docker-engine[qiskit]"
```

### Development Install

```bash
# Additional development dependencies
pip install -r requirements-dev.txt

# Install with development extras
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Docker-based Installation

If you prefer to run everything in containers:

```bash
# Build the Quantum Docker Engine image
docker build -t quantum-docker-engine .

# Run with volume mounting
docker run -it -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace \
  quantum-docker-engine
```

## Quantum Computing Dependencies

### Cirq Installation Verification

```python
# Test Cirq installation
python -c "import cirq; print(f'Cirq version: {cirq.__version__}')"
```

### Qiskit Installation Verification

```python
# Test Qiskit installation
python -c "import qiskit; print(f'Qiskit version: {qiskit.__version__}')"
```

### Quantum Simulator Test

```bash
# Run quantum simulator test
python -c "
import cirq
import numpy as np

# Create a simple quantum circuit
q = cirq.LineQubit(0)
circuit = cirq.Circuit(cirq.H(q), cirq.measure(q, key='result'))

# Run simulation
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=100)
print(f'Quantum simulator working! Results: {result.measurements}')
"
```

## Docker Configuration

### Verify Docker Installation

```bash
# Check Docker version
docker --version
docker-compose --version

# Test Docker functionality
docker run hello-world

# Check Docker daemon status
docker info
```

### Docker Memory Configuration

For optimal quantum simulations, increase Docker memory:

1. **Docker Desktop**: Settings → Resources → Memory → Set to 8GB+
2. **Linux**: Modify `/etc/docker/daemon.json`:
   ```json
   {
     "default-runtime": "runc",
     "runtimes": {
       "runc": {
         "path": "runc"
       }
     },
     "storage-driver": "overlay2",
     "storage-opts": [
       "overlay2.override_kernel_check=true"
     ],
     "log-driver": "json-file",
     "log-opts": {
       "max-size": "10m",
       "max-file": "3"
     },
     "default-ulimits": {
       "memlock": {
         "Hard": -1,
         "Name": "memlock",
         "Soft": -1
       }
     }
   }
   ```

## Post-Installation Setup

### Create Configuration Directory

```bash
# Create config directory
mkdir -p ~/.quantum_docker
```

### Configure Default Settings

Create `~/.quantum_docker/config.yaml`:

```yaml
quantum_docker_config:
  num_qubits: 16
  simulation_backend: cirq
  max_containers: 50
  enable_quantum_networking: true
  enable_quantum_scheduling: true
  enable_quantum_load_balancing: true
  decoherence_time_ms: 1000.0

logging:
  level: INFO
  file: ~/.quantum_docker/quantum_docker.log

docker:
  socket_path: /var/run/docker.sock
  api_version: auto
```

### Environment Variables

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
# Quantum Docker Engine settings
export QUANTUM_DOCKER_CONFIG_DIR="$HOME/.quantum_docker"
export QUANTUM_DOCKER_LOG_LEVEL="INFO"
export QUANTUM_DOCKER_BACKEND="cirq"

# Add qdocker to PATH if needed
export PATH="$PATH:$HOME/.local/bin"
```

## Installation Verification

### Quick Verification Script

Create and run `verify_install.py`:

```python
#!/usr/bin/env python3
"""
Quantum Docker Engine Installation Verification Script
"""

import sys
import subprocess
import importlib

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f" Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f" Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_module(module_name):
    """Check if a Python module is available"""
    try:
        importlib.import_module(module_name)
        print(f" {module_name} - OK")
        return True
    except ImportError:
        print(f" {module_name} - Missing")
        return False

def check_docker():
    """Check Docker installation"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f" Docker - {result.stdout.strip()}")
            return True
        else:
            print(" Docker - Not working")
            return False
    except FileNotFoundError:
        print(" Docker - Not installed")
        return False

def check_qdocker():
    """Check qdocker command"""
    try:
        result = subprocess.run(['qdocker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f" qdocker command - OK")
            return True
        else:
            print(" qdocker command - Not working")
            return False
    except FileNotFoundError:
        print(" qdocker command - Not found")
        return False

def main():
    """Main verification function"""
    print(" Quantum Docker Engine Installation Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Docker", check_docker),
        ("Cirq", lambda: check_module('cirq')),
        ("Qiskit", lambda: check_module('qiskit')),
        ("NumPy", lambda: check_module('numpy')),
        ("Click", lambda: check_module('click')),
        ("Rich", lambda: check_module('rich')),
        ("YAML", lambda: check_module('yaml')),
        ("qdocker Command", check_qdocker),
    ]
    
    results = []
    for name, check_func in checks:
        results.append((name, check_func()))
    
    print("\n Verification Summary:")
    print("-" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"{name:20} {status}")
    
    print(f"\nScore: {passed}/{total}")
    
    if passed == total:
        print("\n All checks passed! Quantum Docker Engine is ready to use.")
        print("Run 'qdocker start' to begin your quantum journey!")
    else:
        print(f"\n  {total - passed} checks failed. Please resolve issues before proceeding.")
        
        if not any(result for name, result in results if "qdocker" in name):
            print("\n Try running: pip install -e . ")
        
        if not any(result for name, result in results if "Docker" in name):
            print("\n Make sure Docker is installed and running")

if __name__ == "__main__":
    main()
```

Run the verification:

```bash
python verify_install.py
```

### Manual Verification Steps

1. **Test basic functionality**:
   ```bash
   qdocker --help
   ```

2. **Start the engine**:
   ```bash
   qdocker start
   ```

3. **Create a test container**:
   ```bash
   qdocker create nginx:alpine test-container
   ```

4. **Check status**:
   ```bash
   qdocker status
   ```

5. **Stop the engine**:
   ```bash
   qdocker stop
   ```

## Updating

### Update Quantum Docker Engine

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinstall package
pip install -e . --force-reinstall
```

### Update Quantum Computing Dependencies

```bash
# Update Cirq
pip install cirq --upgrade

# Update Qiskit  
pip install qiskit --upgrade

# Update all quantum dependencies
pip install -r requirements.txt --upgrade
```

## Uninstallation

### Remove Quantum Docker Engine

```bash
# Uninstall package
pip uninstall quantum-docker-engine

# Remove configuration
rm -rf ~/.quantum_docker

# Remove virtual environment
deactivate
rm -rf quantum_docker_env
```

### Clean Docker Resources

```bash
# Remove quantum docker containers
docker system prune -f

# Remove quantum docker images
docker rmi $(docker images -q quantum-docker-*)
```

## Troubleshooting Installation

### Common Issues

**Permission denied for Docker**:
```bash
sudo usermod -aG docker $USER
# Logout and login again
```

**Python module not found**:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall in virtual environment
pip install -r requirements.txt --force-reinstall
```

**qdocker command not found**:
```bash
# Check if package is installed
pip list | grep quantum

# Add to PATH
export PATH="$PATH:$HOME/.local/bin"
```

**Quantum simulation errors**:
```bash
# Check available memory
free -h

# Reduce qubit count in configuration
# Set num_qubits: 8 in config file
```

### Getting Help

If you encounter issues:

1. Check the troubleshooting section
2. Run the verification script
3. Check Docker and Python installations
4. Create an issue on GitHub with your error details

---

**Installation Complete!** You're now ready to explore quantum container orchestration. Proceed to the [Getting Started Guide](GETTING_STARTED.md) for your first quantum container deployment.
