from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.chat import Notification
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    # Ambil user pertama yang bukan admin
    user = User.query.filter_by(is_admin=False).first()
    if not user:
        print('Tidak ada user! Daftar dulu ya.')
        exit()

    # Ambil semua produk
    products = Product.query.filter_by(is_active=True).all()
    if not products:
        print('Tidak ada produk! Jalankan seed_products.py dulu.')
        exit()

    # Hapus pesanan lama
    OrderItem.query.delete()
    Order.query.delete()
    db.session.commit()

    # Data pesanan dummy
    orders_data = [
        # 1. Belum dibayar
        {
            'status': 'waiting',
            'payment_status': 'pending',
            'payment_method': 'gopay',
            'is_cod': False,
            'address': 'Jl. Mawar No. 12, Semarang, Jawa Tengah',
            'delivery_lat': -6.9667,
            'delivery_lng': 110.4167,
            'courier_lat': None,
            'courier_lng': None,
            'days_ago': 0,
            'notes': 'Tolong dikemas dengan rapi ya',
            'products': [
                (random.choice(products), 2),
            ]
        },
        # 2. Sudah dibayar, menunggu dikemas
        {
            'status': 'waiting',
            'payment_status': 'paid',
            'payment_method': 'dana',
            'is_cod': False,
            'address': 'Jl. Melati No. 5, Semarang, Jawa Tengah',
            'delivery_lat': -6.9833,
            'delivery_lng': 110.4000,
            'courier_lat': None,
            'courier_lng': None,
            'days_ago': 1,
            'notes': '',
            'products': [
                (random.choice(products), 1),
                (random.choice(products), 1),
            ]
        },
        # 3. Sedang dikemas
        {
            'status': 'packed',
            'payment_status': 'paid',
            'payment_method': 'ovo',
            'is_cod': False,
            'address': 'Jl. Anggrek No. 8, Semarang, Jawa Tengah',
            'delivery_lat': -7.0000,
            'delivery_lng': 110.4200,
            'courier_lat': None,
            'courier_lng': None,
            'days_ago': 2,
            'notes': 'Titip di satpam kalau tidak ada di rumah',
            'products': [
                (random.choice(products), 1),
            ]
        },
        # 4. Sedang dikirim (bisa dilacak)
        {
            'status': 'on_the_way',
            'payment_status': 'paid',
            'payment_method': 'qris',
            'is_cod': False,
            'address': 'Jl. Kenanga No. 3, Semarang, Jawa Tengah',
            'delivery_lat': -6.9934,
            'delivery_lng': 110.4282,
            'courier_lat': -6.9800,
            'courier_lng': 110.4150,
            'days_ago': 3,
            'notes': '',
            'products': [
                (random.choice(products), 2),
                (random.choice(products), 1),
            ]
        },
        # 5. Sedang dikirim COD
        {
            'status': 'on_the_way',
            'payment_status': 'pending',
            'payment_method': 'cod',
            'is_cod': True,
            'address': 'Jl. Dahlia No. 15, Semarang, Jawa Tengah',
            'delivery_lat': -6.9750,
            'delivery_lng': 110.4050,
            'courier_lat': -6.9700,
            'courier_lng': 110.4000,
            'days_ago': 2,
            'notes': 'COD, siapkan uang pas',
            'products': [
                (random.choice(products), 1),
            ]
        },
        # 6. Sudah terkirim, belum diulas
        {
            'status': 'delivered',
            'payment_status': 'paid',
            'payment_method': 'bca',
            'is_cod': False,
            'address': 'Jl. Tulip No. 7, Semarang, Jawa Tengah',
            'delivery_lat': -6.9600,
            'delivery_lng': 110.4300,
            'courier_lat': -6.9600,
            'courier_lng': 110.4300,
            'days_ago': 5,
            'notes': '',
            'products': [
                (random.choice(products), 1),
                (random.choice(products), 2),
            ]
        },
        # 7. Sudah terkirim, belum diulas 2
        {
            'status': 'delivered',
            'payment_status': 'paid',
            'payment_method': 'shopeepay',
            'is_cod': False,
            'address': 'Jl. Cempaka No. 20, Semarang, Jawa Tengah',
            'delivery_lat': -6.9850,
            'delivery_lng': 110.3950,
            'courier_lat': -6.9850,
            'courier_lng': 110.3950,
            'days_ago': 7,
            'notes': '',
            'products': [
                (random.choice(products), 3),
            ]
        },
        # 8. Sudah diulas
        {
            'status': 'reviewed',
            'payment_status': 'paid',
            'payment_method': 'mandiri',
            'is_cod': False,
            'address': 'Jl. Bougenville No. 9, Semarang, Jawa Tengah',
            'delivery_lat': -6.9700,
            'delivery_lng': 110.4100,
            'courier_lat': -6.9700,
            'courier_lng': 110.4100,
            'days_ago': 10,
            'notes': '',
            'products': [
                (random.choice(products), 1),
            ]
        },
        # 9. COD delivered
        {
            'status': 'delivered',
            'payment_status': 'paid',
            'payment_method': 'cod',
            'is_cod': True,
            'address': 'Jl. Kamboja No. 4, Semarang, Jawa Tengah',
            'delivery_lat': -6.9900,
            'delivery_lng': 110.4400,
            'courier_lat': -6.9900,
            'courier_lng': 110.4400,
            'days_ago': 8,
            'notes': 'Bayar COD sudah lunas',
            'products': [
                (random.choice(products), 2),
                (random.choice(products), 1),
            ]
        },
        # 10. Baru masuk, belum dibayar
        {
            'status': 'waiting',
            'payment_status': 'pending',
            'payment_method': 'linkaja',
            'is_cod': False,
            'address': 'Jl. Teratai No. 11, Semarang, Jawa Tengah',
            'delivery_lat': -6.9650,
            'delivery_lng': 110.4250,
            'courier_lat': None,
            'courier_lng': None,
            'days_ago': 0,
            'notes': 'Minta dibungkus kado ya',
            'products': [
                (random.choice(products), 1),
            ]
        },
    ]

    created_orders = []
    for data in orders_data:
        # Hitung total
        total = sum(float(p.final_price) * qty for p, qty in data['products'])

        order = Order(
            user_id=user.id,
            total_price=total,
            payment_method=data['payment_method'],
            payment_status=data['payment_status'],
            is_cod=data['is_cod'],
            delivery_address=data['address'],
            delivery_lat=data['delivery_lat'],
            delivery_lng=data['delivery_lng'],
            courier_lat=data['courier_lat'],
            courier_lng=data['courier_lng'],
            shipping_status=data['status'],
            notes=data['notes'],
            created_at=datetime.utcnow() - timedelta(days=data['days_ago'])
        )
        db.session.add(order)
        db.session.flush()

        for product, qty in data['products']:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price=product.final_price
            )
            db.session.add(item)
            product.sold_count += qty

        created_orders.append(order)

        # Buat notifikasi untuk setiap pesanan
        notif_messages = {
            'waiting': ('⏳ Pesanan Menunggu', 'Pesanan baru masuk, menunggu konfirmasi'),
            'packed': ('📦 Pesanan Dikemas', 'Pesanan sedang dikemas oleh penjual'),
            'on_the_way': ('🚚 Pesanan Dikirim', 'Pesanan dalam perjalanan ke alamatmu'),
            'delivered': ('✅ Pesanan Selesai', 'Pesanan telah sampai! Jangan lupa beri ulasan'),
            'reviewed': ('⭐ Ulasan Diterima', 'Terima kasih atas ulasanmu!'),
        }

        title, msg = notif_messages.get(data['status'], ('📦 Update Pesanan', 'Status pesanan diperbarui'))
        notif = Notification(
            user_id=user.id,
            type='order',
            title=title,
            message=msg,
            link=f'/orders/{order.id}',
            is_read=data['days_ago'] > 2
        )
        db.session.add(notif)

    db.session.commit()
    print(f'✅ Berhasil membuat {len(created_orders)} pesanan dummy!')
    print('Pesanan yang dibuat:')
    for i, order in enumerate(created_orders):
        print(f'  #{order.id} - Status: {order.shipping_status} - Total: Rp {int(order.total_price):,}')