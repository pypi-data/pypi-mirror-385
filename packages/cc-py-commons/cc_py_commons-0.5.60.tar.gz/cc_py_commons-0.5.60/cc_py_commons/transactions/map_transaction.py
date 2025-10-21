import json, traceback
from dataclasses import fields
from cc_py_commons.transactions.transaction import Transaction
from cc_py_commons.utils.get_delivery_date import execute as get_delivery_date
from cc_py_commons.utils.logger_v2 import logger

def from_load(load):
	"""Takes a freight-hub load and maps it to a pricing load (Transaction)"""
	trans_data = {}

	for field in fields(Transaction):
		value = getattr(load, field.name, None)
		
		if value:
			trans_data[field.name] = value

	if not trans_data.get('delivery_date') and load.pickup_date:
		trans_data['delivery_date'] = get_delivery_date(pickup_date=load.pickup_date, distance_in_miles=load.distance)

	trans_data['equipment'] = load.equipment_description
	trans_data['all_in_cost'] = load.rate # all in cost may change at booking
	trans_data['carrier_id'] = load.carrier_id
	trans_data['target_pay'] = load.rate # target_pay is what the broker listed the load for
	trans_data['multi_stop'] = load.stops_count
	trans_data['team_service'] = load.team_service_required
	trans_data['partial_load'] = load.partial_load
	trans_data['ltl'] = load.ltl
	
	if isinstance(load.origin, dict):
		trans_data['origin_city'] = load.origin['city']
		trans_data['origin_state'] = load.origin['state']
		trans_data['origin_postcode'] = load.origin['postcode']
	else:
		trans_data['origin_city'] = load.origin.city
		trans_data['origin_state'] = load.origin.state
		trans_data['origin_postcode'] = load.origin.postcode

	if isinstance(load.destination, dict):
		trans_data['destination_city'] = load.destination['city']
		trans_data['destination_state'] = load.destination['state']
		trans_data['destination_postcode'] = load.destination['postcode']
	else:
		trans_data['destination_city'] = load.destination.city
		trans_data['destination_state'] = load.destination.state
		trans_data['destination_postcode'] = load.destination.postcode

	del trans_data['customer_id']
	trans_data['client_id'] = None
	trans_data['equipment_class'] = None
	trans_data['origin_pallets_required'] = load.origin_pallets_required
	trans_data['destination_pallets_required'] = load.destination_pallets_required
	trans_data['hazmat'] = load.hazmat
	trans_data['origin_location_id'] = load.origin_location_id
	trans_data['origin_location_name'] = load.origin_location_name
	trans_data['destination_location_id'] = load.destination_location_id
	trans_data['destination_location_name'] = load.destination_location_name
	trans_data['delivery_open_time'] = load.delivery_open_time
	trans_data['delivery_close_time'] = load.delivery_close_time
	trans_data['pickup_open_time'] = load.pickup_open_time
	trans_data['pickup_close_time'] = load.pickup_close_time
	trans_data['freight_hub_load_id'] = load.id
	trans_data['revenue_code'] = load.revenue_code
	trans_data['user_id'] = load.customer_id
	trans_data['po_number'] = load.po_number
	if load.special_instructions:
		trans_data['comments'] = load.special_instructions
	if load.linear_feet:
		trans_data['linear_feet'] = load.linear_feet

	try:
		transaction = Transaction(**trans_data)
	except Exception as e:
		logger.warning(json.dumps({
			'message': 'Failed to map Transaction schema object',
			'error': str(e),
			'stacktrace': traceback.format_exc()
		}))
		return None
	
	return transaction
