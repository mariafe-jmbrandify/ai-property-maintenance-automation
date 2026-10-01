from maintenance_ops.dispatch import Technician, rank_technicians

TECHS = [
    Technician("Mike", ["Plumbing"], ["Charlotte"], ["Tue", "Wed"], current_jobs=3, rating=4.9),
    Technician("Chris", ["Plumbing"], ["Charlotte"], ["Tue"], current_jobs=1, rating=4.5),
    Technician("Ana", ["General Maintenance"], ["Charlotte"], ["Tue"], current_jobs=0, rating=4.8),
    Technician("Sam", ["Plumbing"], ["Matthews"], ["Tue"], current_jobs=0, rating=5.0),
    Technician("Lee", ["Plumbing"], ["Charlotte"], ["Tue"], current_jobs=6, max_daily_jobs=6),
]


def names(ts):
    return [t.name for t in ts]


def test_filters_area_capacity_and_ranks_by_workload():
    assert names(rank_technicians(TECHS, trade="Plumbing", area="Charlotte", preferred_days=["Tue"])) == ["Chris", "Mike", "Ana"]


def test_preferred_technician_first():
    ranked = rank_technicians(TECHS, trade="Plumbing", area="Charlotte", preferred_days=["Tue"], preferred_technician="Mike")
    assert ranked[0].name == "Mike"


def test_day_mismatch_excluded():
    assert names(rank_technicians(TECHS, trade="Plumbing", area="Charlotte", preferred_days=["Wed"])) == ["Mike"]
