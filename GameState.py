from fractions import Fraction
import re

class Player:
    def __init__(self, deck, waiting_room, level, clock, stock = (0, 0), probability=Fraction(1), top_climax_prob=()):
        '''
        deck: tuple, (Number of cards, Number of climaxes)
        waiting_room: tuple, (Number of cards, Number of climaxes)
        level: tuple, (Number of cards, Number of climaxes)
        clock: tuple, (Number of cards, Number of climaxes)
        stock: tuple, (Number of cards, Number of climaxes)
        probability: Probability of reaching this state
        top_climax_prob: List of probabilities of the top cards being climaxes
        '''
        self.deck = deck
        self.waiting_room = waiting_room
        self.clock = clock
        self.level = level
        self.stock = stock
        self.probability = probability
        self.top_climax_prob = top_climax_prob
    
    def copy(self):
        return Player(self.deck, self.waiting_room, self.level, self.clock, self.stock, self.probability, self.top_climax_prob)
    
    # reload the equality operator
    def __eq__(self, other):
        '''
        Check if two game states are equal, used for merging states in the tree
        '''
        if not isinstance(other, Player):
            raise ValueError("Can only compare Player with Player")
        
        return self.deck == other.deck and \
               self.waiting_room == other.waiting_room and \
               self.clock == other.clock and \
               self.level == other.level and \
               self.stock == other.stock and \
               self.top_climax_prob == other.top_climax_prob
    
    def is_terminal(self):
        return self.level[0] >= 4
    
    def level_up_check(self):
        if self.clock[0] < 7:
            return self
        
        up = self.clock[0] // 7
        rest = self.clock[0] % 7
        
        return Player(
            self.deck,
            (self.waiting_room[0] + self.clock[0] - rest, self.waiting_room[1] + self.clock[1]),
            (self.level[0] + up, self.level[1]),
            (rest, 0),
            self.stock,
            self.probability,
        )
        
    def refresh_deck(self):
        if self.deck[0] != 0:
            raise ValueError("Deck is not empty, can't refresh deck")
        
        new_deck = self.waiting_room
        if new_deck[0] == 0:
            raise ValueError("No cards in waiting room or deck")
  
        states = []
        # Since the deck is shuffled, the top card probability is reset
        climax_prob = Fraction(new_deck[1], new_deck[0])
        non_climax_prob = Fraction(new_deck[0] - new_deck[1], new_deck[0])
       
        if climax_prob > 0:
            climax_game_state = Player(
                (new_deck[0] - 1, new_deck[1] - 1),
                (0, 0),
                self.level,
                (self.clock[0] + 1, self.clock[1] + 1),
                self.stock,
                self.probability * climax_prob,
            )
            climax_game_state = climax_game_state.level_up_check()
            states.append(climax_game_state)
        
        if non_climax_prob > 0:
            non_climax_game_state = Player(
                (new_deck[0] - 1, new_deck[1]),
                (0, 0),
                self.level,
                (self.clock[0] + 1, self.clock[1]),
                self.stock,
                self.probability * non_climax_prob,
            )
            non_climax_game_state = non_climax_game_state.level_up_check()
            states.append(non_climax_game_state)
        
        return states

    def hp(self):
        return self.level[0] * 7 + self.clock[0]
    
    def get_climax_prob(self):
        if self.deck[0] == 0:
            raise ValueError("Deck is empty, can't get climax probability")
        
        if self.top_climax_prob:
            return self.top_climax_prob[0], Player(self.deck, self.waiting_room, self.level, self.clock, self.stock, self.probability, self.top_climax_prob[1:])
        else:
            return Fraction(self.deck[1], self.deck[0]), self
        
    def take_damage(self, damage):
        if damage <= 0:
            raise ValueError("Damage must be positive")
        
        def take_damage_helper(state, damage, checked_num, terminal_states):
            if state.is_terminal():
                terminal_states.append(state)
                return
            
            if state.deck[0] == 0:
                middle_states = state.refresh_deck()
                for middle_state in middle_states:
                    take_damage_helper(middle_state, damage, checked_num, terminal_states)
                return
                    
            climax_prob, state = state.get_climax_prob()
            non_climax_prob = 1 - climax_prob
            
            new_deck = (state.deck[0] - 1, state.deck[1] - 1)
            new_non_climax_deck = (state.deck[0] - 1, state.deck[1])
            
            if climax_prob > 0:
                # The damage is cancelled
                terminal_states.append(Player(
                    new_deck,
                    (state.waiting_room[0] + checked_num + 1, state.waiting_room[1] + 1),
                    state.level,
                    state.clock,
                    state.stock,
                    state.probability * climax_prob,
                    state.top_climax_prob
                ))
            
            if non_climax_prob > 0:
                is_damage_done = checked_num + 1 == damage
                next_state = Player(
                        new_non_climax_deck,
                        state.waiting_room,
                        state.level,
                        (state.clock[0] + damage, state.clock[1]) if is_damage_done else state.clock,
                        state.stock,
                        state.probability * non_climax_prob,
                        state.top_climax_prob
                    )
                next_state = next_state.level_up_check()
                    
                if is_damage_done:
                    terminal_states.append(next_state)
                else:
                    take_damage_helper(next_state, damage, checked_num + 1, terminal_states)
        
        terminal_states = []
        take_damage_helper(self, damage, 0, terminal_states)
        final_states = []
        for state in terminal_states:
            if state.deck[0] == 0:
                final_states.extend(state.refresh_deck())
            else:
                final_states.append(state)
        return final_states
    
    def take_moka(self, moka_num):
        def take_moka_helper(state, left_moka_num, non_climax_num, terminal_states):
            if left_moka_num == 0:
                tmp = []
                if state.deck[0] == 0:
                    tmp.extend(state.refresh_deck())
                else:
                    state.top_climax_prob = tuple([Fraction(0)] * non_climax_num)
                    tmp.append(state)
                
                for s in tmp:
                    found = False
                    for t in terminal_states:
                        if s == t:
                            t.probability += s.probability
                            found = True
                            break
                    if not found:
                        terminal_states.append(s)
                return
            
            climax_prob, state = state.get_climax_prob()
            if state == state:
                climax_prob = Fraction(state.deck[1], state.deck[0] - non_climax_num)
            non_climax_prob = 1 - climax_prob
            
            if climax_prob > 0:
                take_moka_helper(Player(
                    (state.deck[0] - 1, state.deck[1] - 1),
                    (state.waiting_room[0] + 1, state.waiting_room[1] + 1),
                    state.level,
                    state.clock,
                    state.stock,
                    state.probability * climax_prob,
                    state.top_climax_prob
                ), left_moka_num - 1, non_climax_num, terminal_states)
            
            if non_climax_prob > 0:
                take_moka_helper(Player(
                    state.deck,
                    state.waiting_room,
                    state.level,
                    state.clock,
                    state.stock,
                    state.probability * non_climax_prob,
                    state.top_climax_prob
                ), left_moka_num - 1, non_climax_num + 1, terminal_states)

        terminal_states = []
        moka_num = min(moka_num, self.deck[0])
        take_moka_helper(self, moka_num, 0, terminal_states)
        return terminal_states
    
    def michiru(self, michiru_num):
        pass
    
class atkPlayer:
    def __init__(self, deck, stock=(0, 0), probability=Fraction(1)):
        '''
        deck: tuple, (Number of cards, Number of souls)
        stock: tuple, (Number of cards, Number of souls)
        '''
        self.deck = deck
        self.stock = stock
        self.probability = probability
    
    def copy(self):
        return atkPlayer(self.deck, self.stock, self.probability)
    
    def trigger(self):
        soul_prob = Fraction(self.deck[1], self.deck[0])
        non_soul_prob = 1 - soul_prob
        
        soul_game_state = atkPlayer(
            (self.deck[0] - 1, self.deck[1] - 1),
            (self.stock[0] + 1, self.stock[1] + 1),
            self.probability * soul_prob,
        ) if soul_prob > 0 else None
        
        non_soul_game_state = atkPlayer(
            (self.deck[0] - 1, self.deck[1]),
            (self.stock[0] + 1, self.stock[1] ),
            self.probability * non_soul_prob,
        ) if non_soul_prob > 0 else None
            
        return [soul_game_state, non_soul_game_state]

class GameState:
    def __init__(self, player, atk_player):
        self.player = player
        self.atk_player = atk_player
        self.probability = min(player.probability, atk_player.probability)
        self.player.probability = self.probability
        self.atk_player.probability = self.probability
    
    def __str__(self) -> str:
        return f"{self.player.deck[1]}/{self.player.deck[0]} {self.player.waiting_room[1]}/{self.player.waiting_room[0]}\n {self.player.level[1]}/{self.player.level[0]} {self.player.clock[1]}/{self.player.clock[0]}\n{len(self.player.top_climax_prob)}\n{self.atk_player.deck[1]}/{self.atk_player.deck[0]} "
        
    def is_terminal(self):
        return self.player.is_terminal()
    
    def hp(self):
        return self.player.hp()
    
    def parse_operator(self, operator):
        """解析操作符，调用对应的函数"""
        operator = operator.lower()  # 转换为小写以处理大小写不敏感的问题
        moka_match = re.match(r'moka\((\d+)\)', operator)
        damage_trigger_match = re.match(r'(\d+)t', operator)
        damage_match = re.match(r'(\d+)', operator)

        if moka_match:
            num = int(moka_match.group(1))
            player_states = self.player.take_moka(num)
            return [GameState(player_state, self.atk_player.copy()) for player_state in player_states]
        
        elif damage_trigger_match:
            damage = int(damage_trigger_match.group(1))
            atk_player_states = self.atk_player.trigger()
            if atk_player_states[0] is None and atk_player_states[1] is None:
                raise ValueError("No trigger available")
            game_states = []
            
            if atk_player_states[0] is not None:
                # Trigger the soul trigger
                tmp_player = self.player.copy()
                tmp_player.probability = atk_player_states[0].probability
                player_states = tmp_player.take_damage(damage + 1)
                game_states.extend([GameState(player_state, atk_player_states[0].copy()) for player_state in player_states])
            
            if atk_player_states[1] is not None:
                # Trigger the non-soul trigger
                tmp_player = self.player.copy()
                tmp_player.probability = atk_player_states[1].probability
                player_states = tmp_player.take_damage(damage)
                game_states.extend([GameState(player_state, atk_player_states[1].copy()) for player_state in player_states])
            return game_states
        
        elif damage_match:
            damage = int(damage_match.group(1))
            player_states = self.player.take_damage(damage)
            return [GameState(player_state, self.atk_player.copy()) for player_state in player_states]
        else:
            raise ValueError(f"Invalid operator: {operator}")