import datetime
from dataclasses import dataclass

@dataclass
class UserDTO:
    user_id: int
    telegram_username: str
    telegram_id: int
    registration_date: datetime.date
    last_active: datetime.date
