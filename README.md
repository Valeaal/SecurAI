# 🛡️🌐 Bienvenido a SecurAI 🌐🛡️

## Descripción del proyecto

En este trabajo fin de grado (TFG) se plantea desarrollar una aplicación que incorpora un IDS **(Sistema de Detección de Intrusos)** que se ejecutará **localmente en tiempo real** para varios sistemas operativos, de forma que la instalación será sencilla para todos los usuarios, generando instaladores para que el usuario final no tenga que tener conocimientos avanzados de informática.
El IDS analizará el tráfico de la red para estimar la probabilidad de que estemos siendo atacados. Para ello se estudiará el uso de
algunas técnicas de **inteligencia artificial** y se implementarán diversos algoritmos para notificar al usuario del ataque.

## Tabla de contenidos

- [Descripción del proyecto](#descripción-del-proyecto)
- [Características implementadas](#características-implementadas)
- [Instalación](#instalación)
- [Contacto](#contacto)
- [Documentación y memoria](#documentación-y-memoria)

## Características implementadas

- Sistema modular fácilmente escalable
- Módulos de inteligencia artificial para la detección de patrones complejos
- Recopilación de estadísticas de la red
-Simulación de ataques para probar el rendimiento

## Instalación

### Para su uso normal

- **Si usas MacOS** descarga el archivo .dmg de la [release más reciente](https://github.com/Valeaal/SecurAI/releases/latest) e instálalo como cualquier aplicación de Mac.
- **Si usas Windows** descarga el archivo .exe de la [release más reciente](https://github.com/Valeaal/SecurAI/releases/latest) e instálalo. Si no tienes instalado Npcap, el instalador te pedirá instalarlo, solo tendrás que seguir los indicados pasos.

Puedes confiar en el proyecto y, si lo deseas, puedes observar su código fuente por supuesto.

### Para desarrolladores

```bash

# Clonar el repositorio
git clone https://github.com/valeaal/SecurAI.git

# Entrar al directorio
cd SecurAI/BackEnd

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el BackEnd
python3 run.py

# Entrar al directorio
cd SecurAI/FrontEnd/app

# Instalar dependencias
npm install -i

# Ejecutar el Frontend
npm run dev
```

## Contacto

Para cualquier consulta relacionada con este proyecto:

- Email: valeal@uma.es o alvavi2002@gmail.com
- GitHub: [Álvaro Valencia](https://github.com/valeaal)

## Documentación y memoria

La documentación completa y la memoria del TFG están disponibles en la carpeta `/Memoria` de este repositorio. Muy recomendado para entender el funcionamiento, cambiar SecurAI a su gusto, o desarrollar nuevos módulos.