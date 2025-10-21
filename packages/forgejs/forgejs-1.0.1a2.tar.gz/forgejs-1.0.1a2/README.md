# ForgeJS

🚀 **ForgeJS** es un scaffolding para proyectos JavaScript/TypeScript que permite crear proyectos personalizados usando plantillas alojadas en GitHub.

Con ForgeJS puedes:

- Elegir frameworks disponibles.  
- Seleccionar plantillas de proyectos.  
- Ver la estructura de carpetas antes de crear el proyecto.  
- Agregar carpetas personalizadas.  
- Ejecutar `npm install` automáticamente.  
- **Agregar componentes predefinidos a tu proyecto** usando un comando en la terminal **(Fase alpha)**.  
- **Instalar y configurar librerías populares** (como TailwindCSS) mediante un solo comando.

---

## 🔹 Requisitos

- Node.js y npm (para proyectos Node/React)  
- Python 3.7 o superior  
- Internet para descargar las plantillas y componentes  

---

## 🔸 IMPORTANTE

- De momento solo contiene plantillas con **JavaScript (JS)**  
  *(TypeScript será implementado en una próxima actualización)*  
- Framework disponible: **React**  
- Cada carpeta de cada plantilla contiene un archivo `.MD` para entender la estructura y el contenido.  

---

## � Tokens de GitHub (opcional pero recomendado)

ForgeJS descarga las plantillas desde GitHub.  
GitHub limita las peticiones **a 60 por hora** si no estás autenticado.

Para evitar ese límite, puedes configurar tu propio **token personal**:  

1. Crea un token en GitHub desde  
   👉 [https://github.com/settings/tokens](https://github.com/settings/tokens)  
   (solo necesitas habilitar el permiso `public_repo`)

2. Luego configúralo en tu sistema:

### 💻 En Windows PowerShell:
```bash
setx FORGEJS_GITHUB_TOKEN "ghp_tuTokenAqui"
```

### 🐧 En macOS / Linux:
```bash
export FORGEJS_GITHUB_TOKEN="ghp_tuTokenAqui"
```

Cierra y vuelve a abrir la terminal.

ForgeJS detectará automáticamente el token y lo usará para realizar las descargas sin restricciones.

⚠️ **Si no configuras el token**, ForgeJS seguirá funcionando, pero con el límite público de 60 peticiones por hora (por IP).

---

## 🔨 Crear proyectos

Crear proyectos con ForgeJS es muy sencillo.  
Solo necesitas ejecutar uno de los siguientes comandos:

```bash
forgejs
```

o

```bash
forgejs create
```

Luego podrás:

- Elegir el framework disponible.
- Ver las plantillas disponibles.
- Visualizar la estructura de carpetas antes de descargarla.
- Confirmar la plantilla y crear tu proyecto automáticamente.

---

## 📦 Componentes (Fase Alpha)

ForgeJS permite agregar componentes ya creados a un proyecto existente mediante:

```bash
forgejs add <nombre_del_componente>
```

**Ejemplo:**

```bash
forgejs add LoginForm
```

📁 Esto descargará el componente desde el repositorio de ForgeJS y lo colocará automáticamente dentro de la carpeta `src/components` del proyecto actual.

---

## 🎨 Instalación de librerías y frameworks

ForgeJS también permite instalar y configurar librerías populares con un solo comando.  
Actualmente se encuentra en **fase experimental**, con soporte inicial para **TailwindCSS**.

### Comandos disponibles

```bash
forgejs install tailwindcss
```

O sus alias más cortos:

```bash
forgejs i tailwindcss
```

o

```bash
forgejs install tcss
```

### 💡 Ejemplo (React + Vite)

```bash
forgejs install tailwindcss
```

👉 Instalará y configurará automáticamente TailwindCSS en un proyecto React creado con Vite, modificando los archivos `vite.config.js` e `index.css`.

### 💡 Ejemplo (Angular)

Si el proyecto fue creado con Angular, ForgeJS detectará el framework automáticamente y ejecutará la configuración correspondiente (TailwindCSS para Angular, con `postcss` y `autoprefixer`).

---

## ⚙️ Configuración del proyecto

Cada proyecto creado con ForgeJS genera un archivo interno `.forgejs.json` que guarda la información de la plantilla y el framework utilizados.  
Esto permite a ForgeJS reconocer el entorno cuando agregas componentes u otras funciones futuras.

**Ejemplo:**

```json
{
  "framework": "react",
  "template": "basic_template"
}
```

---

## 🧩 Próximas características

- Soporte completo para TypeScript (TS)
- Nuevos frameworks: Vue, Svelte, Angular, Next.js, etc.
- Instaladores inteligentes para librerías como Bootstrap, Framer Motion, Chakra UI, etc.
- Biblioteca de componentes dinámica y personalizable
- Sistema de plugins ForgeJS (extensiones creadas por la comunidad)
