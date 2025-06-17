from flask import Blueprint, request, jsonify
from models import db, Product, Category
from flask_jwt_extended import jwt_required

products_bp = Blueprint('products', __name__)


@products_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_products():
    # Параметры фильтрации
    category_id = request.args.get('category_id')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    search = request.args.get('search')
    in_stock = request.args.get('in_stock')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    query = Product.query

    if category_id:
        query = query.filter_by(category_id=category_id)
    if min_price:
        query = query.filter(Product.price >= float(min_price))
    if max_price:
        query = query.filter(Product.price <= float(max_price))
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if in_stock and in_stock.lower() == 'true':
        query = query.filter(Product.stock > 0)

    sort_field = Product.id
    if sort_by == 'price':
        sort_field = Product.price
    elif sort_by == 'name':
        sort_field = Product.name
    elif sort_by == 'created_at':
        sort_field = Product.created_at

    if sort_order == 'asc':
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())

    page = request.args.get('page', 1, type=int)
    per_page = min(int(request.args.get('per_page', 20)), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    products = [p.to_dict() for p in paginated.items]

    return jsonify({
        'products': products,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page
    }), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200


@products_bp.route('/categories/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    return jsonify(category.to_dict()), 200


@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    products = Product.query.order_by(db.func.random()).limit(8).all()
    return jsonify([p.to_dict() for p in products]), 200