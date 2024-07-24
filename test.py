from GameState import Player, atkPlayer, GameState
from ProbabilityTree import ProbabilityTree
from solver import Solver
import time

deck = (5, 1)
level = (3, 0)
clock = (5, 0)
waiting_room = (15, 4)
operator_list = ["2", "2", "3"]

initial_player = Player(deck, waiting_room, level, clock)
initial_atk_player = atkPlayer((21, 14))
initial_state = GameState(initial_player, initial_atk_player)
probability_tree = ProbabilityTree(initial_state, operator_list)
# probability_tree.build_tree()
# threshold = 3
# result_dict, kill_prob, expectation, variance = probability_tree.calculate_probabilities(threshold)

# print(f"Result: {result_dict}")
# print(f"Kill Probability for threshold {threshold}: {kill_prob}")
# print(f"Expected Damage: {expectation.evalf()}")
# print(f"Variance: {variance.evalf()}")


solver = Solver(initial_state, operator_list)
time1 = time.time()
solver.solve()
time2 = time.time()
print(f"Solver time: {time2 - time1} seconds")
solver.show()