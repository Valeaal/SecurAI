# 🛡️🌐 Bienvenido a SecurAI 🌐🛡️

En este trabajo fin de grado (TFG) se plantea desarrollar una aplicación que incorpora un IDS **(Sistema de Detección de Intrusos)** que se ejecutará **localmente en tiempo real** para varios sistemas operativos, de forma que la instalación será sencilla para todos los usuarios, generando instaladores para que el usuario final no tenga que tener conocimientos avanzados de informática.
El IDS analizará el tráfico de la red para estimar la probabilidad de que estemos siendo atacados. Para ello se estudiará el uso de
algunas técnicas de **inteligencia artificial** y se implementarán diversos algoritmos para notificar al usuario del ataque.

SecurAI es el resultado de esta investigación: un software modular, escalable e innovador que incorpora funcionalidades clave como módulos preestablecidos de detección de amenazas, recopilación de estadísticas de la red y simulación de ataques sobre el propio equipo para comprobar en tiempo real el rendimiento de los módulos.

## Tabla de contenidos

- [Contexto](#contexto)
- [Características implementadas](#características-implementadas)
- [Instalación](#instalación)
- [Resolución de problemas](#resolución-de-problemas)
- [Contacto](#contacto)
- [Documentación y memoria](#documentación-y-memoria)

## Contexto

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
- Sistema de guardado de logs nativo según el sistema operativo.
- Integración Continua, Despliegue Continuo (CI/CD).

## Instalación

Es normal que la aplicación tarde un tiempo considerable en abrise, ya que tiene que cargar los módulos de inteligencia artificial para procesar los paquetes de la red. No te preocupes si tarda unos minutos en abrise y otros en ponerse a funcionar.

### Para su uso normal

- **Si usas MacOS** descarga el archivo .dmg de la [release más reciente](https://github.com/Valeaal/SecurAI/releases/latest) e instálalo como cualquier aplicación de Mac. Como es común en MacOS, el sistema avisará de que no ha podido comprobar la seguridad de la aplicación. Tendrás que confiar en ella desde *Ajustes del Sistema > Privacidad y Seguridad > Abrir Igualmente* en el apartado de Seguridad para poder abrirla.
- **Si usas Windows** descarga el archivo .exe de la [release más reciente](https://github.com/Valeaal/SecurAI/releases/latest) e instálalo. Si no tienes instalado [Npcap](https://wiki.wireshark.org/NPcap), el instalador de SecurAI te pedirá instalarlo, solo tendrás que seguir los pasos indicados y seguir la configuración recomendada, no tienes que instalarlo manualmente. Es probable que salga un aviso de SmartScreen de Microsoft Defender, puedes pulsar *Más Información > Ejecutar de todas formas* para continuar el proceso.

Puedes confiar en el proyecto y, si lo deseas, puedes observar su código fuente por supuesto.

### Para desarrolladores

```bash

# Clonar el repositorio
git clone https://github.com/valeaal/SecurAI.git

# Entrar al directorio
cd /BackEnd

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el BackEnd
python3 run.py

# Entrar al directorio
cd ..
cd /FrontEnd/app

# Instalar dependencias
npm install -i

# Ejecutar el Frontend
npm run dev
```

Si el desarrollador quiere ver los logs que genera la aplicación, puede hacerlo fácilmente gracias a la funcionalidad de guardado de logs nativo al sistema operativo que ejecuta SecurAI.

Los logs se almacenan en la ruta determinada por app.getPath('logs'), que es compatible tanto con Windows como con macOS:

- En Windows: La ruta típicamente es С:\Users\Usuario\AppData\Roaming\SecurAI\logs.
- En MacOS: La ruta típicamente es /Users/Usuario/Library/Logs/SecurAI/.

## Resolución de problemas

- Si tras más de cinco minutos desde el inicio la aplicación muestra la interfaz morada sin más información, o parece no funcionar, es probable que esté funcionando pero el BackEnd no haya establecido bien la comunicación con el FrontEnd. Simplemente hay que recargar el FrontEnd.
  - **En MacOS** pulsa `cmd + R`.
  - **En Windows** pulsa `ctrl + R`.
- Si al abrir la aplicación en Windows siempre te solicita instalar Npcap, SecurAI no está detectando que ya está instalado.
  - No hay problema, puedes omitir la instalación, SecurAI funcionará con normalidad. Puedes comprobar que al intentar instalar Npcap por segunda vez, el mismo instalador te dice que ya está instalado.

## Contacto

Para cualquier consulta relacionada con este proyecto:

- Email: [valeal@uma.es](valeal@uma.es) o [alvavi2002@gmail.com](alvavi2002@gmail.com)
- LinkedIn: [Álvaro Valencia](www.linkedin.com/in/valeal)
- GitHub: [Valeaal](https://github.com/valeaal)

## Documentación y memoria

La documentación completa y la memoria del TFG están disponibles en el archivo `Memoria` de este repositorio. Muy recomendado para entender el funcionamiento, cambiar SecurAI a su gusto, o desarrollar nuevos módulos.
