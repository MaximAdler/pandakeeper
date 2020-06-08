from src.optimizer import Optimizer

# TODO: rewrite integration_tests

optimizer = Optimizer(path='tests/assets/calc_test.py') \
    .check_pandas() \
    .optimize() \
    .compile()
