from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, Product
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    # Получаем числовой ID
    user_id = get_jwt_identity()
    data = request.get_json()

    if 'items' not in data or not data['items']:
        return jsonify({'error': 'Order items required'}), 400

    if 'address' not in data or 'phone' not in data:
        return jsonify({'error': 'Address and phone required'}), 400

    total = 0
    order_items = []

    for item in data['items']:
        product = Product.query.get(item['product_id'])

        if not product:
            return jsonify({'error': f'Product {item["product_id"]} not found'}), 404

        if product.stock < item['quantity']:
            return jsonify({
                'error': f'Not enough stock for product {product.name}',
                'product_id': product.id,
                'available_stock': product.stock
            }), 400

        item_price = product.price
        total += item_price * item['quantity']

        order_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': item_price
        })

    order = Order(
        user_id=user_id,
        total=total,
        address=data['address'],
        phone=data['phone'],
        notes=data.get('notes', ''),
        status='pending'
    )

    db.session.add(order)
    db.session.flush()

    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
        item['product'].stock -= item['quantity']

    db.session.commit()

    return jsonify({
        'message': 'Order created successfully',
        'order_id': order.id,
        'total': order.total
    }), 201

@orders_bp.route('/history', methods=['GET'])
@jwt_required()
def order_history():
    # Получаем числовой ID
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    return jsonify([order.to_dict() for order in orders]), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    # Получаем числовой ID
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    return jsonify(order.to_dict()), 200

@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    # Получаем числовой ID
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    data = request.get_json()
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400

    valid_statuses = ['pending', 'completed', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'}), 400

    if data['status'] == 'cancelled' and order.status != 'cancelled':
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity

    order.status = data['status']
    db.session.commit()

    return jsonify({
        'message': 'Order status updated',
        'order_id': order.id,
        'new_status': order.status
    }), 200