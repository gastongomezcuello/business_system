from zeep import Client
from zeep.transports import Transport
from requests import Session
from datetime import datetime


def generate_invoice(
    auth: dict,
    header: dict,
    receptor: dict,
    amounts: dict,
    tributos: list = None,
    ivas: list = None,
):

    if "CbteFch" not in receptor or not receptor["CbteFch"]:
        receptor["CbteFch"] = datetime.now().strftime("%Y%m%d")

    wsdl_url = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
    session = Session()
    transport = Transport(session=session)
    client = Client(wsdl=wsdl_url, transport=transport)

    detalle = {**receptor, **amounts}

    detalle["MonId"] = "PES"
    detalle["MonCotiz"] = 1

    if tributos:
        detalle["Tributos"] = {"Tributo": tributos}

    if ivas:
        detalle["Iva"] = {"AlicIva": ivas}

    invoice_data = {
        "FeCabReq": {
            "CantReg": 1,
            "PtoVta": header["PtoVta"],
            "CbteTipo": header["CbteTipo"],
        },
        "FeDetReq": {"FECAEDetRequest": [detalle]},
    }

    try:
        response = client.service.FECAESolicitar(Auth=auth, FeCAEReq=invoice_data)
        print(response)
        return response
    except Exception as e:
        return {"error": str(e)}


def parse_arca_response(xml_string):
    ns = {
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",
        "afip": "http://ar.gov.afip.dif.FEV1/",
    }
    root = ET.fromstring(xml_string)

    result = root.find(".//afip:FECAESolicitarResult", ns)
    cab = result.find("afip:FeCabResp", ns)
    det = result.find(".//afip:FECAEDetResponse", ns)

    return {
        "cuit": int(cab.find("afip:Cuit", ns).text),
        "ptoVta": int(cab.find("afip:PtoVta", ns).text),
        "tipoCmp": int(cab.find("afip:CbteTipo", ns).text),
        "fecha": det.find("afip:CbteFch", ns).text,
        "nroCmp": int(det.find("afip:CbteDesde", ns).text),
        "tipoDocRec": int(det.find("afip:DocTipo", ns).text),
        "nroDocRec": int(det.find("afip:DocNro", ns).text),
        "codAut": int(det.find("afip:CAE", ns).text),
        "vtoCAE": det.find("afip:CAEFchVto", ns).text,
    }


def response_to_arca_json(data, total):

    arca_data = {
        "ver": 1,
        "fecha": f"{data['fecha'][:4]}-{data['fecha'][4:6]}-{data['fecha'][6:]}",
        "cuit": data["cuit"],
        "ptoVta": data["ptoVta"],
        "tipoCmp": data["tipoCmp"],
        "nroCmp": data["nroCmp"],
        "importe": float(total),
        "moneda": "PES",
        "ctz": 1,
        "tipoDocRec": data["tipoDocRec"],
        "nroDocRec": data["nroDocRec"],
        "tipoCodAut": "E",
        "codAut": data["codAut"],
    }

    return arca_data
