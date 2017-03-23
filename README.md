##### What?
pycc is a compiler-compiler built in python. Given a grammar Context Free Grammar (CFG), pycc will generate an
LL-compiler that recognizes strings of that grammar.

pycc also does some basic grammar normalization:
- left factoring
- left recursion removal

##### Why?
As with [rexpy](https://github.com/lsankar4033/rexpy), inspiration originally struck while reading about
context free grammars and their compilation in Michael Sipser's
[Introduction to the Theory of Computation](https://www.amazon.com/Introduction-Theory-Computation-Michael-Sipser/dp/113318779X).

I find compilers fascinating as they represent the translation from serial information into a grammatical tree
that can represent thought.

##### How?
In addition to Sipser's book, I referred to MIT and Stanford course notes on compilers for building my
LL-compiler
generator. [This](http://web.stanford.edu/class/archive/cs/cs143/cs143.1128/handouts/090%20Top-Down%20Parsing.pdf)
handout was particularly useful and most of the techniques I use come directly from it.

##### TODO
- read BNF grammar from file
- add usage with BNF reader to README
- add indirect left recursion removal to normalization
- add escape characters to grammar (optional)
- docstrings where appropriate
