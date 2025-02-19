from flask import Blueprint, jsonify
from app.loadDefenseAlgorithms import getDefenseAlgorithmNames

# Creamos un Blueprint para organizar mejor las rutas
loadDefenseAlgorithms_bp = Blueprint('loadDefenseAlgorithms', __name__)

# Ruta para devolver los nombres de los algoritmos de defensa
@loadDefenseAlgorithms_bp.route('/loadedNames', methods=['GET'])
def loadedNames():
    try:
        algorithmNames = getDefenseAlgorithmNames()
        return jsonify({"algorithms": algorithmNames}), 200
    except Exception as e:
        # Si ocurre un error, retornar el mensaje de error como JSON
        return jsonify({"error": str(e)}), 500
