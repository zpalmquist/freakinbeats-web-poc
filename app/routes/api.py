from flask import Blueprint, jsonify, current_app
from app.services.inventory_service import InventoryService

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/data')
def get_data():
    service = InventoryService(
        current_app.config['BASE_DIR'],
        current_app.config['CSV_FILE_PATTERN']
    )
    data = service.get_all_items()
    return jsonify(data)

