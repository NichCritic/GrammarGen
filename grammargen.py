import functools
import itertools
import sys

def start(s, fns):
    return fns[0](s[0], s[1:], fns[1:])

def match_one(current, rest, next_fns, character=None, args=None):
    # If we don't match, this is false
    if not current == character:
        return {"match":False}
    #If there's string left over but nothing to match, the rule is false
    if rest and not next_fns:
        return {"match":False}
    #If we match and there's no characters left to process and nothing to process them, then we return success
    if not rest and not next_fns:
        return {"match":True, "args": args}
    #If we're at the end and there's still functions, try sending them empty strings. match_one fails as expected, match_n succeeds, capturing nothing
    if next_fns and not rest:
        return next_fns[0]("", "", next_fns[1:], args=args)
    #Finally, if there are character to process and functions to process them, delegate to them
    #(Our success is implied by not failing)
    return next_fns[0](rest[0], rest[1:], next_fns[1:], args=args)

def match_n_and_capture(current, rest, next_fns, character=None, args=None):
    myargs = {} if args == None else args
    if not character in myargs:
        myargs[character] = ""
    
    #If we are the last character in the rule we want to capture everything and return    
    if not next_fns:
        #Current and rest can be ""
        myargs[character] = myargs[character] + current + rest
        return {"match": True, "args":myargs}

    #Reaching here implies we are not the last rule. If there are no characters after us or we aren't currently processing a character,
    #then this rule can't match, so we return that
    if not rest:
        return {"match": False}
    if not current:
        return {"match": False}

    #We are processing a character, there's at least one character coming up, and a function to handle it

    #Check to see if the next symbol matches this character. If so, this symbol can just defer to that result
    lookahead = next_fns[0](current, rest, next_fns[1:], args=args)
    if lookahead["match"]:
        if "args" in lookahead:
            myargs.update(lookahead["args"])
        lookahead["args"] = myargs
        return lookahead
    else:
        #Otherwise capture this symbol in the args list and process the next character
        myargs[character] = myargs[character] + current 
        return match_n_and_capture(rest[0], rest[1:], next_fns, character = character, args=myargs)


#These functions are straightforward. Just walk through the list adding itself or the captured argument and delegate to the next
def replace_one(current, next_fns, character=None, args=None):
    current = current + character
    if not next_fns:
        return current
    return next_fns[0](current, next_fns[1:], args = args)

def replace_n(current, next_fns, character=None, args=None):
    current = current + args[character]
    if not next_fns:
        return current
    return next_fns[0](current, next_fns[1:], args = args)


def apply_rule(s, rule):
    match = start(s, rule["rule"])
    if not s:
        return []
    if not match["match"]:
        return []
    else:
        return [rule["replace"][0]("", rule["replace"][1:], args=match["args"])] + concat_each(s[0], apply_rule(s[1:], rule))

def concat_each(s, l):
    return [s+ls for ls in l]



def string_to_rule(rule_string, rule_symbols, sub_symbols):
    rule, sub = rule_string.split("->")
    rule = rule.strip()
    sub = sub.strip()

    rule_fns = []
    for c in rule:
        if not c in rule_symbols:
            if c.islower():
                rule_symbols[c] = functools.partial(match_n_and_capture, character=c)
            else:
                rule_symbols[c] = functools.partial(match_one, character=c)
        rule_fns.append(rule_symbols[c])
    sub_fns = []
    for c in sub:
        if not c in sub_symbols:
            if c.islower():
                sub_symbols[c] = functools.partial(replace_n, character=c)
            else:
                sub_symbols[c] = functools.partial(replace_one, character=c)
        sub_fns.append(sub_symbols[c])

    return {"rule":rule_fns, "replace":sub_fns}, rule_symbols, sub_symbols


def strings_to_rules(rule_strings, rule_symbols, sub_symbols):
    rules = []
    for r_s in rule_strings:
        rule, rule_symbols, sub_symbols = string_to_rule(r_s, rule_symbols, sub_symbols)
        rules.append(rule)
    return rules



if __name__ == "__main__":
    _, rule_file, axiom_file = sys.argv
    rule_strings = []
    with open(rule_file) as rules:
        rule_strings = rules.readlines()

    axiom_strings = []
    with open(axiom_file) as axioms:
        axiom_strings = axioms.readlines()

    rules_from_string = strings_to_rules(rule_strings, {}, {})

    theorems = axiom_strings[:]

    idx = 0
    for i in range(50):
        s = theorems[idx]
        print(s)
        for rule in rules_from_string:
            n_s = apply_rule(s, rule)
            if n_s:
                theorems.extend(n_s)
        idx = idx + 1

    
