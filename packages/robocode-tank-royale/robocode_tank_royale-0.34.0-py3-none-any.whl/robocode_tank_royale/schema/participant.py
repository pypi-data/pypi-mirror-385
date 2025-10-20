"""
Generated Python class from participant.schema.yaml
This file is auto-generated. Do not edit manually.
"""

from .initial_position import InitialPosition

class Participant:
    """Bot participating in a battle"""

    def __init__(self, id: int | None, session_id: str | None, name: str | None, version: str | None, authors: list[str | None] | None, description: str | None = None, homepage: str | None = None, country_codes: list[str | None] | None = None, game_types: list[str | None] | None = None, platform: str | None = None, programming_lang: str | None = None, initial_position: InitialPosition | None = None, team_id: int | None = None, team_name: str | None = None, team_version: str | None = None, is_droid: bool | None = None):
        if version is None:
            raise ValueError("The 'version' parameter must be provided.")
        if session_id is None:
            raise ValueError("The 'session_id' parameter must be provided.")
        if authors is None:
            raise ValueError("The 'authors' parameter must be provided.")
        if id is None:
            raise ValueError("The 'id' parameter must be provided.")
        if name is None:
            raise ValueError("The 'name' parameter must be provided.")
        self.id = id
        self.session_id = session_id
        self.name = name
        self.version = version
        self.authors = authors
        self.description = description
        self.homepage = homepage
        self.country_codes = country_codes
        self.game_types = game_types
        self.platform = platform
        self.programming_lang = programming_lang
        self.initial_position = initial_position
        self.team_id = team_id
        self.team_name = team_name
        self.team_version = team_version
        self.is_droid = is_droid
