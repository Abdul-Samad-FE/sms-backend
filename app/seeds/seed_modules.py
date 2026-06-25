"""Seed dashboard modules (sidebar entries)."""

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.dashboard_module import DashboardModule

ModuleDef = Tuple[str, str, str, str, int]  # name, display, icon, route, sort_order

MODULES: List[ModuleDef] = [
    ("dashboard", "Dashboard", "layout-dashboard", "/dashboard", 10),
    ("schools", "Schools", "building-2", "/schools", 20),
    ("students", "Students", "users", "/students", 30),
    ("classes", "Classes", "graduation-cap", "/classes", 40),
    ("attendance", "Attendance", "calendar-check", "/attendance", 50),
    ("reports", "Reports", "bar-chart-3", "/reports", 60),
    ("admin", "Administration", "shield", "/admin", 90),
]


def seed_modules(db: Session) -> int:
    existing = {row[0] for row in db.query(DashboardModule.modules_name).all()}
    new_count = 0
    for name, display, icon, route, sort in MODULES:
        if name in existing:
            continue
        db.add(
            DashboardModule(
                modules_name=name,
                display_name=display,
                icon=icon,
                route=route,
                sort_order=sort,
            )
        )
        new_count += 1
    if new_count:
        db.commit()
    return new_count
