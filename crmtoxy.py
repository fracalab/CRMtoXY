import csv
from datetime import datetime, timezone, time
import pandas as pd
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

def parse_result_test():
    # Input da parte dell'utente: codice della boutique e del venditore
    bt_code = input("Insert boutique code like B001, B002: ").strip()
    sales_person_code = input("Insert Sales Person code like VM5, VM6: ").strip()

    # Caricamento del file CSV contenente i dati CRM
    df_crm = pd.read_csv("fileinput.csv", low_memory=False, sep=";", header=0)

    # Se manca la colonna 'LINETAXAMOUNT', viene creata con valore 0
    if 'LINETAXAMOUNT' not in df_crm.columns:
        df_crm['LINETAXAMOUNT'] = 0

    # Elenco delle colonne attese nel CSV
    expected_columns = [
        'BOUTIQUE_CODE', 'TRANSACTION_DATE', 'RECEIPT_CODE', 'POSITION', 'TILL_SHORT_DESC',
        'SALESMAN_CODE', 'ID_NUMBER', 'CURRENCY', 'UNIT_PRICE_LIST_VALUE', 'PRODUCT_CODE',
        'QTY', 'ROW_PAID_VALUE', 'LINETAXAMOUNT', 'CUSTOMER_CODE_XY', 'CUSTOMER_CODE_CRM'
    ]

    # Verifica e selezione delle colonne effettivamente presenti
    available_columns = [col for col in expected_columns if col in df_crm.columns]
    df_crm = df_crm[available_columns]

    # Rinomina delle colonne per allinearle allo standard richiesto
    df_crm = df_crm.rename(columns={
        'BOUTIQUE_CODE': 'storeId',
        'TRANSACTION_DATE': 'orderDate',
        'RECEIPT_CODE': 'orderId',
        'POSITION': 'position_r',
        'TILL_SHORT_DESC': 'lineNumber',
        'SALESMAN_CODE': 'salesAssociateid',
        'ID_NUMBER': 'itemInstanceId',
        'CURRENCY': 'currency',
        'UNIT_PRICE_LIST_VALUE': 'unitPrice',
        'PRODUCT_CODE': 'itemId',
        'QTY': 'quantity',
        'ROW_PAID_VALUE': 'lineTotal',
        'LINETAXAMOUNT': 'lineTaxAmount',
        'CUSTOMER_CODE_XY': 'customerId',
        'CUSTOMER_CODE_CRM': 'customerExternalId',
    })

    # Riempimento dei valori mancanti
    df_crm.update(df_crm.select_dtypes('string').fillna(''))
    df_crm.update(df_crm.select_dtypes('number').fillna(0))
    df_crm.update(df_crm.select_dtypes('object').fillna(''))

    # Forza itemId a stringa per evitare il .0
    df_crm['itemId'] = df_crm['itemId'].astype(str).str.strip().str.replace('.0', '', regex=False)

    # Definizione delle colonne dell'output
    xy_csv_columns = [
        'storeId', 'orderDate', 'orderId', 'receiptType', 'lineNumber', 'transactionReasonCode',
        'status', 'salesAssociateid', 'itemInstanceId', 'lineType', 'barcode', 'currency',
        'unitPrice', 'itemId', 'quantity', 'deliveryType', 'itemSKU', 'lineTotal',
        'lineDiscount', 'lineTaxAmount', 'customerExternalId', 'customerId'
    ]

    result_list = []

    for index, row in df_crm.iterrows():
        try:
            if pd.notna(row['orderDate']) and str(row['itemId']) not in ['RB', 'LB', 'LB2', 'AB'] and int(row['orderDate']) > 20151231:

                try:
                    raw_unit_price = str(row['unitPrice']).replace(',', '.').strip()
                    raw_line_total = str(row['lineTotal']).replace(',', '.').strip()

                    unit_price_value = float(raw_unit_price) if raw_unit_price else 0.0
                    line_total_value = float(raw_line_total) if raw_line_total else 0.0
                except ValueError:
                    print(f"⚠️ Valore non numerico a riga {index}: unitPrice='{row['unitPrice']}', lineTotal='{row['lineTotal']}'")
                    continue

                lineDiscount = max(0, int((unit_price_value - line_total_value) * 100))
                lineTotal = int(line_total_value * 100)
                unitPrice = int(unit_price_value * 100)

                receiptType = 'Sale' if row['quantity'] >= 1 else 'Return'
                lineType = receiptType

                try:
                    raw_item_id = str(row['itemInstanceId']).replace(',', '.')
                    itemInstanceId_int = int(float(raw_item_id)) if raw_item_id.strip() else ""
                except:
                    itemInstanceId_int = ""

                barcode = str(itemInstanceId_int) if itemInstanceId_int else ""
                itemSKU = barcode
                deliveryType = "CarryOut"
                status = "Closed"
                transactionReasonCode = ""
                lineTaxAmount = 0
                salesPerson = sales_person_code

                dt_time = datetime.strptime(str(int(row['orderDate'])), "%Y%m%d")
                dt_time = datetime.combine(dt_time, time(9, 0, 0))
                dt_time_epoch = round(dt_time.replace(tzinfo=timezone.utc).timestamp())

                try:
                    # ✅ Conversione da scientifica e rimozione posizione
                    order_id_float = float(str(row['orderId']).replace(',', '.').strip())
                    order_id_str = '{:.0f}'.format(order_id_float)

                    position_r_int = int(float(str(row['position_r']).replace(',', '.')))
                    order_id_final = f"RP{bt_code}{order_id_str}"
                except ValueError:
                    print(f"⚠️ Codice ordine non valido alla riga {index}: orderId='{row['orderId']}', position_r='{row['position_r']}'")
                    continue

                result_list.append((
                    bt_code,
                    dt_time_epoch,
                    order_id_final,              # ✅ Solo orderId senza posizione
                    receiptType,
                    position_r_int,              # ✅ La posizione va in lineNumber
                    transactionReasonCode,
                    status,
                    salesPerson,
                    barcode,
                    lineType,
                    barcode,
                    str(row['currency']),
                    unitPrice,
                    str(row['itemId']),
                    str(row['quantity']),
                    deliveryType,
                    itemSKU,
                    lineTotal,
                    lineDiscount if row['quantity'] >= 1 else 0,
                    lineTaxAmount,
                    str(row['customerExternalId']),
                    str(row['customerId'])
                ))

        except Exception as e:
            print(f"Errore alla riga {index}: {e}")
            continue

    with open('Result.csv', 'w', newline='') as f_r:
        csv_writer = csv.writer(f_r, delimiter=';')
        csv_writer.writerow(xy_csv_columns)
        csv_writer.writerows(result_list)

    print(f"\n✅ Conversione completata. Righe processate: {len(result_list)}")

# Avvio dello script
if __name__ == "__main__":
    parse_result_test()
