from datetime import date
from pydantic import BaseModel, conint, constr
from typing import Optional

class Meal(BaseModel):
	meal_id: int
	category: str
	cuisine: str

class Order(BaseModel):
	center_id: int
	meal_id: int
	num_orders: Optional[int]

class Prediction(BaseModel):
	date : date
	num_orders : int

class Week(BaseModel):
	week: int
	center_id: int
	meal_id: int
	checkout_price: float
	base_price: float
	emailer_for_promotion: int
	homepage_featured: int
	num_orders: Optional[int]