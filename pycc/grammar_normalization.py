"""Module for carrying out grammar normalization to make a grammar LL-parseable.

Currently, this module does:
- left recursion removal
- left factoring
"""

from pycc.grammar import Rule, NSym, TSym
from pycc.constants import EPSILON_CHAR, END_SYMBOL

# TODO Add left factoring

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

# Returns all rules produced by the first rule. Should probably also pass in all rules so we can build symbols
# for the new rules
def _split_symbol_rules(symbol_rules, nonterminal_gen):
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

# TODO - Remove indirect recursion
def remove_left_recursion(rules, nonterminal_gen = None):
    """Returns a new set of rules with all left recursion removed. Optionally takes a generator for new
    symbols, but otherwise generates symbols based on the lexicographically last symbol in the provided rules.
    """
    if nonterminal_gen is None:
        nonterminal_gen = nonterminal_generator(rules)

    new_rules = []

    old_nonterminals = remove_duplicates([rule.sym for rule in rules])
    for nonterminal in old_nonterminals:
        rules_to_consider = [rule for rule in rules if rule.sym == nonterminal]

        new_rules.extend(_split_symbol_rules(rules_to_consider, nonterminal_gen))

    return new_rules
