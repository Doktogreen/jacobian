from random import randint
import uuid

def generate_transaction_reference():
    unique = uuid.uuid1()
    unique = str(unique).replace('-', '').upper()
    reference = 'SIM{}'.format(unique)
    return reference
