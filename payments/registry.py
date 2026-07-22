from .gateways import CashOnDeliveryGateway

GATEWAYS = {
    CashOnDeliveryGateway.code: CashOnDeliveryGateway,
}

DEFAULT_GATEWAY = CashOnDeliveryGateway.code


def get_gateway(code=DEFAULT_GATEWAY):
    try:
        gateway_class = GATEWAYS[code]
    except KeyError:
        raise ValueError(f'Unknown payment gateway: {code}')
    return gateway_class()
