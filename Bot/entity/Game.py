import datetime
from dataclasses import dataclass

@dataclass
class GameDTO:
    id: int
    user_id: int
    rawg_id: int
    name: str
    status: int
    rating: int
    note: str
    date_added: datetime.date
    completion_date: datetime.date

    def _status_to_string(self) -> str:
        if self.status == 1:
            return "Пройдена"
        elif self.status == 2:
            return "В процессе"
        elif self.status == 3:
            return "Планиурется"
        elif self.status == 4:
            return "Брошена"

    def to_full_string(self) -> str:
        text = f"Игра: {self.name}\nСтатус: {self._status_to_string()}\n"
        if self.rating:
            text += f"Оценка: {self.rating}\n"
        if self.completion_date:
            text += f"Дата прохождения: {self.completion_date.strftime('%Y-%m-%d')}\n"
        if self.note:
            text += f"Комментарий:\n{self.note}"
        return text.rstrip()