import os
import threading
import importlib.util

attackTestsPath = "./app/attackTests"
attackTests = []
attackTest_names = []

def loadAttackTests(path=attackTestsPath):
    print("Cargando ataques...")

    for fileName in os.listdir(path):
        if fileName.endswith(".py"):  # Filtrar solo archivos Python
            moduleName = fileName[:-3]  # Quitar la extensión `.py`
            modulePath = os.path.join(path, fileName)
            
            # Cargar el módulo dinámicamente
            spec = importlib.util.spec_from_file_location(moduleName, modulePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Asegurarse que el módulo tiene la función `attack`
            if hasattr(module, "attack"):
                attackTests.append(module)
                attackTest_names.append(moduleName)
            else:
                print(f"⚠️ {fileName} no contiene una función `attack`.")

    for module in attackTests:
        # Esto arrancará cada módulo. La lógica dependerá del módulo, la restricción es que tengan un método attack.
        moduleThread = threading.Thread(target=module.attack, daemon=True)
        moduleThread.start()

def getAttackTestsNames():
    return attackTest_names