import midtransclient
import os

def create_payment(order):
    snap = midtransclient.Snap(
        is_production=os.getenv('MIDTRANS_IS_PRODUCTION') == 'True',
        server_key=os.getenv('MIDTRANS_SERVER_KEY')
    )
    
    param = {
        "transaction_details": {
            "order_id": f"VALENTINE-{order.id}",
            "gross_amount": int(order.total_price)
        },
        "enabled_payments": [
            "gopay", "shopeepay", "dana", "ovo",       # E-Wallet
            "linkaja", "other_qris",                     # QR Code
            "bca_va", "bni_va", "bri_va", "mandiri_va", # Transfer Bank
            "credit_card"                                 # Kartu Kredit/Visa
        ],
        "customer_details": {
            "first_name": order.user.username,
            "email": order.user.email,
            "phone": order.user.phone
        }
    }
    
    transaction = snap.create_transaction(param)
    return transaction['token']  # Token dikirim ke frontend