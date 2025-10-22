from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TransferRequestDto:
    source_station_id: Optional[str] = None
    destination_station_id: Optional[str] = None
    item_ids: Optional[List[str]] = None
    metadata: Optional[List[str]] = None
    order_id: Optional[str] = None
    created_by: Optional[str] = None
