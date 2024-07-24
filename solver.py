# 用枚举找出最优攻击策略，时间复杂度极大，仅用于三种操作的情况
import re
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

class solver_node:
    def __init__(self, state, root_hp, operator_dict, last_op, parent, score=None, level=0):
        self.state = state
        self.root_hp = root_hp
        self.operator_dict = operator_dict
        self.last_op = last_op
        self.score = score
        self.parent = parent
        self.children_groups = None
        self.best_children_group = None
        self.level = level
        self.id = None
    
    def build_children(self):
        if self.is_leaf():
            return
        
        self.children_groups = []
        for op, times in self.operator_dict.items():
            children = []
            next_states = self.state.parse_operator(op)
            op_remains = self.operator_dict.copy()
            if times > 1:
                op_remains[op] -= 1
            else:
                del op_remains[op]
            for state in next_states:
                children.append(solver_node(state, self.root_hp, op_remains, op, self, level=self.level + 1))
            self.children_groups.append(children)
    
    def is_leaf(self):
        return self.operator_dict == {} or self.state.is_terminal()
    
    def is_root(self):
        return self.parent is None
    
    def get_score(self):
        if self.score is not None:
            return self.score
        
        if self.is_leaf():
            self.score = (self.state.hp() - self.root_hp) * self.state.probability
            return self.score
        
        if self.children_groups is None:
            self.build_children()
        
        children_group_score_list = [sum([child.get_score() for child in children]) for children in self.children_groups]
        # Keep track of the best child
        self.score = max(children_group_score_list)
        for i, group in enumerate(self.children_groups):
            if children_group_score_list[i] == self.score:
                self.best_children_group = group
                self.children_groups = None
                break
        return self.score

    def get_description(self):
        operator = operator.lower()  # 转换为小写以处理大小写不敏感的问题
        moka_match = re.match(r'moka\((\d+)\)', operator)
        damage_trigger_match = re.match(r'(\d+)t', operator)
        damage_match = re.match(r'(\d+)', operator)
        
        last_state = self.parent.state
        if moka_match:
            moka_num = int(moka_match.group(1))
            description = ''
            x = len(self.state.player.top_climax_prob) - len(last_state.player.top_climax_prob)
            description.join(f"During moka({moka_num}), {moka_num - x} climax cards are drawn. ")
            if self.state.player.deck[0] > last_state.player.deck[0]:
                description.join(f"After moka, the deck is reshuffled. 1 damage is dealt. ")
                if self.state.player.clock[1] >= 1:
                    description.join(f"The clock card is a climax card. ")
                else:
                    description.join(f"The clock card is not a climax card. ")
            
            return description
        elif damage_trigger_match:
            damage = int(damage_trigger_match.group(1))
            description = ''
            if last_state.atkPlayer.deck[1] > self.state.atkPlayer.deck[1]:
                description.join(f"Triggered successfully, {damage+1} damage is dealt. ")
            else:
                description.join(f"Triggered failed, {damage} damage is dealt. ")
            
            if self.state.atkPlayer.deck[1] == 0:
                description.join(f"The deck is reshuffled. ")

class Solver:
    def __init__(self, initial_state, operator_list):
        self.operator_list = operator_list
        self.operator_dict = {}
        for op in operator_list:
            self.operator_dict[op]  = self.operator_dict.get(op, 0) + 1
        for op, times in self.operator_dict.items():
            print(f"Operator {op}: {times}")
        self.root = solver_node(initial_state, initial_state.hp(), self.operator_dict, None, None, level=0)
    
    def solve(self):
        return self.root.get_score()
    
    def show(self):
        # Show the best strategy
        node = self.root
        queue = [node]
        
        G = nx.DiGraph()
        node_id = 0
        
        while queue:
            node = queue.pop(0)
            
            if node.level != len(self.operator_list):
                G.add_node(node_id, label=str(node.state))
                node.id = node_id
                
                if not node.is_root():
                    G.add_edge(node.parent.id, node.id, label=node.last_op)
                node_id += 1
                if not node.is_leaf():
                    queue.extend(node.best_children_group)
                

        # 设置图像大小和分辨率
        plt.figure(figsize=(20, 20), dpi=300)  # figsize 调整图像大小, dpi 调整分辨率
        
        # 绘制图形
        pos = graphviz_layout(G, root=0)  # 布局方式

        # 绘制节点和边
        nx.draw(G, pos, with_labels=False, node_size=5000, node_color="skyblue", font_size=10, font_weight="bold", arrowsize=10)

        nx.draw_networkx_nodes(G, pos, nodelist=[0], node_size=5000, node_color="red")
        
        # 获取节点和边的注释
        node_labels = nx.get_node_attributes(G, 'label')
        edge_labels = nx.get_edge_attributes(G, 'label')

        # 在节点上添加注释
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=15, font_color="black")

        # 在边上添加注释
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=15, font_color="red")

        # 保存图形到文件
        plt.savefig("strategy_graph.png")
        plt.close()
    
    def calculate_probabilities(self, threshold):
        node = self.root
        queue = [node]
        result = {}
        init_hp = node.root_hp
        
        while queue:
            node = queue.pop(0)
            if node.is_leaf():
                damage = node.state.hp() - init_hp
                result[damage] = result.get(damage, 0) + node.state.probability
            else:
                queue.extend(node.best_children_group)

        # Sort the result dictionary by damage dealt
        result = dict(sorted(result.items()))
        kill_prob = sum(prob for damage, prob in result.items() if damage >= threshold)
        expecated_damage = sum(damage * prob for damage, prob in result.items())
        variance = sum((damage - expecated_damage) ** 2 * prob for damage, prob in result.items())
        check = sum(prob for prob in result.values())
        if check != 1:
            print(f"Error: Probability sum is not 1, sum is {check}")
        return result, kill_prob, expecated_damage, variance