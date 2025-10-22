"""Utility functions for NBA data operations."""

from typing import Any

import httpx
import pandas as pd

from .models import Stats


async def fetch_nba_data(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch data from NBA API endpoints.

    Args:
        endpoint: API endpoint path
        params: Query parameters

    Returns:
        JSON response data
    """
    base_url = "https://stats.nba.com/stats"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/{endpoint}",
            params=params,
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


def calculate_advanced_stats(stats: Stats, team_stats: Stats | None = None) -> dict[str, float]:
    """Calculate advanced basketball statistics.

    Args:
        stats: Player statistics
        team_stats: Team statistics (optional, for certain calculations)

    Returns:
        Dictionary of advanced statistics
    """
    advanced = {}

    # True Shooting Percentage
    tsa = stats.field_goals_attempted + (0.44 * stats.free_throws_attempted)
    if tsa > 0:
        advanced["true_shooting_pct"] = stats.points / (2 * tsa)
    else:
        advanced["true_shooting_pct"] = 0.0

    # Effective Field Goal Percentage
    if stats.field_goals_attempted > 0:
        advanced["effective_fg_pct"] = (
            stats.field_goals_made + (0.5 * stats.three_pointers_made)
        ) / stats.field_goals_attempted
    else:
        advanced["effective_fg_pct"] = 0.0

    # Player Efficiency Rating (simplified version)
    if stats.minutes_played > 0:
        per_minute = (
            stats.points + stats.rebounds + stats.assists +
            stats.steals + stats.blocks - stats.turnovers -
            (stats.field_goals_attempted - stats.field_goals_made) -
            (stats.free_throws_attempted - stats.free_throws_made)
        ) / stats.minutes_played
        advanced["per_36"] = per_minute * 36
    else:
        advanced["per_36"] = 0.0

    # Usage Rate (simplified - would need team stats for accurate calculation)
    if team_stats and stats.minutes_played > 0:
        usage = (
            (stats.field_goals_attempted + 0.44 * stats.free_throws_attempted + stats.turnovers) *
            (team_stats.minutes_played / 5)
        ) / (
            stats.minutes_played *
            (team_stats.field_goals_attempted + 0.44 * team_stats.free_throws_attempted + team_stats.turnovers)
        )
        advanced["usage_rate"] = usage

    return advanced


def create_stats_dataframe(stats_list: list[Stats]) -> pd.DataFrame:
    """Convert a list of Stats objects to a pandas DataFrame.

    Args:
        stats_list: List of Stats objects

    Returns:
        DataFrame with statistics
    """
    data = [stat.model_dump() for stat in stats_list]
    df = pd.DataFrame(data)

    # Add calculated fields
    df["fg_pct"] = df["field_goals_made"] / df["field_goals_attempted"]
    df["3pt_pct"] = df["three_pointers_made"] / df["three_pointers_attempted"]
    df["ft_pct"] = df["free_throws_made"] / df["free_throws_attempted"]

    # Fill NaN values with 0 for percentage columns
    df[["fg_pct", "3pt_pct", "ft_pct"]] = df[["fg_pct", "3pt_pct", "ft_pct"]].fillna(0)

    return df
