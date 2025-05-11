# 🛡️🌐 Bienvenido a SecurAI 🌐🛡️

## Tabla de contenidos

- [Descripción del proyecto](#descripción-del-proyecto)
- [Características implementadas](#características-implementadas)
- [Instalación](#instalación)
- [Contacto](#contacto)
- [Documentación y memoria](#documentación-y-memoria)

## Descripción del proyecto

En este trabajo fin de grado (TFG) se plantea desarrollar una aplicación que incorpora un IDS **(Sistema de Detección de Intrusos)** que se ejecutará **localmente en tiempo real** para varios sistemas operativos, de forma que la instalación será sencilla para todos los usuarios, generando instaladores para que el usuario final no tenga que tener conocimientos avanzados de informática.
El IDS analizará el tráfico de la red para estimar la probabilidad de que estemos siendo atacados. Para ello se estudiará el uso de
algunas técnicas de **inteligencia artificial** y se implementarán diversos algoritmos para notificar al usuario del ataque.

---

Es poco común que los hogares o pequeñas empresas tengan una protección avanzada de sus redes. No es trivial el uso de
herramientas IDS/IPS (Sistema de Detección/Prevención de Intrusos) y requieren de un conocimiento avanzado para su
instalación y utilización. En un contexto social en el que los sistemas informáticos cada vez son más frecuentes y manejan
información cada vez más importante, es crucial tener un escudo ante, por lo menos, los ataques más comunes que podemos
recibir.
Destacar también que la complejidad de los ataques cibernéticos está en claro aumento, por lo que las técnicas de protección y
prevención que hasta ahora han funcionado están en camino de ser ineficaces, por eso es muy importante mantener el desarrollo
de tecnologías punteras, accesibles y al nivel de los atacantes, para garantizar que la infraestructura digital de nuestro hogar o
negocio no se verá comprometida.
La tecnología de detección o prevención de intrusos no es nueva. Un ejemplo de las plataformas ya existentes es [Suricata](https://github.com/OISF/suricata), un proyecto open source que basa su funcionamiento en la definición de reglas que detecten y/o frenen ciertos tipos de ataques. Aun siendo una herramienta extremadamente potente, sus usuarios se quejan de la complejidad que supone su uso ya que por ejemplo
[no posee interfaz gráfica oficial](https://forum.suricata.io/t/suricata-web-gui/2901), lo cual aleja esta herramienta de muchísimos usuarios potenciales. Otro punto de mejora de Suricata es que funciona con reglas predefinidas, y no contempla por ahora el uso de herramientas de inteligencia artificial que pueden ser claves para el [futuro desarrollo de este tipo de herramientas](https://suri-oculus.com/using-ai-in-suricata-enhancing-intrusion-detection-system-capabilities/) ante ataques cada vez más sofisticados.

## Características implementadas

- Sistema modular fácilmente escalable.
- Módulos de inteligencia artificial para la detección de patrones complejos.
- Recopilación de estadísticas de la red.
- Simulación de ataques para probar el rendimiento.
- Instaladores cómodos, no se requieren conocimientos previos.

## Instalación

### Para su uso normal

- **Si usas MacOS** descarga el archivo .dmg de la [release más reciente](https://github.com/Valeaal/SecurAI/releases/latest) e instálalo como cualquier aplicación de Mac.
- **Si usas Windows** descarga el archivo .exe de la [release más reciente](https://github.com/Valeaal/SecurAI/releases/latest) e instálalo. Si no tienes instalado Npcap, el instalador te pedirá instalarlo, solo tendrás que seguir los indicados pasos. Es probable que salga un aviso de SmartScreen de Microsoft Defender, puedes pulsar *Más Información > Ejecutar de todas formas* para continuar el proceso.

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

- Email: [valeal@uma.es] o [alvavi2002@gmail.com]
- LinkedIn: [Álvaro Valencia](www.linkedin.com/in/valeal)
- GitHub: [Valeaal](https://github.com/valeaal)

## Documentación y memoria

La documentación completa y la memoria del TFG están disponibles en la carpeta `/Memoria` de este repositorio. Muy recomendado para entender el funcionamiento, cambiar SecurAI a su gusto, o desarrollar nuevos módulos.
