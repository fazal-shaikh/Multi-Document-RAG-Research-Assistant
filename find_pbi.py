import os

app_data = os.environ.get('APPDATA', '')      # Roaming
local_app_data = os.environ.get('LOCALAPPDATA', '') # Local
user_profile = os.environ.get('USERPROFILE', '')

search_dirs = [
    local_app_data,
    app_data,
    os.path.join(user_profile, 'AppData', 'Local', 'Packages')
]

print("Searching for 'msmdsrv.port.txt' or 'AnalysisServicesWorkspaces'...")

found = False
for s_dir in search_dirs:
    if not s_dir or not os.path.exists(s_dir):
        continue
    print(f"Searching in: {s_dir}")
    for root, dirs, files in os.walk(s_dir):
        # We can optimize search: skip folders with too many files if needed,
        # but let's check for specific subdirectories first.
        # Often Power BI Desktop's path will contain "Power BI Desktop" or "MicrosoftPowerBIDesktop"
        if "Power BI" in root or "PowerBI" in root or "msmdsrv" in root:
            for file in files:
                if 'port' in file.lower() or 'msmdsrv' in file.lower():
                    full_path = os.path.join(root, file)
                    print(f"Found match: {full_path}")
                    found = True
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            print(f"  Content: {f.read().strip()}")
                    except Exception as e:
                        print(f"  Error: {e}")

if not found:
    print("Could not find any msmdsrv/PowerBI port files in standard location. Checking if any msmdsrv.exe is running...")
    # Let's check running processes using tasklist
    import subprocess
    try:
        res = subprocess.run(["tasklist"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if "pbi" in line.lower() or "msmdsrv" in line.lower():
                print(f"Running process: {line}")
    except Exception as e:
        print(f"Error running tasklist: {e}")
