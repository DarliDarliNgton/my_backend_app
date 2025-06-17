from app import create_app
from models import db, User, Category, Product, Order, OrderItem
from datetime import datetime, timedelta
import random

app = create_app()


def seed_database():
    with app.app_context():
        print("🔄 Очистка базы данных...")
        db.drop_all()
        db.create_all()
        print("✅ База очищена и создана заново")

        # Создание пользователей
        print("👥 Создание пользователей...")
        admin = User(
            email="admin@shop.com",
            first_name="Admin",
            last_name="User",
            phone="+1234567890",
            is_admin=True,
            created_at=datetime.utcnow()
        )
        admin.set_password("admin123")

        customer1 = User(
            email="customer1@shop.com",
            first_name="John",
            last_name="Doe",
            phone="+1987654321",
            created_at=datetime.utcnow()
        )
        customer1.set_password("customer123")

        customer2 = User(
            email="customer2@shop.com",
            first_name="Jane",
            last_name="Smith",
            phone="+1122334455",
            created_at=datetime.utcnow()
        )
        customer2.set_password("customer123")

        db.session.add_all([admin, customer1, customer2])
        db.session.commit()
        print(f"✅ Создано {User.query.count()} пользователей")

        # Создание категорий
        print("📦 Создание категорий...")
        categories_data = [
            {"name": "Процессоры", "slug": "cpu", "description": "Центральные процессоры для настольных ПК и серверов"},
            {"name": "Видеокарты", "slug": "gpu",
             "description": "Графические процессоры для игр и профессиональной работы"},
            {"name": "Материнские платы", "slug": "motherboard", "description": "Основные платы для сборки ПК"},
            {"name": "Оперативная память", "slug": "ram", "description": "Модули оперативной памяти DDR4 и DDR5"},
            {"name": "SSD накопители", "slug": "ssd",
             "description": "Твердотельные накопители различных форм-факторов"},
            {"name": "Блоки питания", "slug": "psu", "description": "Источники питания для компьютерных систем"},
            {"name": "Корпуса", "slug": "cases", "description": "Корпуса для ПК различных размеров и дизайнов"},
            {"name": "Охлаждение", "slug": "cooling", "description": "Системы охлаждения для процессоров и корпусов"},
            {"name": "Мониторы", "slug": "monitors",
             "description": "Мониторы с различными диагоналями и характеристиками"},
            {"name": "Периферия", "slug": "peripherals",
             "description": "Клавиатуры, мыши, наушники и другие аксессуары"},
        ]

        categories = []
        for cat_data in categories_data:
            category = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"]
            )
            categories.append(category)
            db.session.add(category)

        db.session.commit()
        print(f"✅ Создано {Category.query.count()} категорий")

        # Создание товаров
        print("🛒 Создание товаров...")
        products_data = [
            {
                "name": "Intel Core i9-13900K",
                "description": "24 ядра (8P+16E), до 5.8 ГГц, LGA 1700",
                "price": 58990,
                "stock": 15,
                "category": "cpu",
                "specifications": {
                    "socket": "LGA 1700",
                    "cores": "24 (8P+16E)",
                    "threads": 32,
                    "base_clock": "3.0 ГГц",
                    "max_clock": "5.8 ГГц",
                    "tdp": "125 Вт",
                    "l3_cache": "36 МБ"
                }
            },
            {
                "name": "AMD Ryzen 9 7950X",
                "description": "16 ядер, 32 потока, до 5.7 ГГц, AM5",
                "price": 64990,
                "stock": 10,
                "category": "cpu",
                "specifications": {
                    "socket": "AM5",
                    "cores": 16,
                    "threads": 32,
                    "base_clock": "4.5 ГГц",
                    "max_clock": "5.7 ГГц",
                    "tdp": "170 Вт",
                    "l3_cache": "64 МБ"
                }
            },
            {
                "name": "NVIDIA GeForce RTX 4090",
                "description": "24 ГБ GDDR6X, 16384 ядер CUDA",
                "price": 189990,
                "stock": 5,
                "category": "gpu",
                "specifications": {
                    "memory": "24 ГБ GDDR6X",
                    "memory_bus": "384-bit",
                    "cuda_cores": 16384,
                    "base_clock": "2.23 ГГц",
                    "boost_clock": "2.52 ГГц",
                    "tbp": "450 Вт"
                }
            },
            {
                "name": "ASUS ROG Strix Z790-E",
                "description": "LGA 1700, DDR5, PCIe 5.0, Wi-Fi 6E",
                "price": 34990,
                "stock": 20,
                "category": "motherboard",
                "specifications": {
                    "socket": "LGA 1700",
                    "chipset": "Intel Z790",
                    "form_factor": "ATX",
                    "memory_slots": 4,
                    "max_memory": "128 ГБ DDR5",
                    "m2_slots": 4
                }
            },
            {
                "name": "Kingston Fury Beast 32GB DDR5",
                "description": "32GB (2x16GB) DDR5 6000MHz CL36",
                "price": 14990,
                "stock": 30,
                "category": "ram",
                "specifications": {
                    "type": "DDR5",
                    "capacity": "32 ГБ (2x16)",
                    "speed": "6000 МГц",
                    "latency": "CL36",
                    "voltage": "1.35 В"
                }
            },
            {
                "name": "Samsung 980 Pro 2TB",
                "description": "PCIe 4.0 NVMe SSD, скорость чтения до 7000 МБ/с",
                "price": 17990,
                "stock": 25,
                "category": "ssd",
                "specifications": {
                    "interface": "PCIe 4.0 x4",
                    "capacity": "2 ТБ",
                    "read_speed": "7000 МБ/с",
                    "write_speed": "5100 МБ/с",
                    "tbw": "1200 ТБ"
                }
            },
            {
                "name": "Be Quiet! Dark Power 13 1000W",
                "description": "Модульный блок питания 80+ Titanium",
                "price": 24990,
                "stock": 15,
                "category": "psu",
                "specifications": {
                    "wattage": "1000 Вт",
                    "efficiency": "80+ Titanium",
                    "modular": "Полностью модульный",
                    "connectors": "2x EPS, 6x PCIe"
                }
            },
            {
                "name": "NZXT H9 Flow",
                "description": "Корпус Mid-Tower с панорамным стеклом",
                "price": 15990,
                "stock": 18,
                "category": "cases",
                "specifications": {
                    "type": "Mid-Tower",
                    "motherboard": "ATX, Micro-ATX, Mini-ITX",
                    "fans": "3x 120mm предустановлено",
                    "radiator_support": "360mm"
                }
            },
            {
                "name": "Noctua NH-D15",
                "description": "Топовый башенный кулер для процессоров",
                "price": 8990,
                "stock": 22,
                "category": "cooling",
                "specifications": {
                    "type": "Воздушное",
                    "socket": "LGA1700, AM5, AM4",
                    "tpd": "250 Вт",
                    "noise": "24.6 дБ"
                }
            },
            {
                "name": "Samsung Odyssey G9",
                "description": "49-дюймовый изогнутый игровой монитор",
                "price": 89990,
                "stock": 8,
                "category": "monitors",
                "specifications": {
                    "size": "49 дюймов",
                    "resolution": "5120x1440",
                    "refresh_rate": "240 Гц",
                    "panel": "QLED"
                }
            }
        ]

        for prod_data in products_data:
            category = next((c for c in categories if c.slug == prod_data["category"]), None)
            if category:
                product = Product(
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    stock=prod_data["stock"],
                    category_id=category.id,
                    specifications=prod_data["specifications"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(product)

        db.session.commit()
        print(f"✅ Создано {Product.query.count()} товаров")

        # Создание заказов
        print("📦 Создание заказов...")
        customers = [customer1, customer2]
        products = Product.query.all()
        statuses = ['pending', 'completed', 'cancelled']

        for i in range(10):  # Создадим 10 заказов
            customer = random.choice(customers)
            order_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))

            order = Order(
                user_id=customer.id,
                total=0,
                address=f"ул. Примерная, д. {i + 1}, кв. {i + 10}",
                phone=customer.phone,
                status=random.choice(statuses),
                created_at=order_date,
                notes=f"Заказ №{i + 1} для {customer.first_name} {customer.last_name}"
            )
            db.session.add(order)
            db.session.flush()  # Получаем ID заказа

            # Добавляем товары в заказ
            order_items = []
            order_total = 0
            num_items = random.randint(1, 5)  # От 1 до 5 товаров в заказе

            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)

                # Проверяем, есть ли достаточно товара на складе
                if product.stock < quantity:
                    quantity = product.stock

                if quantity > 0:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity,
                        price=product.price
                    )
                    order_total += product.price * quantity
                    db.session.add(order_item)
                    order_items.append(order_item)

                    # Уменьшаем количество товара на складе
                    product.stock -= quantity

            order.total = order_total
            db.session.commit()

        print(f"✅ Создано {Order.query.count()} заказов")
        print("🎉 База данных успешно заполнена тестовыми данными!")


if __name__ == '__main__':
    seed_database()