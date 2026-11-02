"""Synthetic-only backend; production never substitutes these responses."""
from three_role_boundary_01_fixtures import ideal, SyntheticBackend as BaseBackend

class SyntheticBackend(BaseBackend):
    synthetic_fixture=True
