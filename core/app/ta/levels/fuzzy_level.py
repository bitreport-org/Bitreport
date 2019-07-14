from app.database.models import Level


class FuzzyLevel:
    def __init__(self, lvl: Level, last_price: float, eps: float = 0.02) -> None:
        self.lvl = lvl
        self.lower = lvl.value * (1 - eps)
        self.upper = lvl.value * (1 + eps)
        self.resistance = 0
        self.support = 0
        self.eps = eps
        self.dist = lvl.value - last_price

    def __repr__(self):
        return (
            f"{self.lvl.type.upper()} {self.lvl.value} {self.lvl.strength}"
            f"R: {self.resistance} S: {self.support}"
        )

    def __eq__(self, other):
        val1 = self.lower <= other.lvl.value <= self.upper
        val2 = other.lower <= self.lvl.value <= other.upper
        return val1 or val2

    def json(self) -> dict:
        return {
            "resistance": self.resistance,
            "support": self.support,
            "value": self.lvl.value,
            "strength": self.lvl.strength,
            "first_occurrence": self.lvl.first_occurrence,
            "type": self.lvl.type,
            "tf": self.lvl.timeframe,
        }

    @property
    def score(self) -> int:
        return self.support + self.resistance

    def update(self, others: list):
        for other in others:
            if self == other:
                if other.lvl.type == "resistance":
                    self.resistance += 1
                else:
                    self.support += 1
        return self
