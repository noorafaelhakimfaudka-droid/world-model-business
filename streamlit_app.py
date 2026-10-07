"""
streamlit_app.py
Root entry point for Streamlit Community Cloud deployment.
Executes app.py
"""
import sys
import os
import runpy

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Hapus cache modul lokal dari sys.modules agar perubahan kode selalu terbaca segar saat refresh browser
for mod in list(sys.modules.keys()):
    if any(mod.startswith(pkg) for pkg in ["ui", "screens", "core"]):
        del sys.modules[mod]

runpy.run_path(os.path.join(root_dir, "app.py"), run_name="__main__")
