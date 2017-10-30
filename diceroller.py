import random

def roll_n_die(n):
    if(n <= 0):
        return 0
    return random.randrange(0, n) + 1

def roll_xda(x, a, explode=False, e_target=0, e_num=1):
    rolls = []
    if(explode and e_target <= 0):
        return []
    for n in range(x):
        r = roll_n_die(a)
        rolls.append(r)
        if(explode and r >= e_target):
            rolls.extend(roll_xda(e_num, a, explode=explode, e_target=e_target, e_num=e_num))
    return rolls

def roll_xda_successes(x, a, s, explode=False, e_target=0, e_num=1):
    rolls = roll_xda(x, a, explode, e_target, e_num)
    successes = [1 if r >= s else 0 for r in rolls]
    return (successes, rolls)

def keep_n(rolls, num, highest):
    rolls = sorted(rolls, reverse=highest)
    if(num < len(rolls)):
        return rolls[:num]
    return rolls

def drop_n(rolls, num, highest):
    rolls = sorted(rolls, reverse=highest)
    if(num >= len(rolls)):
        return []
    elif(num <= 0):
        return rolls
    return rolls[:len(rolls) - num]

def roll_with_options(x, a, success, s_target, explode, e_target, e_num, keep, k_num, k_highest, drop, d_num, d_highest):
    print('x:',x,'a:',a,'success:',success,'s_target:',s_target,'explode:',explode,'e_target:',e_target,'e_num:',e_num,'keep:',keep,'k_num:',k_num,'k_highest:',k_highest,'drop:',drop,'d_num:',d_num,'d_highest:',d_highest)
    base_rolls = roll_xda(x, a, explode, e_target, e_num)
    if(success):
        successes = [1 if r >= s_target else 0 for r in base_rolls]
        successes = keep_n(successes, k_num, k_highest) if keep else successes
        successes = drop_n(successes, d_num, d_highest) if drop else successes
        return (successes, base_rolls)
    rolls = keep_n(base_rolls, k_num, k_highest) if keep else base_rolls
    rolls = drop_n(rolls, d_num, d_highest) if drop else rolls
    return (rolls, base_rolls)

def total_rolls(rolls, mod=0, add=True):
    total = mod if add else -mod
    for n in rolls:
        total += n
    return total
