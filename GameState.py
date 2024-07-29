from fractions import Fraction
from utils import Operator
from math import comb
from functools import lru_cache

class Player:
    def __init__(self, deck, waiting_room, level, clock, probability=Fraction(1), top_climax_prob=()):
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
        self.probability = probability
        self.top_climax_prob = top_climax_prob
    
    def copy(self):
        return Player(self.deck, self.waiting_room, self.level, self.clock, self.probability, self.top_climax_prob)
    
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
               self.probability == other.probability and \
               self.top_climax_prob == other.top_climax_prob
    
    def __hash__(self):
        return hash((self.deck, self.waiting_room, self.level, self.clock, self.probability, self.top_climax_prob))
    
    def same_state(self, other):
        '''
        Check if two game states are the same, used for checking if the state is already in the tree
        '''
        if not isinstance(other, Player):
            raise ValueError("Can only compare Player with Player")
        
        return self.deck == other.deck and \
               self.waiting_room == other.waiting_room and \
               self.level == other.level and \
               self.clock == other.clock and \
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
                self.probability * non_climax_prob,
            )
            non_climax_game_state = non_climax_game_state.level_up_check()
            states.append(non_climax_game_state)
        
        return states

    def inplace_shuffle_deck(self):
        if self.top_climax_prob:
            self.top_climax_prob = ()
        
    def hp(self):
        return self.level[0] * 7 + self.clock[0]
    
    def get_climax_prob(self):
        if self.deck[0] == 0:
            raise ValueError("Deck is empty, can't get climax probability")
        
        if self.top_climax_prob:
            return self.top_climax_prob[0], Player(self.deck, self.waiting_room, self.level, self.clock, self.probability, self.top_climax_prob[1:])
        else:
            return Fraction(self.deck[1], self.deck[0]), self
    
    @lru_cache(maxsize=None)
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
    
    @lru_cache(maxsize=None)
    def take_moka(self, moka_num):
        '''
        Draw moka_num cards from the deck, put the climax cards into the waiting room, and the rest back to the deck
        During the process, the deck won't be reshuffled even if it's empty
        Return: list of Player
        '''
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
                        if s.same_state(t):
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
                    state.probability * climax_prob,
                    state.top_climax_prob
                ), left_moka_num - 1, non_climax_num, terminal_states)
            
            if non_climax_prob > 0:
                take_moka_helper(Player(
                    state.deck,
                    state.waiting_room,
                    state.level,
                    state.clock,
                    state.probability * non_climax_prob,
                    state.top_climax_prob
                ), left_moka_num - 1, non_climax_num + 1, terminal_states)

        terminal_states = []
        moka_num = min(moka_num, self.deck[0])
        take_moka_helper(self, moka_num, 0, terminal_states)
        return terminal_states
    
    @lru_cache(maxsize=None)
    def michiru(self, michiru_num):
        '''
        Draw michiru_num cards from the deck, put them into waiting room,
        return how many climax cards are drawn
        During the process, the deck is reshuffled if it's empty
        Retutrn: dict(num of climax cards: list of Player)
        '''
        def case_comb(n, c, a, d):
            return comb(c, d) * comb(n-c, a-d)
        
        def michiru_helper_fast(state, michiru_num, terminal_states):
            '''
            We don't consider refresh deck situation here
            '''
            tot_cases = comb(state.deck[0], michiru_num)
            
            for num_climax in range(max(0, michiru_num - state.deck[0] + state.deck[1]), min(state.deck[1], michiru_num) + 1):
                new_player = Player(
                    (state.deck[0] - michiru_num, state.deck[1] - num_climax),
                    (state.waiting_room[0] + michiru_num, state.waiting_room[1] + num_climax),
                    state.level,
                    state.clock,
                    state.probability * Fraction(case_comb(state.deck[0], state.deck[1], michiru_num, num_climax), tot_cases),
                    state.top_climax_prob
                )
                
                if new_player.deck[0] == 0:
                    if num_climax not in terminal_states:
                        terminal_states[num_climax] = new_player.refresh_deck()
                    else:
                        terminal_states[num_climax].extend(new_player.refresh_deck())
                else:
                    if num_climax not in terminal_states:
                        terminal_states[num_climax] = []
                    terminal_states[num_climax].append(new_player)
            
        def michiru_helper(state, left_michiru_num, num_climax, terminal_states):
            '''
            Terminal states: dict(num of climax cards: list of Player)
            '''
            if left_michiru_num == 0:
                tmp = []
                if state.deck[0] == 0:
                    tmp.extend(state.refresh_deck())
                else:
                    tmp.append(state)
                
                for s in tmp:
                    found = False
                    if num_climax not in terminal_states:
                        terminal_states[num_climax] = []
                        
                    for t in terminal_states[num_climax]:
                        if s.same_state(t):
                            t.probability += s.probability
                            found = True
                            break
                    if not found:
                        terminal_states[num_climax].append(s)
                return
            
            if state.deck[0] == 0:
                tmp = state.refresh_deck()
                for s in tmp:
                    michiru_helper(s, left_michiru_num, num_climax, terminal_states)
                return
            
            climax_prob, state = state.get_climax_prob()
            non_climax_prob = 1 - climax_prob
            
            if climax_prob > 0:
                michiru_helper(Player(
                    (state.deck[0] - 1, state.deck[1] - 1),
                    (state.waiting_room[0] + 1, state.waiting_room[1] + 1),
                    state.level,
                    state.clock,
                    state.probability * climax_prob,
                    state.top_climax_prob
                ), left_michiru_num - 1, num_climax + 1, terminal_states)
            
            if non_climax_prob > 0:
                michiru_helper(Player(
                    (state.deck[0] - 1, state.deck[1]),
                    (state.waiting_room[0] + 1, state.waiting_room[1]),
                    state.level,
                    state.clock,
                    state.probability * non_climax_prob,
                    state.top_climax_prob
                ), left_michiru_num - 1, num_climax, terminal_states)
            
        terminal_states = {}
        if michiru_num <= self.deck[0] and self.top_climax_prob == ():
            michiru_helper_fast(self, michiru_num, terminal_states)
        else:
            michiru_helper(self, michiru_num, 0, terminal_states)
        return terminal_states
    
    @lru_cache(maxsize=None)
    def woody(self, woody_num):
        '''
        Check the top woody_num cards, return the number of climax cards.
        After checking, the top cards are reshuffled into the deck.
        During the process, the deck won't be reshuffled even if it's empty
        woody_num <= state.deck[0]
        We don't consider refresh deck situation here
        '''
        def case_comb(n, c, a, d):
            return comb(c, d) * comb(n-c, a-d)
        
        if woody_num <= 0:
            raise ValueError("Woody number must be positive")
        
        woody_num = min(woody_num, self.deck[0])
        terminal_probs = {}
        
        if self.top_climax_prob == ():
            tmp_deck = self.deck
        elif woody_num > len(self.top_climax_prob):
            woody_num -= len(self.top_climax_prob)
            tmp_deck = (self.deck[0] - len(self.top_climax_prob), self.deck[1])
        elif woody_num <= len(self.top_climax_prob):
            return {0:1}
        
        tot_cases = comb(tmp_deck[0], woody_num)
        for num_climax in range(max(0, woody_num - tmp_deck[0] + tmp_deck[1]), min(tmp_deck[1], woody_num) + 1):
            prob = Fraction(case_comb(tmp_deck[0], tmp_deck[1], woody_num, num_climax), tot_cases)
            terminal_probs[num_climax] = prob

        return terminal_probs
        
    def put_to_clock(self, damage):
        '''
        Put damage cards from the deck to the clock, return the new game states
        During the process, the deck is reshuffled if it's empty
        Return: list of Player
        '''
        def put_to_clock_helper(state, left_damage, terminal_states):
            if left_damage == 0:
                tmp = []
                if state.deck[0] == 0:
                    tmp.extend(state.refresh_deck())
                else:
                    tmp.append(state)
                
                for s in tmp:
                    found = False
                    for t in terminal_states:
                        if s.same_state(t):
                            t.probability += s.probability
                            found = True
                            break
                    if not found:
                        terminal_states.append(s)
                return
            
            climax_prob, state = state.get_climax_prob()
            non_climax_prob = 1 - climax_prob
            
            if climax_prob > 0:
                climax_state = Player(
                    (state.deck[0] - 1, state.deck[1] - 1),
                    state.waiting_room,
                    state.level,
                    (state.clock[0] + 1, state.clock[1] + 1),
                    state.probability * climax_prob,
                    state.top_climax_prob
                )
                climax_state = climax_state.level_up_check()
                put_to_clock_helper(climax_state, left_damage - 1, terminal_states)
            
            if non_climax_prob > 0:
                non_climax_state = Player(
                    (state.deck[0] - 1, state.deck[1]),
                    state.waiting_room,
                    state.level,
                    (state.clock[0] + 1, state.clock[1]),
                    state.probability * non_climax_prob,
                    state.top_climax_prob
                )
                put_to_clock_helper(non_climax_state, left_damage - 1, terminal_states)
        
        terminal_states = []
        put_to_clock_helper(self, damage, terminal_states)
        return terminal_states
        
    
class atkPlayer:
    def __init__(self, deck):
        '''
        deck: tuple, (Number of cards, Number of souls)
        '''
        self.deck = deck
    
    def copy(self):
        return atkPlayer(self.deck)
    
    def __eq__(self, value: object) -> bool:
        return self.deck == value.deck
    
    def __hash__(self) -> int:
        return hash(self.deck)
    
    def trigger(self):
        soul_prob = Fraction(self.deck[1], self.deck[0])
        non_soul_prob = 1 - soul_prob
        
        soul_game_state = atkPlayer(
            (self.deck[0] - 1, self.deck[1] - 1)
        ) if soul_prob > 0 else None
        
        non_soul_game_state = atkPlayer(
            (self.deck[0] - 1, self.deck[1])
        ) if non_soul_prob > 0 else None
            
        return soul_game_state, non_soul_game_state, soul_prob, non_soul_prob

class GameState:
    def __init__(self, player, atk_player, probability):
        self.player = player
        self.atk_player = atk_player
        self.probability = probability
    
    def set_probability(self, probability):
        self.probability = probability
    
    def add_probability(self, probability):
        self.probability += probability
        
    def __str__(self) -> str:
        return f"{self.player.deck[1]}/{self.player.deck[0]} {self.player.waiting_room[1]}/{self.player.waiting_room[0]}\n {self.player.level[1]}/{self.player.level[0]} {self.player.clock[1]}/{self.player.clock[0]}\n{len(self.player.top_climax_prob)}\n{self.atk_player.deck[1]}/{self.atk_player.deck[0]} "
    
    def __eq__(self, value: object) -> bool:
        return self.player.same_state(value.player) and self.atk_player == value.atk_player
    
    def __hash__(self) -> int:
        return hash((self.player.deck, self.player.waiting_room, self.player.level, self.player.clock, self.player.top_climax_prob, self.atk_player.deck))
        
    def is_terminal(self):
        return self.player.is_terminal()
    
    def hp(self):
        return self.player.hp()
    
    def execute(self, operator):
        """
        operator: (Operator, int)
        """
        if self.is_terminal():
            return [self]
        
        operator_type, num = operator
        base_prob = self.probability
        self.player.probability = 1
        
        if operator_type == Operator.MOKA:
            player_states = self.player.take_moka(num)
            return [GameState(player_state.copy(), self.atk_player.copy(), base_prob * player_state.probability) for player_state in player_states]
        
        elif operator_type == Operator.MICHIRU:
            player_states_dict = self.player.michiru(num)
            final_states = []
            for damage, state_list in player_states_dict.items():
                if damage == 0:
                    final_states.extend([GameState(player_state.copy(), self.atk_player.copy(), base_prob * player_state.probability) for player_state in state_list])
                else:
                    for player_state in state_list:
                        tmp_player = player_state.copy()
                        new_base_prob = base_prob * tmp_player.probability
                        tmp_player.probability = 1
                        new_player_states = tmp_player.take_damage(damage)
                        final_states.extend([GameState(new_player_state.copy(), self.atk_player.copy(), new_base_prob * new_player_state.probability) for new_player_state in new_player_states])
            return final_states
        
        elif operator_type == Operator.WOODY:
            damage_probs_dict = self.player.woody(num)
            final_states = []
            for damage, prob in damage_probs_dict.items():
                if damage == 0:
                    final_states.append(GameState(self.player.copy(), self.atk_player.copy(), base_prob * prob))
                else:
                    tmp_player = self.player.copy()
                    new_base_prob = base_prob * prob
                    new_player_states = tmp_player.put_to_clock(damage)
                    final_states.extend([GameState(new_player_state.copy(), self.atk_player.copy(), new_base_prob * new_player_state.probability) for new_player_state in new_player_states])
            return final_states
        
        elif operator_type == Operator.TRIGGER:
            damage = num
            atk_player_soul_state, atk_player_non_soul_state, soul_prob, non_soul_prob = self.atk_player.trigger()
            if atk_player_soul_state is None and atk_player_non_soul_state is None:
                raise ValueError("No trigger available")
            game_states = []
            
            if atk_player_soul_state is not None:
                # Trigger the soul trigger
                tmp_player = self.player.copy()
                player_states = tmp_player.take_damage(damage + 1)
                game_states.extend([GameState(player_state.copy(), atk_player_soul_state.copy(), base_prob * soul_prob * player_state.probability) for player_state in player_states])
            
            if atk_player_non_soul_state is not None:
                # Trigger the non-soul trigger
                tmp_player = self.player.copy()
                player_states = tmp_player.take_damage(damage)
                game_states.extend([GameState(player_state.copy(), atk_player_non_soul_state.copy(), base_prob * non_soul_prob * player_state.probability) for player_state in player_states])
                    
            return game_states
        
        elif operator_type == Operator.DAMAGE:
            damage = num
            player_states = self.player.take_damage(damage)
            return [GameState(player_state.copy(), self.atk_player.copy(), base_prob * player_state.probability) for player_state in player_states]
        else:
            raise ValueError(f"Invalid operator: {operator}")