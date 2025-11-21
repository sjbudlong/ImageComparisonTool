# Quick Start Guide

## For Online Environments

### 1. Install
```bash
pip install -r requirements.txt
python verify_installation.py
```

### 2. Run
```bash
# GUI mode
python main.py

# CLI mode
python main.py --base-dir /path/to/images --new-dir new --known-good-dir baseline
```

---

## For Offline Environments

### On Internet-Connected Machine

1. **Download dependencies:**
   ```bash
   # Linux/Mac
   ./offline_setup.sh
   
   # Windows
   offline_setup.bat
   ```

2. **Transfer folder:**
   - Copy `offline_packages/` to USB drive
   - Move to offline machine

### On Offline Machine

3. **Install:**
   ```bash
   cd offline_packages
   
   # Linux/Mac
   ./install_offline.sh
   
   # Windows
   install_offline.bat
   ```

4. **Verify:**
   ```bash
   cd ..
   python dependencies.py
   python verify_installation.py
   ```

5. **Run:**
   ```bash
   python main.py
   ```

---

## Common Commands

### Check Dependencies
```bash
python dependencies.py                  # Check what's installed
python dependencies.py --save-freeze    # Save exact versions
python verify_installation.py           # Full system test
```

### Run Comparisons
```bash
# GUI with all options
python main.py

# CLI with histogram equalization (for 3D renders)
python main.py \
  --base-dir ./renders \
  --new-dir current \
  --known-good-dir baseline \
  --use-histogram-eq \
  --color-distance-threshold 20 \
  --highlight-color "0,0,255"

# Skip dependency check for faster startup
python main.py --skip-dependency-check
```

### View Results
Open `reports/summary.html` in a web browser

---

## Troubleshooting

### "Module not found" errors
```bash
# Check what's missing
python dependencies.py

# Install missing package
pip install <package-name>
```

### tkinter missing (Linux only)
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter # Fedora/RHEL
```

### Can't run in offline environment
1. Verify Python 3.8+ is installed: `python --version`
2. Check dependencies: `python dependencies.py`
3. If packages missing, redo offline installation steps

### OpenCV import fails
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

---

## Next Steps

- Read **README.md** for full documentation
- Adjust tolerances in GUI for your use case
- For 3D renders, enable histogram equalization
- Customize highlight colors for different test types

## Support

Run `python main.py --help` for all options
