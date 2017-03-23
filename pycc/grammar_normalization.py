"""Module for carrying out grammar normalization to make a grammar LL-parseable.

Currently, this module does:
- left recursion removal
- left factoring
"""

from collections import defaultdict
from pycc.grammar import Grammar, Rule, NSym, TSym
from pycc.constants import EPSILON_CHAR, END_SYMBOL

def _is_left_recursive(rule):
    return rule.sym == rule.exp_syms[0]

def nonterminal_generator(rules):
    """Generator that continuously provides new nonterminal symbols to be used in rules. Avoids collision with
    the rule set specified.

    Currently just iterates from the last ord used in specified rule nonterminals.
    """
    used = [ord(rule.sym.char) for rule in rules]
    used.sort()
    i = used[-1]

    while True:
        i += 1
        yield chr(i)

def _lrr_split_symbol_rules(symbol_rules, nonterminal_gen):
    """Given all the rules for a given symbol, creates a new set of rules by eliminating any left recursive
    rules. If no left recursive rules exist, just returns the original rules.
    """
    symbol_rules = [rule for rule in symbol_rules if rule.exp_syms != [rule.sym]]

    if not any([_is_left_recursive(rule) for rule in symbol_rules]):
        return symbol_rules

    new_rules = []

    new_symbol = NSym(next(nonterminal_gen))
    old_symbol = symbol_rules[0].sym

    found_non_recursive_rule = False
    for rule in symbol_rules:
        if rule.exp_syms[0] == rule.sym:
            new_rules.append(
                Rule(new_symbol,
                     rule.exp_syms[1:] + [new_symbol]))
        else:
            found_non_recursive_rule = True
            # NOTE - insert to front to preserve property that start_symbol is identified by first rule
            new_rules.insert(0,
                             Rule(old_symbol,
                                  rule.exp_syms + [new_symbol]))

    if found_non_recursive_rule:
        new_rules.append(
            Rule(new_symbol,
                 [TSym(EPSILON_CHAR)]))
    else:
        new_rules.insert(0, Rule(old_symbol, [new_symbol]))

    return new_rules

def remove_duplicates(seq):
    """Helper method for removing duplicates while preserving order of first occurrence of each elt
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def rules_for_symbol(rules, symbol):
    return [rule for rule in rules if rule.sym == symbol]

def remove_left_recursion(grammar, nonterminal_gen = None):
    """Returns a new set of rules with all left recursion removed. Optionally takes a generator for new
    symbols, but otherwise generates symbols based on the lexicographically last symbol in the provided rules.
    """
    if nonterminal_gen is None:
        nonterminal_gen = nonterminal_generator(grammar.rules)

    new_rules = []
    old_nonterminals = remove_duplicates([rule.sym for rule in grammar.rules])
    for nonterminal in old_nonterminals:
        new_rules.extend(
            _lrr_split_symbol_rules(rules_for_symbol(grammar.rules, nonterminal), nonterminal_gen))

    return Grammar(new_rules, grammar.start_symbol)

def longest_common_prefix(exp_syms1, exp_syms2):
    prefix = []
    for i in range(min(len(exp_syms1), len(exp_syms2))):
        if exp_syms1[i] != exp_syms2[i]:
            break

        prefix.append(exp_syms1[i])

    return tuple(prefix)

def _lf_split_symbol_rules(symbol_rules, nonterminal_gen):
    symbol = symbol_rules[0].sym

    prefix_map = defaultdict(set)
    reverse_prefix_map = defaultdict(set)
    factored_rule_indices = set()
    for i in range(len(symbol_rules)):
        for j in range(i + 1, len(symbol_rules)):
            prefix = longest_common_prefix(symbol_rules[i].exp_syms,
                                           symbol_rules[j].exp_syms)

            if len(prefix) > 0:
                prefix_map[prefix] |= set([i,j])
                reverse_prefix_map[i].add(prefix)
                reverse_prefix_map[j].add(prefix)
                factored_rule_indices |= set([i,j])

    # For rules with multiple shared prefixes, pick the largest one and remove all others
    for i, prefixes in reverse_prefix_map.items():
        if len(prefixes) > 1:
            longest_prefix = max(prefixes, key=len)
            for prefix in prefixes:
                if prefix != longest_prefix:
                    prefix_map[prefix].discard(i)

    # Remove all prefixes with only 1 item
    updated_prefix_map = {}
    for prefix, indices in prefix_map.items():
        if len(indices) > 1:
            updated_prefix_map[prefix] = indices
        else:
            factored_rule_indices -= indices

    new_rules = []
    for prefix_tuple, indices in updated_prefix_map.items():
        new_sym = NSym(next(nonterminal_gen))

        prefix = list(prefix_tuple)
        new_rules.append(Rule(symbol, prefix + [new_sym]))
        for i in indices:
            original_exp = symbol_rules[i].exp_syms
            new_exp = original_exp[len(prefix):]
            if len(new_exp) is 0:
                new_exp = [TSym(EPSILON_CHAR)]
            new_rules.append(Rule(new_sym, new_exp))

    for i in range(len(symbol_rules)):
        if i not in factored_rule_indices:
            new_rules.append(symbol_rules[i])

    return new_rules

def left_factor(grammar, nonterminal_gen = None):
    """Removes common left factors that may exist for any nonterminal. Optionally takes a generator for new
    symbols, but otherwise generates symbols based on the lexicographically last symbol in the provided rules.
    """
    if nonterminal_gen is None:
        nonterminal_gen = nonterminal_generator(grammar.rules)

    new_rules = []
    old_nonterminals = remove_duplicates([rule.sym for rule in grammar.rules])
    for nonterminal in old_nonterminals:
        new_rules.extend(
            _lf_split_symbol_rules(rules_for_symbol(grammar.rules, nonterminal), nonterminal_gen))

    return Grammar(new_rules, grammar.start_symbol)
