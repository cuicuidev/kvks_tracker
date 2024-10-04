import os
import subprocess
import shutil
import zipfile
import venv

root_dir = os.path.abspath(os.path.dirname(__file__))
desktop_dir = os.path.join(root_dir, 'desktop')
api_dir = os.path.join(root_dir, 'api')
bin_dir = os.path.join(api_dir, 'downloads', 'bin')

scripts = {
    'main_job': {
        'path': os.path.join(desktop_dir, 'main_job', 'main.py'),
        'requirements': os.path.join(desktop_dir, 'main_job', 'requirements.txt'),
        'output_name': 'kvks_tracker'
    },
    'setup': {
        'path': os.path.join(desktop_dir, 'setup', 'main.py'),
        'requirements': os.path.join(desktop_dir, 'setup', 'requirements.txt'),
        'output_name': 'kovaaks_tracker_setup'
    },
    'watchdog_config': {
        'path': os.path.join(desktop_dir, 'watchdog_config', 'main.py'),
        'requirements': os.path.join(desktop_dir, 'watchdog_config', 'requirements.txt'),
        'output_name': 'config'
    }
}

os.makedirs(bin_dir, exist_ok=True)

def build_script(script):
    venv_dir = os.path.join(root_dir, f'venv_{script["output_name"]}')
    venv.create(venv_dir, with_pip=True)
    
    subprocess.check_call([os.path.join(venv_dir, 'Scripts', 'python.exe'), '-m', 'pip', 'install', '-r', script['requirements']])

    subprocess.check_call([
        os.path.join(venv_dir, 'Scripts', 'python.exe'), '-m', 'PyInstaller',
        '--onefile',
        '--name', script['output_name'],
        '--distpath', bin_dir,
        '--windowed',
        script['path']
    ])
    
    shutil.rmtree(venv_dir)

for script_key, script in scripts.items():
    print(f"Building {script_key}...")
    build_script(script)

print("Zipping the build")
zip_file_path = os.path.join(bin_dir, 'desktop_client.zip')
with zipfile.ZipFile(zip_file_path, 'w') as zipf:
    for script_key in ['main_job', 'watchdog_config']:
        executable_name = f"{scripts[script_key]['output_name']}.exe"
        executable_path = os.path.join(bin_dir, executable_name)
        if os.path.exists(executable_path):
            zipf.write(executable_path, arcname=executable_name)

print("Cleaning up")
for script_key in ['main_job', 'watchdog_config']:
    executable_name = f"{scripts[script_key]['output_name']}.exe"
    executable_path = os.path.join(bin_dir, executable_name)
    if os.path.exists(executable_path):
        print(f"Removing unzipped executable: {executable_path}")
        os.remove(executable_path)

print("Build process completed successfully!")