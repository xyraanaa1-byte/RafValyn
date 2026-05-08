# Urutan ini PENTING! Tabel yang dirujuk harus diimport duluan
from app.models.user import User
from app.models.product import Product      # ← products harus ada duluan
from app.models.product import CartItem     # ← baru CartItem
from app.models.review import Review        # ← review butuh user & product
from app.models.order import Order          # ← order butuh user
from app.models.order import OrderItem      # ← order_items butuh products & orders
from app.models.message import Message      # ← message butuh user
from app.models.chat import ChatRoom, ChatMessage, Notification
from app.models.journal import Journal, Schedule
from app.models.tourism import TourismSpot, TourismTicket