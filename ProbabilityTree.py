import time
from functools import lru_cache

class ProbabilityTree:
    def __init__(self, initial_state, operator_list):
        self.root = initial_state
        self.operator_list = operator_list # List of (Operator, parameter) tuples
        self.op_num = len(operator_list)
        self.leaves = {}
    
    def __eq__(self, value: object) -> bool:
        return self.root == value.root and self.operator_list == value.operator_list

    def __hash__(self) -> int:
        return hash((self.root, tuple(self.operator_list)))
    
    def build_tree(self, debug=False, show=False):
        def build_tree_helper(layer, op_index, debug=False):
            next_layer = {}
            
            for node in layer.values():
                next_states = node.execute(self.operator_list[op_index])
                # if debug:
                #     # Check if the sum of probabilities remains the same
                #     tot_prob = sum(state.probability for state in next_states)
                #     if tot_prob != node.probability:
                #         print("=====================================")
                #         print(f"Error: Probability sum is not the same, sum is {tot_prob}, expected {node.probability}, the difference is {tot_prob - node.probability}")
                #         print(f"Layer {op_index + 1} operator: {self.operator_list[op_index]}")
                #         player = node.player
                #         print(f"parent node: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
                #         atk_player = node.atk_player
                #         print(f"atk player: {atk_player.deck}, {atk_player.stock}, {atk_player.probability}")
                        
                #         print(f"next states:")
                #         for state in next_states:
                #             player = state.player
                #             print(f"player: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
                #             atk_player = state.atk_player
                #             print(f"atk player: {atk_player.deck}, {atk_player.stock}, {atk_player.probability}")
                #         print("=====================================")
                for state in next_states:
                    if state.is_terminal() or op_index == self.op_num - 1:
                        if state in self.leaves:
                            self.leaves[state].add_probability(state.probability)
                        else:
                            self.leaves[state] = state
                    else:
                        if state in next_layer:
                            next_layer[state].add_probability(state.probability)
                        else:
                            next_layer[state] = state
            # if debug:
            #     print(f"Layer {op_index + 1}: {len(next_layer)} middle states")
            #     print(f"Middle states:")
            #     tot_prob = 0
            #     for state in next_layer:
            #         tot_prob += state.probability
            #         player = state.player
            #         print(f"player: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
            #     print(f"Layer {op_index + 1} total probability: {tot_prob}")
        
            return next_layer

        last_layer = {self.root: self.root}
        tot_time = 0
        tot_state = 0
        
        for i in range(self.op_num):
            # if not show:
            last_layer = build_tree_helper(last_layer, i, debug=debug)
            # else:
            #     print(f"Layer {i + 1} / {self.op_num}: {len(last_layer)} states to process", end='')
            #     tot_state += len(last_layer)
            #     time1 = time.time()
            #     last_layer = build_tree_helper(last_layer, i, debug=debug)
            #     time2 = time.time()
            #     tot_time += time2 - time1
            #     print(f", time: {time2 - time1} s. ", end='')
            #     if i != self.op_num - 1:
            #         print(f"Next layer: {len(last_layer)} states, estimated time: {tot_time / tot_state * len(last_layer)} s")
            #         # if len(last_layer) > 500000:
            #         #     print("Warning: Too many states to process, consider reducing the number of operators")
            #         #     self.kill_states(last_layer, threshold=0.05)
            #         #     print(f"Estimated time: {tot_time / tot_state * len(last_layer)} s")
            #     else:
            #         print(f"Leaves: {len(self.leaves)}")
        return 
    
    def kill_states(self, layer, threshold=0.05):
        layer.sort(key=lambda x: x.probability, reverse=True)
        p = 0
        x = 0
        while p < threshold:
            p += layer.pop().probability
            x += 1
        
        for s in layer:
            s.probability /= (1 - p)
            s.player.probability = s.probability
            s.atk_player.probability = s.probability
        
        print(f"Killed {x} states covering {float(p)} probability, remaining {len(layer)} states")
        return
    
    @lru_cache(maxsize=None)
    def calculate_probabilities(self, threshold):
        self.build_tree()
        result = {}
        init_hp = self.root.hp()
        
        for leaf in self.leaves.values():
            damage = leaf.hp() - init_hp
            if damage in result:
                result[damage] += leaf.probability
            else:
                result[damage] = leaf.probability
                
        # Sort the result dictionary by damage dealt
        result = dict(sorted(result.items()))
        kill_prob = sum(prob for damage, prob in result.items() if damage >= threshold)
        expecated_damage = sum(damage * prob for damage, prob in result.items())
        variance = sum((damage - expecated_damage) ** 2 * prob for damage, prob in result.items())
        check = sum(result.values())
        if check != 1:
            print(f"Error: Probability sum is not 1, sum is {check}")
        return result, kill_prob, expecated_damage, variance

