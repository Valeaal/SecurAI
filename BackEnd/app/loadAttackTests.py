import os
import threading
import importlib.util

# Ruta donde se encuentran los archivos de ataque
attackTestsPath = "./app/attackTests"

# Diccionario donde almacenamos los módulos y la lista de nombres
attackTests = {}  # Clave -> Nombre, Valor -> Módulo

def getAttackTestsNames():
    return list(attackTests.keys())

def loadAttackTests(path=attackTestsPath):
    print("Cargando ataques...")
    attackTests.clear()  # Limpiar ataques previos

    for fileName in os.listdir(path):
        if fileName.endswith(".py"):  # Solo archivos .py
            moduleName = fileName[:-3]  # Nombre del módulo sin extensión
            modulePath = os.path.join(path, fileName)

            # Cargar el módulo dinámicamente
            spec = importlib.util.spec_from_file_location(moduleName, modulePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Asegurarse de que el módulo tiene la función `attack`
            if hasattr(module, "attack"):
                attackTests[moduleName] = module
                # print(f"✅ {fileName} cargado correctamente.")                
                moduleThread = threading.Thread(target=module.attack, daemon=True)
                moduleThread.start()
            else:
                print(f"⚠️ {fileName} no contiene una función `attack`.")

def startAttack(attack_name):
    """
    Inicia un ataque si no está en ejecución.
    """
    if attack_name in attackTests:
        module = attackTests[attack_name]
        if getattr(module, "running", True):
            print(f"⚠️ El ataque {attack_name} ya está en ejecución.")
            return
        module.running = True
    else:
        print(f"⚠️ El ataque {attack_name} no está cargado.")

def stopAttack(attack_name):
    """
    Detiene un ataque si está en ejecución.
    """
    if attack_name in attackTests:
        module = attackTests[attack_name]
        if not getattr(module, "running", False):
            print(f"⚠️ El ataque {attack_name} no estaba en ejecución.")
            return "Orden de modulo de ataque completada"
        module.running = False
    else:
        print(f"⚠️ El ataque {attack_name} no está cargado.")
        return "Orden de modulo de ataque no completada"
