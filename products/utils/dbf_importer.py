from dbfread import DBF

import traceback

VAT_CONVERSION = {
    21.00: 5,  # 21% -> Gravado
    10.50: 4,  # 10.5% -> Gravado
    

}

def import_products_from_dbf(file_path):
    table = DBF(file_path, load=True, encoding="latin1")
    created = 0
    skipped = 0

    for record in table :
        try:
            code = record.get("CODIGO", "").strip()
            name = record.get("DESCRIPCIO", "").strip()

            if not code or not name:
                print(f"Skipping record with missing code or name: {record}")
                skipped += 1
                continue

        product, _ = Product.objects.get_or_create(
            code=code, 


            