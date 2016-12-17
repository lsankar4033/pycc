# Technique taken from this document:
# http://web.stanford.edu/class/archive/cs/cs143/cs143.1128/handouts/090%20Top-Down%20Parsing.pdf

from copy import deepcopy
from pycc.grammar import NSym, TSym

EPSILON_CHAR = ''
END_SYMBOL = 'EOF'

def build_parse_table(rules, first_sets, follow_sets):
    parse_table = {}

    for rule in rules:
        (first_sets, first_chars) = _get_next_terminals(rules, first_sets, rule.exp_syms, 0)

        sym_char = rule.sym.char
        for c in first_chars:
            if c is not EPSILON_CHAR:
                _add_to_parse_table(parse_table, sym_char, c, rule)

        if EPSILON_CHAR in first_chars:
            follow_chars = follow_sets[sym_char]
            for c in follow_chars:
                _add_to_parse_table(parse_table, sym_char, c, rule)

    return parse_table

def _add_to_parse_table(parse_table, nonterm, term, rule):
    parse_table_exp = [str(s) for s in rule.exp_syms]
    if (nonterm, term) in parse_table and parse_table[(nonterm, term)] is not parse_table_exp:
        raise ValueError("Received non LL(1) grammar! {} -> {} appears more than once in parse table.".format(nonterm, term))

    parse_table[(nonterm, term)] = parse_table_exp

# TODO - make sure we can't enter this method for cyclic first_set dependencies
# I.e. if a first set depends on another first set that depends on the first one. This should be detected.
def build_first_sets(rules):
    first_sets = {}
    nonterm_syms = set([rule.sym for rule in rules])

    for sym in nonterm_syms:
        if sym.char not in first_sets:
            first_sets = _add_sym_to_first_sets(sym, rules, first_sets)

    return first_sets

def _add_sym_to_first_sets(sym, rules, first_sets):
    sym_rules = [rule for rule in rules if rule.sym == sym]
    sym_first_sets = set()

    for rule in sym_rules:
        (first_sets, next_terminals) = _get_next_terminals(rules, first_sets, rule.exp_syms, 0)
        sym_first_sets |= next_terminals

    first_sets[sym.char] = sym_first_sets
    return first_sets

def build_follow_sets(rules, first_sets):
    start_sym = rules[0].sym

    follow_sets = {start_sym.char: set([END_SYMBOL])}
    follow_dependencies = {} # Map of A -> {B,...} representing that NSym A's set depends on NSym B's set

    for rule in rules:
        (follow_sets, follow_dependencies) = _process_rule_follow(rule,
                                                                  rules,
                                                                  first_sets,
                                                                  follow_sets,
                                                                  follow_dependencies)

    # Topo-sort nodes by dependency, then in reverse topo-sort order, list dependencies for each node
    sorted_syms = topo_sort(follow_dependencies)
    sorted_syms.reverse()

    for sym in sorted_syms:
        if sym in follow_dependencies:
            for dep in follow_dependencies[sym]:
                follow_sets[sym] |= follow_sets[dep]

    return follow_sets

def topo_sort(g_in):
    """Implementation of Kahn's algorithm to get a topological sort from a graph.
    """
    g = deepcopy(g_in)

    # Reverse dependencies to help in Kahn's algorithm
    gr = {}
    for s in g:
        ts = g[s]
        for t in ts:
            if t not in gr:
                gr[t] = set()

            gr[t].add(s)

    S = set(g.keys()) - set(gr.keys())
    ret = []

    while len(S) > 0:
        n = S.pop()
        ret.append(n)
        to_remove = []
        if n in g:
            for m in g[n]:
                gr[m].remove(n)
                to_remove.append((n,m))
                if len(gr[m]) is 0:
                    S.add(m)

        for (n,m) in to_remove:
            g[n].remove(m)

    for n in g:
        if len(g[n]) > 0:
            raise ValueError("Cyclic dependency encountered during topological sort!")

    return ret

def _process_rule_follow(rule, all_rules, first_sets, follow_sets, dependencies):
    """Process a single rule during follow set computation. This method doesn't fully compute follow sets, but
    instead does whatever it can with first_sets and tracks follow set dependencies to later be processed in
    topological sort order.
    """
    new_dependencies = dependencies.copy()
    new_follow_sets = follow_sets.copy()

    nsyms = [sym for sym in rule.exp_syms if type(sym) is NSym]

    for sym in nsyms:
        if sym.char not in new_follow_sets:
            new_follow_sets[sym.char] = set()
        if sym.char not in new_dependencies:
            new_dependencies[sym.char] = set()

        sym_ind = rule.exp_syms.index(sym)

        if sym_ind is len(rule.exp_syms) - 1 and sym.char != rule.sym.char:
            new_dependencies[sym.char].add(rule.sym.char)

        else:
            (first_sets, next_terminals) = _get_next_terminals(all_rules,
                                                               first_sets,
                                                               rule.exp_syms,
                                                               sym_ind + 1)

            if EPSILON_CHAR in next_terminals and sym != rule.sym:
                new_dependencies[sym.char].add(rule.sym.char)

            next_terminals.discard(EPSILON_CHAR)
            new_follow_sets[sym.char] |= next_terminals

    return (new_follow_sets, new_dependencies)

def _add_sym_to_follow_sets(sym, rules, first_sets, follow_sets):
    sym_follow_sets = follow_sets[sym.char] if sym.char in follow_sets else set()
    rules_with_sym = [rule for rule in rules if sym in rule.exp_syms]

    for rule in rules_with_sym:
        sym_ind = rule.exp_syms.index(sym)

        if sym_ind is len(rule.exp_syms) - 1:
            if rule.sym.char not in follow_sets:
                follow_sets = _add_sym_to_follow_sets(rule.sym, rules, first_sets, follow_sets)

            sym_follow_sets |= follow_sets[rule.sym.char]

        else:
            i = sym_ind + 1
            has_trailing_epsilon = True
            while has_trailing_epsilon and i < len(rule.exp_syms):
                has_trailing_epsilon = False
                next_sym = rule.exp_syms[i]

                if type(next_sym) is TSym:
                    sym_follow_sets.add(next_sym.char)

                else:
                    next_terms = first_sets[next_sym.char]
                    if EPSILON_CHAR in next_terms:
                        has_trailing_epsilon = True
                        to_add = next_terms.copy()
                        to_add.remove(EPSILON_CHAR)

                        sym_follow_sets |= to_add

                    else:
                        to_add = next_terms.copy()

                        sym_follow_sets |= to_add

                i += 1

            if has_trailing_epsilon and i is len(rule.exp_syms) and len(sym_follow_sets) is 0:
                # TODO - this code is duplicated above
                if rule.sym.char not in follow_sets:
                    follow_sets = _add_sym_to_follow_sets(rule.sym, rules, first_sets, follow_sets)

                sym_follow_sets |= follow_sets[rule.sym.char]

    follow_sets[sym.char] = sym_follow_sets
    return follow_sets

def _get_next_terminals(rules, first_sets, syms, start_ind):
    """Given a sequence of symbols and previously calculated first_sets, will determine all terminals that
    follow immediately after the specified index. The returned set will include EPSILON_CHAR if it's possible
    for no terminal to follow the specified index based on the syms provided.

    This method returns a tuple of (first_sets, next_terminals), where first_sets will include any new
    first_sets computed and next_terminals is the aforementioned set

    This method is used in first_set computation, follow_set computation, and parse_table computation.
    """
    next_terminals = set()

    i = start_ind
    has_trailing_epsilon = True
    while has_trailing_epsilon and i < len(syms):
        next_sym = syms[i]
        has_trailing_epsilon = False

        if type(next_sym) is TSym:
            next_terminals.add(next_sym.char)

        else:
            if next_sym.char not in first_sets:
                first_sets = _add_sym_to_first_sets(next_sym, rules, first_sets)

            next_sym_first_chars = first_sets[next_sym.char]
            if EPSILON_CHAR in next_sym_first_chars:
                has_trailing_epsilon = True
                to_add = next_sym_first_chars.copy()
                to_add.remove(EPSILON_CHAR)

                next_terminals |= to_add

            else:
                to_add = next_sym_first_chars.copy()

                next_terminals |= to_add

        i += 1

    if has_trailing_epsilon and i is len(syms):
        next_terminals.add(EPSILON_CHAR)

    return (first_sets, next_terminals)

class LLParser:
    # We may want to add some helpers for converting a string to rules, etc.
    # Assume that the first rule supplied is the start rule
    def __init__(self, rules):
        # TODO add some basic rule validation
        # - no nonterminal symbols used without
        # TODO add some grammar transformation (remove left recursion, left factoring)
        self.start_symbol = rules[0].sym.char
        self.nonterminals = set([rule.sym.char for rule in rules])

        first_sets = build_first_sets(rules)
        follow_sets = build_follow_sets(rules, first_sets)
        self.parse_table = build_parse_table(rules, first_sets, follow_sets)

    def parse(self, s):
        parse_stack = [END_SYMBOL, self.start_symbol]
        i = 0

        s_list = list(s) + [END_SYMBOL]
        while i < len(s_list):

            # successful full match
            if parse_stack[-1] == END_SYMBOL and s_list[i] == END_SYMBOL:
                return True

            # match
            elif parse_stack[-1] == s_list[i]:
                parse_stack.pop()
                i += 1

            # predict attempt
            elif parse_stack[-1] != s_list[i] and parse_stack[-1] in self.nonterminals:
                X = parse_stack.pop()
                a = s_list[i]

                # predict miss
                if (X, a) not in self.parse_table:
                    return False

                syms = self.parse_table[(X, a)].copy()
                syms.reverse()

                parse_stack = parse_stack + [sym for sym in syms if sym is not EPSILON_CHAR]

            # mismatch
            else:
                return False

        return True
