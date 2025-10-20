hybrid-constraint-engine
========================

A small constraint checking engine using NumPy + Numba with a simple Problem API.

- Pure-Python distribution (no compiled extensions)
- Depends on numpy and numba (prebuilt wheels required on target platform)
- Top-level modules installed: Core_class, constraint_kernel, build_attr_schema_auto, dtype_utils

Quick start

- Install: `pip install hybrid-constraint-engine`
- Use: `from Core_class import Problem`

Build and publish

- Build: `python -m pip install -U build twine` then `python -m build`
- Upload to TestPyPI: `python -m twine upload -r testpypi dist/*`
- Upload to PyPI: `python -m twine upload dist/*`

