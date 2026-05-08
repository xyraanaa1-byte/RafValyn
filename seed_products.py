from app import create_app, db
from app.models.product import Product
from datetime import datetime

app = create_app()

products = [
    # ===== BONEKA =====
    {'name': 'Boneka Beruang Peluk XL', 'category': 'boneka', 'price': 185000, 'stock': 50, 'description': 'Boneka beruang lembut ukuran XL 60cm, cocok untuk hadiah valentine. Bahan premium super soft, aman untuk semua usia.', 'sold_count': 234, 'is_cod': True, 'weight': 0.8},
    {'name': 'Boneka Kelinci Cantik Pink', 'category': 'boneka', 'price': 125000, 'stock': 30, 'description': 'Boneka kelinci lucu warna pink dengan pita cantik. Ukuran 40cm, bahan fleece lembut.', 'sold_count': 156, 'is_cod': True, 'weight': 0.5},
    {'name': 'Boneka Couple Bear Set', 'category': 'boneka', 'price': 245000, 'stock': 25, 'description': 'Set 2 boneka beruang couple, cocok untuk pasangan. Dilengkapi baju bertuliskan "I Love You".', 'sold_count': 89, 'is_cod': True, 'weight': 1.0},
    {'name': 'Boneka Panda Jumbo 80cm', 'category': 'boneka', 'price': 320000, 'stock': 15, 'description': 'Boneka panda raksasa 80cm, bahan premium imported. Sangat lembut dan menggemaskan.', 'sold_count': 45, 'is_cod': False, 'weight': 1.5},
    {'name': 'Boneka Kucing Aesthetic', 'category': 'boneka', 'price': 95000, 'stock': 40, 'description': 'Boneka kucing aesthetic dengan ekspresi lucu. Ukuran 30cm, cocok jadi dekorasi kamar.', 'sold_count': 312, 'is_cod': True, 'weight': 0.4},

    # ===== COKLAT =====
    {'name': 'Coklat Ferrero Rocher 16pcs', 'category': 'coklat', 'price': 145000, 'stock': 60, 'description': 'Coklat Ferrero Rocher original 16 pcs dalam kotak cantik. Cocok untuk hadiah valentine spesial.', 'sold_count': 445, 'is_cod': True, 'weight': 0.3},
    {'name': 'Hamper Coklat Premium Box', 'category': 'coklat', 'price': 275000, 'stock': 20, 'description': 'Hamper coklat premium berisi berbagai pilihan coklat impor dalam kotak mewah bertema valentine.', 'sold_count': 123, 'is_cod': True, 'weight': 0.7},
    {'name': 'Coklat Godiva Assorted', 'category': 'coklat', 'price': 385000, 'stock': 12, 'description': 'Coklat Godiva assorted 18 pcs. Pilihan rasa beragam, kemasan elegan cocok untuk hadiah.', 'sold_count': 67, 'is_cod': False, 'weight': 0.4},
    {'name': 'Coklat Batang Custom Nama', 'category': 'coklat', 'price': 85000, 'stock': 100, 'description': 'Coklat batang custom dengan nama kamu dan pasangan. Bisa request desain dan tulisan.', 'sold_count': 678, 'is_cod': True, 'weight': 0.2},
    {'name': 'Dark Chocolate Truffles Box', 'category': 'coklat', 'price': 195000, 'stock': 35, 'description': 'Dark chocolate truffles handmade 12 pcs. Dibuat fresh setiap hari, tanpa pengawet.', 'sold_count': 234, 'is_cod': True, 'weight': 0.3},

    # ===== BUNGA =====
    {'name': 'Buket Mawar Merah 12 Tangkai', 'category': 'bunga', 'price': 225000, 'stock': 30, 'description': 'Buket mawar merah segar 12 tangkai dengan dekorasi cantik. Dikirim fresh dari kebun.', 'sold_count': 567, 'is_cod': True, 'weight': 0.5},
    {'name': 'Buket Tulip Mix Warna', 'category': 'bunga', 'price': 285000, 'stock': 20, 'description': 'Buket tulip import mix warna 10 tangkai. Elegan dan romantis untuk valentine.', 'sold_count': 234, 'is_cod': True, 'weight': 0.6},
    {'name': 'Flower Box Mawar Premium', 'category': 'bunga', 'price': 395000, 'stock': 15, 'description': 'Box bunga mawar premium berisi 20 tangkai mawar dalam kotak eksklusif bertema valentine.', 'sold_count': 89, 'is_cod': False, 'weight': 0.8},
    {'name': 'Buket Bunga Artificial Abadi', 'category': 'bunga', 'price': 165000, 'stock': 50, 'description': 'Buket bunga artificial yang tidak layu. Bisa disimpan selamanya sebagai kenangan valentine.', 'sold_count': 345, 'is_cod': True, 'weight': 0.4},
    {'name': 'Mini Flower Pot Valentine', 'category': 'bunga', 'price': 115000, 'stock': 40, 'description': 'Pot bunga mini bertema valentine dengan bunga succulent cantik. Bisa ditaruh di meja.', 'sold_count': 212, 'is_cod': True, 'weight': 0.5},

    # ===== PERHIASAN =====
    {'name': 'Gelang Couple Silver', 'category': 'perhiasan', 'price': 185000, 'stock': 25, 'description': 'Gelang couple bahan silver 925 dengan ukiran nama. Tahan karat dan tidak mudah pudar.', 'sold_count': 178, 'is_cod': False, 'weight': 0.1},
    {'name': 'Kalung Love Pendant Gold', 'category': 'perhiasan', 'price': 245000, 'stock': 20, 'description': 'Kalung rantai gold dengan liontin hati. Bahan stainless steel anti karat, cocok untuk hadiah.', 'sold_count': 134, 'is_cod': False, 'weight': 0.1},
    {'name': 'Cincin Couple Titanium', 'category': 'perhiasan', 'price': 325000, 'stock': 15, 'description': 'Cincin couple bahan titanium premium. Bisa custom ukiran nama dan tanggal.', 'sold_count': 56, 'is_cod': False, 'weight': 0.1},
    {'name': 'Anting Crystal Heart', 'category': 'perhiasan', 'price': 125000, 'stock': 30, 'description': 'Anting berbentuk hati dengan kristal swarovski. Cocok untuk tampilan romantis valentine.', 'sold_count': 223, 'is_cod': True, 'weight': 0.05},
    {'name': 'Gelang Charm Love Bracelet', 'category': 'perhiasan', 'price': 195000, 'stock': 22, 'description': 'Gelang charm dengan berbagai liontin cinta. Bahan sterling silver, dilengkapi kotak hadiah.', 'sold_count': 145, 'is_cod': False, 'weight': 0.1},

    # ===== PARFUM =====
    {'name': 'Parfum Rose Garden 50ml', 'category': 'parfum', 'price': 285000, 'stock': 30, 'description': 'Parfum dengan aroma mawar yang romantis. Tahan lama hingga 8 jam, cocok untuk kencan.', 'sold_count': 234, 'is_cod': True, 'weight': 0.2},
    {'name': 'Body Mist Couple Set', 'category': 'parfum', 'price': 195000, 'stock': 25, 'description': 'Set body mist couple 2 botol 150ml. Aroma saling melengkapi untuk him & her.', 'sold_count': 167, 'is_cod': True, 'weight': 0.4},
    {'name': 'Parfum Vanilla Love EDP', 'category': 'parfum', 'price': 345000, 'stock': 18, 'description': 'Eau de parfum aroma vanilla yang hangat dan romantis. Import dari Prancis, 50ml.', 'sold_count': 89, 'is_cod': False, 'weight': 0.2},
    {'name': 'Reed Diffuser Romantic', 'category': 'parfum', 'price': 145000, 'stock': 40, 'description': 'Reed diffuser aroma floral romantic untuk ruangan. Tahan hingga 1 bulan, tampilan elegan.', 'sold_count': 312, 'is_cod': True, 'weight': 0.3},
    {'name': 'Perfume Oil Musk Rose', 'category': 'parfum', 'price': 125000, 'stock': 35, 'description': 'Perfume oil musk rose tanpa alkohol. Tahan lama seharian, cocok untuk kulit sensitif.', 'sold_count': 198, 'is_cod': True, 'weight': 0.1},

    # ===== KARTU =====
    {'name': 'Kartu Valentine Handmade', 'category': 'kartu', 'price': 35000, 'stock': 100, 'description': 'Kartu ucapan valentine handmade dengan desain cantik. Bisa request tulisan custom.', 'sold_count': 892, 'is_cod': True, 'weight': 0.05},
    {'name': 'Pop Up Card 3D Heart', 'category': 'kartu', 'price': 55000, 'stock': 75, 'description': 'Kartu ucapan pop up 3D berbentuk hati. Saat dibuka akan muncul bunga 3D yang cantik.', 'sold_count': 456, 'is_cod': True, 'weight': 0.1},
    {'name': 'E-Card Digital Custom', 'category': 'kartu', 'price': 25000, 'stock': 999, 'description': 'Kartu ucapan digital custom desain. Dikirim via email/WhatsApp dalam 1 jam.', 'sold_count': 1234, 'is_cod': False, 'weight': 0.0},
    {'name': 'Kartu Foto Polaroid Set', 'category': 'kartu', 'price': 75000, 'stock': 60, 'description': 'Set 6 kartu foto polaroid custom dengan foto kamu dan pasangan. Print HD quality.', 'sold_count': 345, 'is_cod': True, 'weight': 0.1},
    {'name': 'Love Letter Box Premium', 'category': 'kartu', 'price': 95000, 'stock': 40, 'description': 'Kotak surat cinta premium berisi 5 lembar surat dengan amplop cantik bertema valentine.', 'sold_count': 234, 'is_cod': True, 'weight': 0.2},

    # ===== PAKET =====
    {'name': 'Paket Valentine Komplit', 'category': 'paket', 'price': 485000, 'stock': 20, 'description': 'Paket lengkap: buket mawar + coklat + boneka + kartu ucapan. Dikemas dalam box premium.', 'sold_count': 123, 'is_cod': True, 'weight': 2.0},
    {'name': 'Hamper Valentine Mewah', 'category': 'paket', 'price': 685000, 'stock': 15, 'description': 'Hamper valentine super mewah: parfum + perhiasan + coklat premium + buket bunga.', 'sold_count': 45, 'is_cod': False, 'weight': 2.5},
    {'name': 'Paket Couple Sweet', 'category': 'paket', 'price': 325000, 'stock': 25, 'description': 'Paket couple: gelang couple + coklat + kartu custom. Cocok untuk hadiah anniversary.', 'sold_count': 89, 'is_cod': True, 'weight': 0.8},
    {'name': 'Gift Box Mini Valentine', 'category': 'paket', 'price': 185000, 'stock': 35, 'description': 'Gift box mini berisi coklat + kartu + boneka kecil. Cocok untuk budget terbatas.', 'sold_count': 234, 'is_cod': True, 'weight': 0.6},
    {'name': 'Paket Surprise Delivery', 'category': 'paket', 'price': 395000, 'stock': 18, 'description': 'Paket surprise delivery langsung ke alamat pasangan. Isi kejutan pilihan kamu sendiri.', 'sold_count': 67, 'is_cod': False, 'weight': 1.5},
]

with app.app_context():
    # Hapus produk lama kalau ada
    Product.query.delete()
    db.session.commit()

    for p in products:
        product = Product(
            name=p['name'],
            category=p['category'],
            price=p['price'],
            stock=p['stock'],
            description=p['description'],
            sold_count=p['sold_count'],
            is_cod=p['is_cod'],
            weight=p['weight'],
            is_active=True
        )
        db.session.add(product)

    db.session.commit()
    print(f'✅ Berhasil menambahkan {len(products)} produk!')