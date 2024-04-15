import os
import shutil
import subprocess
from rich.console import Console

console = Console()

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Create .asar folder
asar_folder = os.path.join(os.path.dirname(__file__), '.asar')
if os.path.exists(asar_folder):
    shutil.rmtree(asar_folder)
else:
    os.mkdir(asar_folder)

    
console.clear()
console.print('Loading current myLIM .asar...', style='bold green')
mylim_asar = '/Applications/myLIM.app/Contents/Resources/app.asar'
output_dir = os.path.join(os.path.dirname(__file__), '.asar')

# Extract app.asar using 'asar' command
command = ['asar', 'e', mylim_asar, output_dir]
subprocess.run(command, check=True)

script_path = os.path.join(output_dir, 'electron', 'main.js')
script = read_file_content(script_path)

if script:
    if 'patchlim' in script:
        console.clear()
        console.print('myLIM is already patched.', style='bold red')
        exit(0)
    else:
        # Patch DevTools
        script = script.replace('process.env.MYLIM_ELECTRON_DEBUG', 'true')

        # Write patched script
        with open(script_path, 'w') as file:
            file.write('const { patchlim } = require("./mod.js");\n')
            file.write('patchlim();\n')
            file.write(script)
        
        console.clear()
        console.print('Patching of main script done!', style='bold green')


        ui_path = os.path.join(output_dir, 'www', 'index.html')
        with open(ui_path, 'r') as file:
            ui_content = file.read()
            ui_content = ui_content.replace('<script src="cordova.js"></script>', '<script src="cordova.js"></script>\n<!-- patchlim code --!>\n<script src="ui-mod.js"></script>')
            with open(ui_path, 'w') as file:
                file.write(ui_content)
            with open(os.path.join(output_dir, 'www', 'ui-mod.js'), 'w') as file:
                file.write(read_file_content(os.path.join(os.path.dirname(__file__), 'modification', 'web-mod.js')))

        console.clear()
        console.print('Patching of UI script done!', style='bold green')

        # Write mod.js
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'modification', 'electron-mod.js'), os.path.join(output_dir, 'electron', 'mod.js'))
        console.clear()
        console.print('Applying patch to myLIM...', style='bold green')

        # Pack .asar folder into app.asar
        asar_command = ['asar', 'p', output_dir, mylim_asar]
        subprocess.run(asar_command, check=True)

        # Remove .asar folder
        shutil.rmtree(asar_folder)

        console.clear()
        console.print('Patch applied successfully!', style='bold green')
        exit(0)
else:
    console.print('Error reading Electron script .js!','bold red')
    exit(1)
