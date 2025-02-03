from flask import Blueprint, jsonify

# Crear el Blueprint
arpSpoofing_bp = Blueprint('arpSpoofing', __name__)

# Ruta para detectar ARP Spoofing
@arpSpoofing_bp.route('/defense/arpSpoofing', methods=['GET'])
def arpSpoofingDetect():
    # Lógica de detección de ARP Spoofing aún no implementada, pero por ahora solo devolvemos un mensaje.
    return jsonify({
        "status": "success",
        "message": "Detectando ARP Spoofing. Funcionalidad aún en desarrollo."
    }), 200
