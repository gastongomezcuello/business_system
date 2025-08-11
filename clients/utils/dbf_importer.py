from dbfread import DBF
from django.utils.timezone import make_aware, is_naive


from datetime import datetime
from clients.models import Client, IdDocument, Account


import traceback


AFIP_CONVERSION = {
    "I": "1",  # Responsable Inscripto
    "M": "6",  # Monotributo
    "E": "4",  # Exento
    "C": "5",  # Consumidor Final
    "N": "15",  # No alcanzado
}


def parse_date_safe(value):
    if isinstance(value, datetime):
        return make_aware(value) if is_naive(value) else value
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d")
        return make_aware(dt)
    except:
        return None


def import_clients_from_dbf(file_path):
    table = DBF(file_path, load=True, encoding="latin1")
    created = 0
    skipped = 0

    for record in list(table)[:10]:
        try:
            ruc = record.get("RUC", "").strip()
            print(f"Importando cliente con RUC: {ruc}")
            name = record.get("RAZON", "").strip()
            email = record.get("EMAIL", "").strip().lower() or f"{ruc}@placeholder.com"

            # Convertir condición fiscal

            cond_fisc = record.get("COND_FISC", "").strip().upper()

            vat_code = AFIP_CONVERSION.get(cond_fisc, "5")

            # Crear o encontrar documento
            id_doc, _ = IdDocument.objects.get_or_create(
                number=ruc,
                defaults={
                    "kind": "80",
                },
            )

            # Crear cliente
            client, created_client = Client.objects.get_or_create(
                id_data=id_doc,
                defaults={
                    "name": name,
                    "email": email,
                    "vat_condition_code": vat_code,
                    "address": record.get("DIRECCION", "").strip(),
                    "city": record.get("CIUDAD", "").strip(),
                    "province": record.get("PROVINCIA", "").strip(),
                    "phone_1": record.get("FONO1", "").strip(),
                    "phone_2": record.get("FONO2", "").strip(),
                    "cellphone": record.get("CELU1", "").strip(),
                    "cellphone_2": record.get("CELU2", "").strip(),
                    "fax": record.get("FAX", "").strip(),
                    "page": record.get("PAGINA", "").strip(),
                    "contact_name": record.get("CONTACTO", "").strip(),
                    "representative": record.get("REPRESENTA", "").strip(),
                    "credit_limit": record.get("MONTOCRED") or 0,
                    "price_level": str(record.get("NIVPREC") or ""),
                    "discount": record.get("DTO_ASIG") or 0,
                    "observations": record.get("OBS", "").strip(),
                    "created_at": parse_date_safe(record.get("FEC_ALTA")),
                },
            )

            print(created_client, client)
            # Crear cuenta asociada si no existe
            if created_client:
                client.refresh_from_db()
                account = client.account  # ya debería estar creado por el signal
                account.balance = record.get("SALDO_CTA") or 0
                account.last_payment_date = parse_date_safe(record.get("FEC_ULTPAG"))
                account.last_update = parse_date_safe(record.get("FEC_SALDO"))
                account.save()
                created += 1
            else:
                skipped += 1

        except Exception as e:
            print(f"🛑 Error importando cliente {record.get('RAZON')}: {e}")
            traceback.print_exc()
            skipped += 1

    return created, skipped
