import os
import threading
import importlib.util

defenseAlgorithmsPath = "./app/defenseAlgorithms"
algorithms = []
algorithm_names = []

def loadDefenseAlgorithms(path=defenseAlgorithmsPath):
    print("Cargando algoritmos de defensa...")
    for fileName in os.listdir(path):
        if fileName.endswith(".py"):
            moduleName = fileName[:-3]
            modulePath = os.path.join(path, fileName)
            spec = importlib.util.spec_from_file_location(moduleName, modulePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "detect"):
                algorithms.append(module)
                algorithm_names.append(moduleName)
            else:
                print(f"⚠️ {fileName} no contiene una función `detect`.")

    for module in algorithms:
        # Esto arrancará cada módulo. La lógica dependerá del módulo, la restricción es que tengan un método detect.
        moduleThread = threading.Thread(target=module.detect, daemon=True)
        moduleThread.start()

def getDefenseAlgorithmNames():
    return algorithm_names