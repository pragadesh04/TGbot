import qrcode
import io
import base64
from PIL import Image


def generate_qr_code(upi_id: str, amount: float = 0) -> str:
    """
    Generate a QR code for UPI payment.
    Returns base64 encoded image.
    """
    # UPI Payment URL format
    if amount > 0:
        upi_url = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"
    else:
        upi_url = f"upi://pay?pa={upi_id}&cu=INR"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return img_str
