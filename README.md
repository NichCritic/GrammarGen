# GrammarGen
A generator for statements given a certain set of rules

Takes a rule file and an axiom file and prints the first 50 products of applying the rules to the axioms

# Instructions

With python 3.8 installed, run as 
	
	python grammargen.py <rulefile> <axiomfile>

# Rule file format

	xI -> xIU
	Mx -> Mxx
	xIIIy -> xUy
	xUUy -> xy

Format is <Rule> -> <Substitution>
lower case characters match 0..n characters until the next character matches
Captial letters (and really any other character you want) match themselves once
Rules go on their own lines
Any other whitespace is ignored

Axioms are just input as strings, one per line