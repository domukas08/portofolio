@echo off
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background "%~dp0nettside.blend" --python "%~dp0export_glb.py"
echo Done. Refresh the browser to see changes.
