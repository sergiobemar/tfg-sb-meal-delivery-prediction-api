from pydantic import BaseModel, conint, constr
from typing import Optional

class Order(BaseModel):
	week: int
	center_id: int
	meal_id: int
	checkout_price: float
	base_price: float
	emailer_for_promotion: int
	homepage_featured: int
	num_orders: Optional[int]

class Prediction(BaseModel):
	center_id: int
	meal_id: int