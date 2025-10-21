import os
from pathlib import Path

def setup_tailwind_react(project_path: Path):
    print("🎨 Instalando TailwindCSS para React (Vite)...")

    vite_config_path = project_path / "vite.config.js"
    index_css_path = project_path / "src" / "index.css"
    app_css_path = project_path / "src" / "App.css"

    if not vite_config_path.exists():
        print("❌ No se encontró vite.config.js. ¿Seguro que es un proyecto React + Vite?")
        return

    os.system("npm install tailwindcss @tailwindcss/vite")

    vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(),],
})
"""
    vite_config_path.write_text(vite_config, encoding="utf-8")
    index_css_path.write_text('@import "tailwindcss";\n', encoding="utf-8")

    if app_css_path.exists():
        app_css_path.unlink()

    print("✅ TailwindCSS configurado correctamente para React.")
