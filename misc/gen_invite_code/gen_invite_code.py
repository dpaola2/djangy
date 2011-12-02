#!/usr/bin/env python
#
# Generate random invitation codes of the form "adjective adjective noun."
# You can customize the adjectives.txt and nouns.txt files to suit your tastes.
#
# Author: Sameer Sundresh <sameer@sundresh.org>
#

import random, sys

n = 1
if len(sys.argv) > 1:
    n = int(sys.argv[1])

def strip_newlines(lines):
    return map(lambda x: x[:-1], lines)

def choose_word(words):
    return words[random.randint(0, len(words)-1)]

adjectives = strip_newlines(open('adjectives.txt').readlines())
nouns      = strip_newlines(open('nouns.txt').readlines())

for i in range(0, n):
    adj1 = choose_word(adjectives)
    adj2 = choose_word(adjectives)
    while adj1[-1] == adj2[-1]:
        adj2 = choose_word(adjectives)
    # For some reason, results looked better to me when the last letter of
    # the first word came alphabetically before the last letter of the
    # second word.  Clearly, this is a superficial proxy for the actual
    # semantic interaction between adjectives.
    if adj1[-1] > adj2[-1]:
        (adj1, adj2) = (adj2, adj1)
    # Zombie usually sounds better as the second adjective than the first.
    if adj1 == 'zombie':
        (adj1, adj2) = (adj2, adj1)
    noun = choose_word(nouns)

    print "%s %s %s" % (adj1, adj2, noun)
