from flask import Blueprint, jsonify, request
from app.loadAttackTests import *

# Creamos un Blueprint para organizar mejor las rutas
loadAttackTests_bp = Blueprint('loadAttackTests', __name__)

# Encender o parar un ataque
@loadAttackTests_bp.route('/startOrStop', methods=['POST'])
def startOrStopRoute():
    try:
        data = request.get_json()

        if not data or 'attackName' not in data or 'isActive' not in data:
            return jsonify({"error": "Faltan parámetros"}), 400

        attackName = data['attackName']
        isActive = data['isActive']

        if isActive:
            result = startAttack(attackName)
            return jsonify({"message": result}), 200
        else:
            result = stopAttack(attackName)
            return jsonify({"message": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 