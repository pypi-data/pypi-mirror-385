See Project Logistic /My_code/TESTING_GUIDE.md in the source repository for the full, formatted testing guide.

Quick start

from hyce import Problem
import numpy as np

P = Problem(n_points=6)
P.add_vehicle_type("Truck")
P.add_vehicle_type("Bike")
P.add_vehicle("Truck", route=[0, 1, 2])
P.add_vehicle("Bike", route=[3, 4])

unary = np.array(
    [[0.0, 2.0, 1.5, 0.5, 0.5, 0.5],
     [0.4, 0.6, 0.7, 0.3, 0.3, 0.3]],
    dtype=np.float32,
)
P.add_attribute("load", kind="unary", data=unary, agg="sum")

P.set_constraint("Truck", "load", value=5.0, mode="add")
P.set_constraint("Bike", "load", value=2.0, mode="add")

violated = P.check_constraints_njit(verbose=True)
print("Vi phạm?", violated)

