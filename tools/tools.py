"""Synthetic, offline customer-support tools for the ZentroMart capstone.

The mock order tool gates individual order details behind a simple identity check.
This is an educational simulation, NOT production-ready authentication.
"""
import csv
import os
from datetime import datetime
from uuid import uuid4

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.normpath(os.path.join(_HERE, '..', 'data'))
_TICKETS = os.path.join(_HERE, 'tickets_created.csv')
_TEXT_COLS = {
    'order_id', 'customer_id', 'delivery_pincode', 'return_rrn',
    'cancellation_rrn', 'rto_rrn', 'sku', 'return_sku', 'damage_sku',
    'pincode', 'phone',
}


def _clean(row):
    out = {}
    for key, value in row.items():
        if value == '':
            out[key] = None
        elif value in ('True', 'False'):
            out[key] = value == 'True'
        elif key not in _TEXT_COLS and value.lstrip('-').isdigit():
            out[key] = int(value)
        else:
            out[key] = value
    return out


def _read(name):
    with open(os.path.join(_DATA, name), encoding='utf-8', newline='') as handle:
        return [_clean(row) for row in csv.DictReader(handle)]


_ORDERS = {order['order_id']: order for order in _read('orders.csv')}
_ITEMS = {}
for _item in _read('order_items.csv'):
    _ITEMS.setdefault(_item['order_id'], []).append(_item)
_CUSTOMERS = {customer['customer_id']: customer for customer in _read('customers.csv')}


def lookup_order(order_id: str, verification_value: str = None) -> dict:
    """Lookup a synthetic order, disclosing details ONLY after verification.

    Calling with order_id alone always yields a verification-required message
    and no information about whether that order exists.

    Pass one caller-provided value: phone suffix (4 ASCII digits) OR delivery
    pincode (6 ASCII digits). Never read out the expected verification value.
    The conversation agent must enforce a maximum of one retry; this stateless
    tool does not track attempts or provide production-grade authentication.
    """
    oid = ''.join(ch for ch in str(order_id) if '0' <= ch <= '9')
    if verification_value is None or str(verification_value).strip() == '':
        return {'verification_required': True, 'order_id': oid,
                'message': 'Ask for the registered phone last 4 digits OR delivery pincode.'}

    proof = ''.join(ch for ch in str(verification_value) if '0' <= ch <= '9')
    order = _ORDERS.get(oid)
    if order:
        customer = _CUSTOMERS[order['customer_id']]
        valid = ((len(proof) == 4 and proof == customer['phone'][-4:])
                 or (len(proof) == 6 and proof == order['delivery_pincode']))
        if valid:
            return {'found': True, 'verified': True, **order,
                    'items': _ITEMS.get(oid, []),
                    'customer_first_name': customer['name'].split()[0],
                    'is_plus': customer['is_plus']}
    return {'verified': False, 'verification_required': True,
            'message': 'Verification failed or order not found.'}


def create_ticket(summary: str, order_id: str = None,
                  reason: str = None, intent: str = None) -> dict:
    """Log a synthetic human-handover ticket. Only claim success if created=True."""
    if not summary or len(summary.strip()) < 20:
        return {'created': False, 'error':
                'summary too short: include issue, checks made, and escalation reason'}
    tid = 'TKT' + uuid4().hex
    row = {'ticket_id': tid,
           'created_at': datetime.now().isoformat(timespec='seconds'),
           'order_id': order_id or '', 'intent': intent or '',
           'reason': reason or '', 'summary': summary}
    fresh = not os.path.exists(_TICKETS)
    with open(_TICKETS, 'a', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        if fresh:
            writer.writeheader()
        writer.writerow(row)
    return {'created': True, 'ticket_id': tid}
