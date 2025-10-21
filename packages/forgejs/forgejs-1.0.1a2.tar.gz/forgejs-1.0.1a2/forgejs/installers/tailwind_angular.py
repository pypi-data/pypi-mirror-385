import os
from pathlib import Path

def setup_tailwind_angular(project_path: Path):
    print("🎨 Instalando TailwindCSS para Angular...")

    os.system("npm install -D tailwindcss postcss autoprefixer")

    tailwind_config = project_path / "tailwind.config.js"
    postcss_config = project_path / "postcss.config.js"
    styles_css = project_path / "src" / "styles.css"

    tailwind_config.write_text("""/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: { extend: {} },
  plugins: [],
}
""", encoding="utf-8")

    postcss_config.write_text("""module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""", encoding="utf-8")

    if styles_css.exists():
        styles_css.write_text("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n", encoding="utf-8")

    print("✅ TailwindCSS configurado correctamente para Angular.")
