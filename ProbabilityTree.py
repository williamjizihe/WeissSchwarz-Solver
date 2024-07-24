from sympy import Rational

class ProbabilityTree:
    def __init__(self, initial_state, operator_list):
        self.root = initial_state
        self.operator_list = operator_list
        self.op_num = len(operator_list)
        self.layers = [[self.root]]
        self.leaves = []
        
    def build_tree(self, debug=False):
        def build_tree_helper(layer, op_index, debug=False):
            next_layer = []
            leaves = []
            for node in layer:
                next_states = node.parse_operator(self.operator_list[op_index])  # 使用解析器结果
                if debug:
                    # Check if the sum of probabilities remains the same
                    tot_prob = sum(state.probability for state in next_states)
                    if tot_prob != node.probability:
                        print("=====================================")
                        print(f"Error: Probability sum is not the same, sum is {tot_prob}, expected {node.probability}, the difference is {tot_prob - node.probability}")
                        print(f"Layer {op_index + 1} operator: {self.operator_list[op_index]}")
                        player = node.player
                        print(f"parent node: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
                        atk_player = node.atk_player
                        print(f"atk player: {atk_player.deck}, {atk_player.stock}, {atk_player.probability}")
                        
                        print(f"next states:")
                        for state in next_states:
                            player = state.player
                            print(f"player: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
                            atk_player = state.atk_player
                            print(f"atk player: {atk_player.deck}, {atk_player.stock}, {atk_player.probability}")
                        print("=====================================")
                for state in next_states:
                    if state.is_terminal() or op_index == self.op_num - 1:
                        leaves.append(state)
                    else:
                        next_layer.append(state)
            if debug:
                print(f"Layer {op_index + 1}: {len(next_layer)} middle states, {len(leaves)} leaves")
                print(f"Middle states:")
                tot_prob = 0
                for state in next_layer:
                    tot_prob += state.probability
                    player = state.player
                    print(f"player: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
                print(f"Leaves:")
                for state in leaves:
                    tot_prob += state.probability
                    player = state.player
                    print(f"player: {player.deck}, {player.waiting_room}, {player.level}, {player.clock}, {player.probability}, {player.top_climax_prob}")
                print(f"Layer {op_index + 1} total probability: {tot_prob}")
            self.leaves.extend(leaves)
            return next_layer

        for i in range(self.op_num):
            self.layers.append(build_tree_helper(self.layers[i], i, debug=debug))
        return self.layers, self.leaves

    def calculate_probabilities(self, threshold):
        result = {}
        init_hp = self.root.hp()
        
        for leaf in self.leaves:
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
        check = sum(prob for damage, prob in result.items())
        if check != 1:
            print(f"Error: Probability sum is not 1, sum is {check}")
        return result, kill_prob, expecated_damage, variance

