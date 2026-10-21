#!/usr/bin/env python3
"""Offline validation for ZentroMart's synthetic capstone pack. Python stdlib only."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import re
import sys

ROOT=Path(__file__).resolve().parent
EXPECTED={
    'data/customers.csv':300,
    'data/orders.csv':1000,
    'data/order_items.csv':1783,
    'data/products.csv':70,
    'data/pincodes.csv':36,
    'data/holidays.csv':4,
    'data/support_logs.csv':244,
    'practice/questions.csv':52,
    'practice/conversations.csv':96,
}
errors=[]


def check(assertion, description):
    if not assertion:errors.append(description)


def read_csv(path):
    with (ROOT/path).open('r',encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))


def keys(rows,fields):
    return [tuple(r[c] for c in fields) for r in rows]


def unique(rows,fields,description):
    k=keys(rows,fields)
    check(len(k)==len(set(k)), f'{description}: duplicate primary keys')
    check(all(all(v for v in item) for item in k), f'{description}: blank primary key')


def fk(rows,field,parents,parentfield,description):
    valid={p[parentfield] for p in parents}
    missing=[r[field] for r in rows if r[field] and r[field] not in valid]
    check(not missing, f'{description} {field}: {len(missing)} broken references')


def run():
    data={}
    for name,n in EXPECTED.items():
        rows=read_csv(name)
        data[Path(name).stem]=rows
        check(len(rows)==n, f'{name}: expected {n}, found {len(rows)}')
    for table,pk in {'customers':['customer_id'],'orders':['order_id'],
                     'order_items':['order_id','line_no'],'products':['sku'],
                     'pincodes':['pincode'],'holidays':['date'],
                     'support_logs':['log_id'],'questions':['id'],
                     'conversations':['conversation_id','turn']}.items():
        unique(data[table],pk,table)
    for rows,col,parents,key,label in [
        ('orders','customer_id','customers','customer_id','orders'),
        ('orders','delivery_pincode','pincodes','pincode','orders'),
        ('customers','pincode','pincodes','pincode','customers'),
        ('order_items','order_id','orders','order_id','order_items'),
        ('order_items','sku','products','sku','order_items'),
        ('support_logs','order_id','orders','order_id','support_logs'),
        ('support_logs','customer_id','customers','customer_id','support_logs'),
        ('conversations','order_id','orders','order_id','conversations'),
        ('conversations','customer_id','customers','customer_id','conversations'),
    ]:
        fk(data[rows],col,data[parents],key,label)

    counts=Counter()
    products={p['sku']:p for p in data['products']}
    for item in data['order_items']:
        counts[item['order_id']]+=int(item['qty'])*int(item['unit_price_inr'])
        prod=products[item['sku']]
        check(item['title']==prod['title'] and item['return_category']==prod['return_category'],
              f'product mismatch: order {item["order_id"]} line {item["line_no"]}')
    for order in data['orders']:
        oid=order['order_id']
        check(int(order['subtotal_inr'])==counts[oid], f'subtotal mismatch: {oid}')
        expected=(int(order['subtotal_inr'])-int(order['coupon_discount_inr'] or 0)
                  +int(order['delivery_fee_inr'])+int(order['cod_fee_inr']))
        check(expected==int(order['total_inr']), f'amount mismatch: {oid}')
    kbfiles=list((ROOT/'kb').glob('*.md'))
    check(len(kbfiles)==21,f'expected 21 KB docs, found {len(kbfiles)}')
    ids=[]
    for file in kbfiles:
        text=file.read_text(encoding='utf8')
        for field in ('doc_id:', 'title:', 'doc_type:', 'effective_from:', 'status:'):
            check(field in text,f'missing metadata {file.name}: {field}')
        ids+=re.findall(r'^##\s*\[([^\]]+)\]',text,re.M)
    check(len(ids)==len(set(ids)), 'duplicate KB section IDs')
    valid=set(ids)
    for kind in ['questions','conversations']:
        for r in data[kind]:
            for reference in r['gold_evidence'].split(' ; '):
                if not reference:continue
                good = (reference in valid or
                        (reference.startswith('products.csv:') and reference.split(':',1)[1] in products))
                check(good,f'{kind}: invalid evidence {reference}')
    groups=defaultdict(list)
    for row in data['conversations']:
        groups[row['conversation_id']].append(int(row['turn']))
    check(len(groups)==23,f'expected 23 conversations, found {len(groups)}')
    for cid,turns in groups.items():
        check(sorted(turns)==list(range(1,len(turns)+1)), f'{cid}: nonconsecutive turns')
    
    placeholder_found = False
    for p in ROOT.rglob('*'):
        if (
            p.is_file()
            and p.suffix in ('.csv', '.md', '.py')
            and p.name not in ('CHANGELOG.md', 'validate_dataset.py')
            and '.venv' not in p.parts
            and '.git' not in p.parts
            and '__pycache__' not in p.parts
        ):
            try:
                content = p.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue

            if '[COMPANY]' in content or '[company]' in content:
                placeholder_found = True
                break

    check(not placeholder_found, 'unresolved company placeholder')

    # Verify no personal/order details are disclosed without successful proof.
    sys.path.insert(0,str(ROOT))
    from tools import lookup_order,create_ticket
    oid=data['orders'][0]['order_id']
    order=next(x for x in data['orders'] if x['order_id']==oid)
    customer=next(x for x in data['customers'] if x['customer_id']==order['customer_id'])
    pending=lookup_order(oid)
    check(pending.get('verification_required') is True and 'items' not in pending and 'status' not in pending,
          'unverified lookup leaked order details')
    unknown=lookup_order('99999999','0000')
    check('items' not in unknown and not unknown.get('verified'), 'missing order leaked details')
    wrong='9999' if customer['phone'][-4:]!='9999' else '8888'
    denied=lookup_order(oid,verification_value=wrong)
    check(not denied.get('verified') and 'items' not in denied and 'status' not in denied,
          'invalid verification leaked order details')
    for proof in (customer['phone'][-4:],order['delivery_pincode']):
        verified=lookup_order(oid,verification_value=proof)
        check(verified.get('found') is True and verified.get('verified') is True
              and 'items' in verified and 'status' in verified
              and 'phone_last4' not in verified, 'valid verification rejected or returned phone suffix')
    check(create_ticket('short').get('created') is False,'short ticket unexpectedly created')
    # Every expected verification tool call must refer to the same order and to digits in the prompt.
    for row in data['conversations']:
        call=row['expected_tool_calls']
        if 'verification_value=' in call:
            proof=call.split('verification_value=',1)[1].split(')',1)[0]
            digits=''.join(d for d in row['customer_message'] if '0'<=d<='9')
            check(digits==proof, f'{row["conversation_id"]} turn {row["turn"]}: wrong verification call')
            check(f'order_id={row["order_id"]}' in call,
                  f'{row["conversation_id"]} turn {row["turn"]}: wrong lookup order id')
    if errors:
        print(f'FAIL — {len(errors)} issue(s) found:')
        for e in errors[:40]:print(' -',e)
        return 1
    print('PASS — all 9 CSVs, 21 KB documents, primary/foreign keys, order math,')
    print('       practice evidence, verification gates and company naming validated.')
    print('       1,000 orders | 1,783 items | 244 logs | 52 questions | 23 conversations')
    return 0

if __name__=='__main__':sys.exit(run())
