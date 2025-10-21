import uuid
import datetime
from dataclasses import dataclass, field
from typing import List

from cc_py_commons.bids.bid_history import BidHistory

@dataclass
class Bid:
  id: uuid.UUID
  quote_id: uuid.UUID
  carrier_id: uuid.UUID
  receipt_id: str
  amount: int
  estimated_days: int
  notes: str
  match_score: float
  status_id: uuid.UUID
  pickup_date: datetime.datetime
  delivery_date: datetime.datetime
  decline_reason: str
  bid_histories: List[BidHistory]
  porus_truck_id: uuid.UUID 
  truck_lane_id: uuid.UUID
  distance: float
  origin_city: str
  origin_state: str
  dest_city: str
  dest_state: str
  origin_zip: str = field(default=None)
  origin_deadhead: float = field(default=None)
  dest_zip: str = field(default=None)
  invite_emailed_at: datetime.datetime = field(default=None)
