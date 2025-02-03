import os
import time
import threading
import importlib.util

from scapy.all import sniff

machineLearnTimeout = 10  # Valor por defecto para entrenar la IA cada 10s
defenseAlgorithmsPath = "./app/defenseAlgorithms"

# Lista para almacenar los tiempos de análisis
analysisTimes = []
lastPrintTime = time.time()

def loadDefenseAlgorithms(path):
    print("Cargando algoritmos de defensa...")
    algorithms = []
    for fileName in os.listdir(path):
        if fileName.endswith(".py"):  # Filtrar solo archivos Python
            moduleName = fileName[:-3]  # Quitar la extensión `.py`
            modulePath = os.path.join(path, fileName)
            
            # Cargar el módulo dinámicamente
            spec = importlib.util.spec_from_file_location(moduleName, modulePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Verificar si el módulo tiene la función `detect`
            if hasattr(module, "detect"):
                algorithms.append(module.detect)
            else:
                print(f"El archivo {fileName} no contiene una función `detect`.")

    return algorithms

def packetProcessing(packet):
    global lastPrintTime
    analysisStartTime = time.time()

    # Procesamiento del paquete con los algoritmos de defensa
    for detect in defenseAlgorithms:
        try:
            detect(packet)  # Ejecutar la función `detect` del algoritmo
        except Exception as e:
            print(f"Error ejecutando un algoritmo: {e}")

    # Tiempo de análisis
    analysisEndTime = time.time()
    analysisTime = analysisEndTime - analysisStartTime
    analysisTimes.append(analysisTime)

    # Verificar si han pasado al menos 10 segundos desde la última impresión
    currentTime = time.time()
    if currentTime - lastPrintTime >= 20:
        # Calcular el promedio de los tiempos de análisis
        avgAnalysisTime = sum(analysisTimes) / len(analysisTimes) if analysisTimes else 0
        print(f"Promedio de tiempo de análisis: {avgAnalysisTime:.8f} segundos")
        
        # Restablecer los tiempos de análisis y actualizar el tiempo de impresión
        analysisTimes.clear()
        lastPrintTime = currentTime

def packetCapture():
    global defenseAlgorithms
    defenseAlgorithms = loadDefenseAlgorithms(defenseAlgorithmsPath) 

    print(f"Iniciando captura de paquetes en el hilo {threading.get_ident()}...")
    while True:
        paquetes = sniff(timeout=machineLearnTimeout,prn=packetProcessing)

        """
        #Esto es si eligieramos la opción 2a
        if paquetes:
            # Crea y arranca una nueva hebra cada 10s para entrenar los modelos en segundo plano
            trainingThread = threading.Thread(target=trainModels(paquetes))
            trainingThread.daemon = True
            trainingThread.start()    
        """

