import re
from collections import defaultdict

class NFA:
    def __init__(self, start_state, accept_state, transitions):
        self.start_state = start_state
        self.accept_state = accept_state
        self.transitions = transitions

    @staticmethod
    def thompson(regex):
        """Generate an NFA from a regex using Thompson's construction."""
        stack = []
        state_count = 0

        def new_state():
            nonlocal state_count
            state = f"q{state_count}"
            state_count += 1
            return state

        def concat(nfa1, nfa2):
            nfa1.transitions[nfa1.accept_state]["ε"] = {nfa2.start_state}
            return NFA(nfa1.start_state, nfa2.accept_state, {**nfa1.transitions, **nfa2.transitions})

        def union(nfa1, nfa2):
            start = new_state()
            accept = new_state()
            transitions = {
                start: {"ε": {nfa1.start_state, nfa2.start_state}},
                nfa1.accept_state: {"ε": {accept}},
                nfa2.accept_state: {"ε": {accept}},
            }
            return NFA(start, accept, {**transitions, **nfa1.transitions, **nfa2.transitions})

        def kleene(nfa):
            start = new_state()
            accept = new_state()
            transitions = {
                start: {"ε": {nfa.start_state, accept}},
                nfa.accept_state: {"ε": {nfa.start_state, accept}},
            }
            return NFA(start, accept, {**transitions, **nfa.transitions})

        for char in regex:
            if char == "*":
                nfa = stack.pop()
                stack.append(kleene(nfa))
            elif char == "|":
                nfa2, nfa1 = stack.pop(), stack.pop()
                stack.append(union(nfa1, nfa2))
            elif char == ".":
                nfa2, nfa1 = stack.pop(), stack.pop()
                stack.append(concat(nfa1, nfa2))
            else:
                start = new_state()
                accept = new_state()
                transitions = {start: {char: {accept}}}
                stack.append(NFA(start, accept, transitions))

        return stack.pop()

class DFA:
    def __init__(self, start_state, accept_states, transitions):
        self.start_state = start_state
        self.accept_states = accept_states
        self.transitions = transitions

    @staticmethod
    def subset_construction(nfa):
        """Convert an NFA to a DFA using the subset construction."""
        start_set = frozenset({nfa.start_state})
        queue = [start_set]
        dfa_states = {start_set: f"q0"}
        dfa_transitions = {}
        accept_states = set()
        state_count = 1

        while queue:
            current_set = queue.pop(0)
            current_name = dfa_states[current_set]
            dfa_transitions[current_name] = {}

            move_map = defaultdict(set)
            for state in current_set:
                for char, next_states in nfa.transitions.get(state, {}).items():
                    if char != "ε":
                        move_map[char].update(next_states)

            for char, next_states in move_map.items():
                next_set = frozenset(next_states)
                if next_set not in dfa_states:
                    dfa_states[next_set] = f"q{state_count}"
                    state_count += 1
                    queue.append(next_set)
                dfa_transitions[current_name][char] = dfa_states[next_set]

            if nfa.accept_state in current_set:
                accept_states.add(current_name)

        return DFA(dfa_states[start_set], accept_states, dfa_transitions)

    def match(self, string):
        """Check if the DFA accepts a given string."""
        current_state = self.start_state
        for char in string:
            current_state = self.transitions[current_state].get(char)
            if current_state is None:
                return False
        return current_state in self.accept_states
