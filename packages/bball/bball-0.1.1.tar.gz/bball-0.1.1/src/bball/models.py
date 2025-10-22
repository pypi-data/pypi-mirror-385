"""Core data models for NBA analytics."""

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel


class Player(BaseModel):
    """NBA Player model."""
    id: str
    name: str
    team_id: str | None = None
    position: str
    height: int | None = None  # in inches
    weight: int | None = None  # in pounds
    jersey_number: int | None = None

    class Config:
        json_schema_extra: ClassVar = {
            "example": {
                "id": "203999",
                "name": "Nikola Jokic",
                "team_id": "DEN",
                "position": "C",
                "height": 83,
                "weight": 284,
                "jersey_number": 15,
            },
        }


class Team(BaseModel):
    """NBA Team model."""
    id: str
    name: str
    city: str
    abbreviation: str
    conference: str
    division: str

    class Config:
        json_schema_extra: ClassVar = {
            "example": {
                "id": "1610612743",
                "name": "Nuggets",
                "city": "Denver",
                "abbreviation": "DEN",
                "conference": "West",
                "division": "Northwest",
            },
        }


class Stats(BaseModel):
    """Basketball statistics model."""
    points: float = 0
    rebounds: float = 0
    assists: float = 0
    steals: float = 0
    blocks: float = 0
    turnovers: float = 0
    field_goals_made: float = 0
    field_goals_attempted: float = 0
    three_pointers_made: float = 0
    three_pointers_attempted: float = 0
    free_throws_made: float = 0
    free_throws_attempted: float = 0
    minutes_played: float = 0

    @property
    def field_goal_percentage(self) -> float:
        """Calculate field goal percentage."""
        if self.field_goals_attempted == 0:
            return 0.0
        return self.field_goals_made / self.field_goals_attempted

    @property
    def three_point_percentage(self) -> float:
        """Calculate three-point percentage."""
        if self.three_pointers_attempted == 0:
            return 0.0
        return self.three_pointers_made / self.three_pointers_attempted

    @property
    def free_throw_percentage(self) -> float:
        """Calculate free throw percentage."""
        if self.free_throws_attempted == 0:
            return 0.0
        return self.free_throws_made / self.free_throws_attempted


class Game(BaseModel):
    """NBA Game model."""
    id: str
    date: datetime
    home_team_id: str
    away_team_id: str
    home_score: int | None = None
    away_score: int | None = None
    season: str
    season_type: str = "Regular Season"  # Regular Season, Playoffs, etc.

    @property
    def winner_id(self) -> str | None:
        """Get the winning team ID."""
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_team_id if self.home_score > self.away_score else self.away_team_id
