"""Data access layer.

Each repository owns the ORM queries for one aggregate (User, Role,
Student, ...). Services compose repositories to implement business logic
without touching SQLAlchemy directly. Pattern adapted from GreenX 2.0.
"""
