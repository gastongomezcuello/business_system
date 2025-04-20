import base64
import json
import qrcode


def dict_to_base64(data_dict):
    json_data = json.dumps(data_dict)
    return base64.b64encode(json_data.encode()).decode()


def generate_qr(base64_string):
    url_completa = f"https://www.afip.gob.ar/fe/qr/?p={base64_string}"
    qr = qrcode.make(url_completa)
    return qr
