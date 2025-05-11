from django.conf import settings
from jinja2 import Template
from arca.qr import generate_qr
from io import BytesIO
import base64
import subprocess

# from weasyprint import HTML
import os


def invoice_pdf(invoice):

    business_data = {
        "business_name": "Empresa imaginaria S.A.",  # Nombre / Razon social
        "address": "Calle falsa 123",  # Direccion
        "tax_id": 12345678912,  # CUIL/CUIT
        "gross_income_id": 12345432,  # Ingresos brutos
        "start_date": "25/10/2017",  # Fecha inicio de actividades
        "vat_condition": "Responsable inscripto",  # Condicion frente al IVA
    }

    # Datos del comprobante
    bill = {
        "number": "000000032",  # Numero de comprobante
        "point_of_sale": "0001",  # Numero del punto de venta
        "date": "25/10/2017",  # Fecha de emision del comprobante
        "since": "25/10/2017",  # Fecha de comienzo
        "until": "25/10/2017",  # Fecha de fin
        "expiration": "25/10/2017",  # Fecha de expiracion del comprobante
        "type": "B",  # Tipo de comprobante
        "code": "6",  # Codigo de tipo del comprobante
        "concept": "Productos",  # Concepto del comprobante (Productos / Servicios / Productos y servicios)
        "CAE": 12345678912345,  # CAE
        "CAE_expiration": "05/11/2017",  # Fecha de expiracion del CAE
    }

    # Items del comprobante
    items = [
        {
            "code": "321",  # Codigo
            "name": "Cafe Americano",  # Nombre
            "quantity": "1,00",  # Cantidad
            "measurement_unit": "Unidad",  # Unidad de medida
            "price": "1500,00",  # Precio
            "tax_percent": "21%",  # Precio
            "percent_subsidized": "0,00",  # Precio subsidiado
            "impost_subsidized": "0,00",  # Impuestos subsidiado
            "subtotal": "1500,00",  # Subtotal
        }
    ]

    # Datos de a quien va emitido del comprobante
    billing_data = {
        "tax_id": 12345678912,  # Document/CUIT/CUIL
        "name": "Pepe perez",  # Nombre / Razon social
        "vat_condition": "Consumidor final",  # Condicion frente al iva
        "address": "Calle falsa 123",  # Direccion
        "payment_method": "Efectivo",  # Forma de pago
    }

    # Resumen
    overall = {
        "subtotal": "150,00",  # Subtotal
        "impost_tax": "0,00",  # Tributos
        "total": "150,00",  # Total
    }
    # store = invoice.store
    # order = invoice.order
    # client = invoice.order.client
    # raw_items = invoice.order.items.all()

    # business_data = {
    #     "business_name": store.name,
    #     "address": store.address,
    #     "tax_id": store.cuit,
    #     "gross_income_id": store.gross_income_id,
    #     "start_date": store.start_date.strftime("%d/%m/%Y"),
    #     "vat_condition": store.get_vat_condition_display(),
    # }

    # bill = {
    #     "number": invoice.document_number.formatted_document_number(),
    #     "point_of_sale": store.store_number.formatted_store_number(),
    #     "date": invoice.date.strftime("%d/%m/%Y"),
    #     "since": "",
    #     "until": "",
    #     "expiration": "",
    #     "type": invoice.get_document_letter_display(),
    #     "code": invoice.document_letter,
    #     "concept": "Productos",
    #     "CAE": invoice.json_arca_request["codAut"],
    #     "CAE_expiration": invoice.json_arca_request["vtoCAE"].strftime("%d/%m/%Y"),
    # }

    # # Items del comprobante
    # items = []
    # for item in raw_items:
    #     items.append(
    #         {
    #             "code": str(item.product.code),
    #             "name": item.product.name,
    #             "quantity": f"{item.quantity:.2f}".replace(".", ","),
    #             "measurement_unit": item.product.unit or "Unidad",
    #             "price": f"{item.product.price:.2f}".replace(".", ","),
    #             "tax_percent": f"{item.product.get_vat_value()}%",
    #             "percent_subsidized": "0,00",
    #             "impost_subsidized": "0,00",
    #             "subtotal": f"{item.subtotal():.2f}".replace(".", ","),
    #         }
    #     )

    # # Datos de a quien va emitido del comprobante
    # billing_data = {
    #     "tax_id": client.id_data.number,
    #     "name": client.name,
    #     "vat_condition": client.get_vat_condition_display(),
    #     "address": client.address,
    #     "payment_method": "Cuenta corriente",
    # }

    # # Resumen
    # overall = {
    #     "subtotal": f"{order.calculate_subtotal():.2f}".replace(".", ","),
    #     "impost_tax": f"{order.vat_total():.2f}".replace(".", ","),
    #     "total": f"{order.calculate_total():.2f}".replace(".", ","),
    # }

    # qr = generate_qr(invoice.b64_fiscal_data)

    qr_falso = generate_qr("jakdhjkasdhkasdh4324")

    buffered = BytesIO()

    qr_falso.save(buffered, format="PNG")

    buffered.seek(0)

    qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    html_path = f"{settings.BASE_DIR}/templates/arca_pdf.html"

    html = open(html_path, encoding="utf-8").read()

    template = Template(html)

    rendered_html = template.render(
        business_data=business_data,
        bill=bill,
        items=items,
        billing_data=billing_data,
        overall=overall,
        qr_code_image=qr_base64,
    )

    # pdf_name = (
    #     store.store_number.formatted_store_number()
    #     + invoice.document_letter
    #     + invoice.document_number.formatted_document_number()
    # )

    pdf_name = "test_invoice"
    os.makedirs(f"{settings.BASE_DIR}/invoices", exist_ok=True)
    debug_path = os.path.join(settings.BASE_DIR, "invoices", "debug_qr.html")
    pdf_path = f"{settings.BASE_DIR}/invoices/{pdf_name}.pdf"
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    try:
        subprocess.run(
            [
                "chromium",
                "--headless",
                "--disable-gpu",
                f"--print-to-pdf={pdf_path}",
                f"file://{os.path.abspath(debug_path)}",
            ],
            check=True,
        )
        os.remove(debug_path)
    except subprocess.CalledProcessError as e:
        print("Error al generar PDF:", e)
        return None

    return pdf_path
