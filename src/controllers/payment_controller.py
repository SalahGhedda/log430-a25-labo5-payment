"""
Payment controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import numbers
import requests
from commands.write_payment import create_payment, update_status_to_paid
from queries.read_payment import get_payment_by_id

def get_payment(payment_id):
    return get_payment_by_id(payment_id)

def add_payment(request):
    """ Add payment based on given params """
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    order_id = payload.get('order_id')
    total_amount = payload.get('total_amount')
    result = create_payment(order_id, user_id, total_amount)
    if isinstance(result, numbers.Number):
        return {"payment_id": result}
    else:
        return {"error": str(result)}
    
def process_payment(payment_id, credit_card_data):
    _process_credit_card_payment(credit_card_data)

    update_result = update_status_to_paid(payment_id)
    error_from_payment_update = update_result.get("error")
    if error_from_payment_update:
        raise RuntimeError(str(error_from_payment_update))

    order_id = update_result.get("order_id")
    if order_id is None:
        raise RuntimeError("Missing order_id returned by payment update.")
    is_paid = bool(update_result.get("is_paid", True))
    payload = {
        "order_id": order_id,
        "is_paid": is_paid
    }
    try:
        response = requests.put(
            "http://api-gateway:8080/store-api/orders",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        response_payload = response.json()
        store_manager_update = response_payload.get("updated", True)
    except requests.RequestException as exception:
        raise RuntimeError("Failed to update order status in Store Manager.") from exception
    except ValueError:
        store_manager_update = True
    return {
        "order_id": order_id,
        "payment_id": update_result.get("payment_id", payment_id),
        "is_paid": is_paid,
        "store_manager_update": store_manager_update
    }
    
def _process_credit_card_payment(payment_data):
    """ Placeholder method for simulated credit card payment """
    print(payment_data.get('cardNumber'))
    print(payment_data.get('cardCode'))
    print(payment_data.get('expirationDate'))