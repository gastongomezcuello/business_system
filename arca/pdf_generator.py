from django.conf import settings
from jinja2 import Template
from arca.qr import generate_qr

import os
import pdfkit


def invoice_pdf(invoice):

    store = invoice.store
    order = invoice.order
    client = invoice.order.client
    raw_items = invoice.order.items.all()

    business_data = {
        "business_name": store.name,
        "address": store.address,
        "tax_id": store.cuit,
        "gross_income_id": store.gross_income_id,
        "start_date": store.start_date.strftime("%d/%m/%Y"),
        "vat_condition": store.get_vat_condition_display(),
    }

    bill = {
        "number": invoice.document_number.formatted_document_number(),
        "point_of_sale": store.store_number.formatted_store_number(),
        "date": invoice.date.strftime("%d/%m/%Y"),
        "since": "",
        "until": "",
        "expiration": "",
        "type": invoice.get_document_letter_display(),
        "code": invoice.document_letter,
        "concept": "Productos",
        "CAE": invoice.json_arca_request["codAut"],
        "CAE_expiration": invoice.json_arca_request["vtoCAE"].strftime("%d/%m/%Y"),
    }

    # Items del comprobante
    items = []
    for item in raw_items:
        items.append(
            {
                "code": str(item.product.code),
                "name": item.product.name,
                "quantity": f"{item.quantity:.2f}".replace(".", ","),
                "measurement_unit": item.product.unit or "Unidad",
                "price": f"{item.product.price:.2f}".replace(".", ","),
                "tax_percent": f"{item.product.get_vat_value()}%",
                "percent_subsidized": "0,00",
                "impost_subsidized": "0,00",
                "subtotal": f"{item.subtotal():.2f}".replace(".", ","),
            }
        )

    # Datos de a quien va emitido del comprobante
    billing_data = {
        "tax_id": client.id_data.number,
        "name": client.name,
        "vat_condition": client.get_vat_condition_display(),
        "address": client.address,
        "payment_method": "Cuenta corriente",
    }

    # Resumen
    overall = {
        "subtotal": f"{order.calculate_subtotal():.2f}".replace(".", ","),
        "impost_tax": f"{order.vat_total():.2f}".replace(".", ","),
        "total": f"{order.calculate_total():.2f}".replace(".", ","),
    }

    qr = generate_qr(invoice.b64_fiscal_data)

    html_path = f"{settings.BASE_DIR}/templates/arca_pdf.html"

    html = open(html_path, encoding="utf-8").read()

    template = Template(html)

    rendered_html = template.render(
        business_data=business_data,
        bill=bill,
        items=items,
        billing_data=billing_data,
        overall=overall,
        qr_code_image=qr,
    )

    pdf_name = (
        store.store_number.formatted_store_number()
        + invoice.document_letter
        + invoice.document_number.formatted_document_number()
    )
    os.makedirs(f"{settings.BASE_DIR}/invoices", exist_ok=True)
    pdf_path = f"{settings.BASE_DIR}/invoices/{pdf_name}.pdf"

    pdfkit.from_string(rendered_html, pdf_path)

    return pdf_path
