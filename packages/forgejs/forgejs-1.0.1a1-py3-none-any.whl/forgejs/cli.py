#!/usr/bin/env python3
import os
import sys
import requests
import zipfile
import io
from pathlib import Path
import json

# ==============================
# CONFIGURACIÓN DEL REPO
# ==============================
GITHUB_USER = "BenjaMorenoo"
GITHUB_REPO = "ForgeJS-Templates"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = "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"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def get_frameworks():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/templates?ref={GITHUB_BRANCH}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ No se pudo obtener la lista de frameworks.")
        return []
    data = r.json()
    return [item["name"] for item in data if item["type"] == "dir"]

def get_templates_list(framework):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/templates/{framework}?ref={GITHUB_BRANCH}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ No se pudieron obtener las plantillas para este framework.")
        return []
    data = r.json()
    return [item["name"] for item in data if item["type"] == "dir"]

def list_template_folders(framework, template_name):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/templates/{framework}/{template_name}?ref={GITHUB_BRANCH}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ No se pudo obtener el contenido de la plantilla.")
        return []
    data = r.json()
    folders = [item for item in data if item["type"] == "dir"]

    print(f"\n📁 Estructura de '{template_name}':")
    for folder in folders:
        print(f"📦 {folder['name']}/")
        if folder["name"] == "src":
            src_url = folder["url"]
            src_response = requests.get(src_url, headers=HEADERS)
            if src_response.status_code == 200:
                src_data = src_response.json()
                src_folders = [f for f in src_data if f["type"] == "dir"]
                if src_folders:
                    for sub in src_folders:
                        print(f"   └── 📂 {sub['name']}/")
                else:
                    print("   (src/ está vacío)")
            else:
                print(f"   ⚠️  No se pudo acceder a src/ ({src_response.status_code})")
    print("")
    return [folder["name"] for folder in folders]

def download_from_repo(search_path, target_dir):
    zip_url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
    r = requests.get(zip_url, headers=HEADERS)
    if r.status_code != 200:
        print("❌ Error al descargar el repositorio.")
        return False

    with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
        matching_files = [f for f in zip_ref.namelist() if search_path in f]
        if not matching_files:
            print(f"❌ No se encontró '{search_path}' en el repositorio.")
            return False

        for file in matching_files:
            relative_path = file.split(search_path, 1)[-1]
            if not relative_path:
                continue
            target_path = target_dir / relative_path
            if file.endswith("/"):
                os.makedirs(target_path, exist_ok=True)
            else:
                os.makedirs(target_path.parent, exist_ok=True)
                with zip_ref.open(file) as src, open(target_path, "wb") as dst:
                    dst.write(src.read())
    return True

def update_package_json(project_name):
    pkg_path = Path(project_name) / "package.json"
    if pkg_path.exists():
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg_data = json.load(f)
        pkg_data["name"] = project_name
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(pkg_data, f, indent=2)
        print(f"📦 package.json actualizado con el nombre '{project_name}'")
    else:
        print("⚠️ No se encontró package.json")

def add_custom_folders(project_name):
    while True:
        add_folder = input("¿Quieres agregar una carpeta personalizada? (s = Sí / n = No): ").strip()
        if add_folder.lower() != "s":
            break
        folder_name = input("👉 Nombre de la carpeta a crear (ej. hooks): ").strip()
        if folder_name:
            folder_path = Path(project_name) / "src" / folder_name
            os.makedirs(folder_path, exist_ok=True)
            print(f"📁 Carpeta '{folder_name}' creada dentro de src/")

def run_npm_install(project_name):
    choice = input("¿Quieres ejecutar 'npm install' automáticamente? (s = Sí / n = No): ").strip()
    if choice.lower() == "s":
        print("\n📦 Instalando dependencias...")
        os.chdir(project_name)
        os.system("npm install")
        print("\n✅ Dependencias instaladas correctamente.")
    else:
        print(f"\nℹ️ Puedes instalar dependencias manualmente con:\n cd {project_name}\n npm install")

# ==============================
# FUNCIONES PRINCIPALES
# ==============================
def create_project():
    print("🚀 Crear proyecto ForgeJS\n")
    frameworks = get_frameworks()
    if not frameworks: return

    print("🧩 Frameworks disponibles:")
    for i, fw in enumerate(frameworks, 1):
        print(f" {i}. {fw}")

    while True:
        try:
            fw_choice = int(input("\nSelecciona un framework (número): ").strip())
            if 1 <= fw_choice <= len(frameworks):
                framework = frameworks[fw_choice - 1]
                break
            else:
                print("❌ Número fuera de rango")
        except ValueError:
            print("❌ Entrada inválida")

    templates = get_templates_list(framework)
    if not templates: return

    while True:
        print(f"\n📦 Plantillas disponibles para {framework}:")
        for i, temp in enumerate(templates, 1):
            print(f" {i}. {temp}")
        try:
            temp_choice = int(input("\nElige una plantilla (número): ").strip())
            if 1 <= temp_choice <= len(templates):
                template_name = templates[temp_choice - 1]
                list_template_folders(framework, template_name)
                confirm = input("\n¿Deseas usar esta plantilla? (s = Sí / n = Volver a la lista): ").strip().lower()
                if confirm == "s":
                    break
            else:
                print("❌ Número fuera de rango")
        except ValueError:
            print("❌ Entrada inválida")

    project_name = input(f"\nNombre del nuevo proyecto (Enter = '{template_name}'): ").strip() or template_name
    print(f"ℹ️ Se usará '{project_name}' como nombre del proyecto")

    target_dir = Path.cwd() / project_name
    os.makedirs(target_dir, exist_ok=True)
    search_path = f"templates/{framework}/{template_name}/"
    if not download_from_repo(search_path, target_dir): return
    update_package_json(project_name)

    # Guardar configuración del proyecto
    config = {"framework": framework, "template": template_name}
    with open(target_dir / ".forgejs.json", "w") as f:
        json.dump(config, f)

    add_custom_folders(project_name)
    run_npm_install(project_name)
    print(f"\n🎉 Proyecto '{project_name}' listo para usar!")

def add_component(component_name):
    project_path = Path.cwd()
    config_path = project_path / ".forgejs.json"
    if not config_path.exists():
        print("❌ No se detectó un proyecto ForgeJS aquí.")
        return

    with open(config_path) as f:
        config = json.load(f)
    framework = config["framework"]

    search_path = f"components/{framework}/{component_name}/"
    target_dir = project_path / "src" / "components"
    os.makedirs(target_dir, exist_ok=True)

    if download_from_repo(search_path, target_dir):
        print(f"✅ Componente '{component_name}' agregado correctamente!")
    else:
        print(f"❌ No se pudo agregar el componente '{component_name}'")

# ==============================
# CLI PRINCIPAL
# ==============================
def main():
    if len(sys.argv) == 1 or sys.argv[1] == "create":
        create_project()
    elif sys.argv[1] == "add":
        if len(sys.argv) < 3:
            print("❌ Debes indicar el nombre del componente: forgejs add <nombre>")
            return
        add_component(sys.argv[2])
    else:
        print("❌ Comando no reconocido. Usa 'create' o 'add <nombre>'")
