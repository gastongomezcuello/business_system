import os
import subprocess
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


ARCA_DIR = os.path.join(os.path.dirname(__file__), "response")
TICKET_PATH = os.path.join(ARCA_DIR, "loginTicketResponse.xml")


def is_ticket_valid(path=TICKET_PATH):
    if not os.path.exists(path):
        return False
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        expiration = root.findtext("header/expirationTime")
        dt_exp = datetime.fromisoformat(expiration)
        return dt_exp > datetime.utcnow()
    except Exception:
        return False


def generate_tra(service, out_file):
    import pytz

    dt_now = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
    gen_time = dt_now - timedelta(minutes=10)
    exp_time = dt_now + timedelta(minutes=10)

    root = ET.Element("loginTicketRequest")
    header = ET.SubElement(root, "header")
    ET.SubElement(header, "uniqueId").text = str(int(dt_now.timestamp()))
    ET.SubElement(header, "generationTime").text = gen_time.isoformat()
    ET.SubElement(header, "expirationTime").text = exp_time.isoformat()
    ET.SubElement(root, "service").text = service

    tree = ET.ElementTree(root)
    tree.write(out_file, encoding="utf-8", xml_declaration=True)


def sign_tra(cert_path, key_path, tra_path, cms_der_path):
    subprocess.run(
        [
            "openssl",
            "cms",
            "-sign",
            "-in",
            tra_path,
            "-signer",
            cert_path,
            "-inkey",
            key_path,
            "-nodetach",
            "-outform",
            "DER",
            "-out",
            cms_der_path,
        ],
        check=True,
    )


def code_base64(input_path, output_path):
    subprocess.run(
        ["openssl", "base64", "-in", input_path, "-out", output_path, "-e"], check=True
    )


def call_wsaa(wsdl_url, cms_b64_path):
    import zeep

    with open(cms_b64_path, "r") as f:
        cms = f.read()

    client = zeep.Client(wsdl=wsdl_url)
    response = client.service.loginCms(cms)

    with open(TICKET_PATH, "w") as f:
        f.write(response)

    return response


def take_token_sign(xml_path=TICKET_PATH):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    token = root.findtext("credentials/token")
    sign = root.findtext("credentials/sign")
    return token, sign


def get_token_sign(cert_path, key_path, service, wsdl_url):
    os.makedirs(ARCA_DIR, exist_ok=True)

    if is_ticket_valid():
        return take_token_sign()

    base_name = os.path.join(
        ARCA_DIR, f"TRA_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )
    tra_path = f"{base_name}.xml"
    cms_der_path = f"{base_name}.cms"
    cms_b64_path = f"{base_name}.b64"

    try:
        generate_tra(service, tra_path)
        sign_tra(cert_path, key_path, tra_path, cms_der_path)
        code_base64(cms_der_path, cms_b64_path)
        call_wsaa(wsdl_url, cms_b64_path)
        return take_token_sign()
    finally:
        for path in (tra_path, cms_der_path, cms_b64_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar {path}: {e}")
