# How to Use Client-Side Monitor Service
## What This Does:
   This service runs silently in the background on your computer and:
   - Takes screenshots when asked
   - Monitors open applications
   - Shows a "freeze" message when activated
   - Sends information to a monitoring server
This runs in the background as a Windows Service - you won't see a window or icon.

---

## Installation Steps (Manual)

### Step 1: Install Required Software

You need Python and some packages. Computers in the computer lab already hae python, but not the packages.

#### Option A: Automatic Setup (Easiest)
1. Open Command Prompt as Administrator:
   - Press `Win + R`
   - Type: `cmd`
   - Press `Ctrl + Shift + Enter` (runs as admin)

2. Copy and paste this entire command:
```
pip install pywin32 cryptography pillow numpy psutil pyautogui && python -m Scripts/pywin32_postinstall -install
```

3. Wait for it to finish

#### Option B: Manual Setup
If Option A doesn't work:

1. Open Command Prompt as Administrator
2. Run each command separately:
   ```
   pip install pywin32
   ```
   ```
   pip install cryptography
   ```
   ```
   pip install pillow
   ```
   ```
   pip install numpy
   ```
   ```
   pip install psutil
   ```
   ```
   pip install pyautogui
   ```
   ```
   python -m Scripts/pywin32_postinstall -install
   ```

---

### Step 2: Configure the Port

The service needs to know which **port** to listen on. A port is like a "communication channel."

1. Find the file called `socket.txt` in the same folder as the service files
2. Open it with Notepad (right-click → Open with → Notepad)
3. Delete whatever is inside
4. Type a number between 1000 and 65000 (example: `5000`)
5. Save it

**Example socket.txt contents:**
```
5000
```

---

### Step 3: Install the Service

Now tell Windows to install the service:

1. Open Command Prompt as Administrator
2. Navigate to the folder containing the service files. For example:
   ```
   cd C:\Users\YourName\Desktop\client-side
   ```
   (Replace `YourName` with your username and adjust path if needed)

3. Run this command:
   ```
   python install_service.py --install
   ```

4. You should see:
   ```
   ✓ Service 'Client-Side Monitor Service' installed successfully
   ```

---

### Step 4: Start the Service

1. Still in Command Prompt, run:
   ```
   python install_service.py --start
   ```

2. You should see:
   ```
   ✓ Service 'ClientSideMonitor' started
   ```

---

## Common Commands

### Check if it's running:
```
python install_service.py --status
```

### Stop the service:
```
python install_service.py --stop
```

### Start the service again:
```
python install_service.py --start
```

### View the activity log:
```
type logs\service.log
```

---

## Uninstalling

If you want to remove the service completely:

1. Open Command Prompt as Administrator
2. Navigate to your service folder
3. Stop it first:
   ```
   python install_service.py --stop
   ```
4. Remove it:
   ```
   python install_service.py --remove
   ```

5. You can then delete the folder with all the files.

---

## Troubleshooting

### "Python is not recognized"
- **Problem**: Command Prompt doesn't know what Python is
- **Solution**: 
  1. Uninstall Python
  2. Reinstall it from python.org
  3. Check the box that says "Add Python to PATH" during installation
  4. Restart your computer
  5. Try again

### "Access Denied" or "Admin required"
- **Problem**: You didn't open Command Prompt as Administrator
- **Solution**: 
  1. Right-click Command Prompt
  2. Select "Run as Administrator"
  3. Click "Yes" when asked

### Service won't start
- **Problem**: Could be many things
- **Solution**:
  1. Check `logs/service.log` for error messages
  2. Make sure `socket.txt` has a valid port number
  3. Make sure the port number isn't already in use by another program
  4. Try restarting your computer

### "Port already in use"
- **Problem**: Another program is using that port
- **Solution**:
  1. Open `socket.txt`
  2. Change the port to a different number (try `5001` or `5002`)
  3. Stop and restart the service

