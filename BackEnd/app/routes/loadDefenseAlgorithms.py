from flask import Blueprint, jsonify, request
from app.loadDefenseAlgorithms import *

# Creamos un Blueprint para organizar mejor las rutas
loadDefenseAlgorithms_bp = Blueprint('loadDefenseAlgorithms', __name__)

# Enviar los nombres de los algoritmos de defensa
@loadDefenseAlgorithms_bp.route('/loadedNames', methods=['GET'])
def loadedNames():
    try:
        algorithmNames = getDefenseAlgorithmNames()
        return jsonify({"algorithms": algorithmNames}), 200
    except Exception as e:
        # Si ocurre un error, retornar el mensaje de error como JSON
        return jsonify({"error": str(e)}), 500
    
# Iniciar un módulo
@loadDefenseAlgorithms_bp.route('/startModule', methods=['POST'])
def startModuleRoute():
    try:
        data = request.get_json()
        if "algorithmName" not in data:
            return jsonify({"error": "Falta el parámetro 'algorithmName'"}), 400

        algorithmName = data["algorithmName"]
        result = startModule(algorithmName)
        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para detener un módulo
@loadDefenseAlgorithms_bp.route('/stopModule', methods=['POST'])
def stopModuleRoute():
    try:
        data = request.get_json()
        if "algorithmName" not in data:
            return jsonify({"error": "Falta el parámetro 'algorithmName'"}), 400

        algorithmName = data["algorithmName"]
        result = stopModule(algorithmName)
        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500