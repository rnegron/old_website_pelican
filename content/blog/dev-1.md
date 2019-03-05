title: Identity and Equality in Python
date: 2018-07-27
slug: dev-python-strings-identity-vs-equality
category: blog
tags: python, django, programming


I would consider [Python](https://www.python.org/) to be the programming language I'm most comfortable writing code in. There's plenty to love, and one of its more recognizable features is its simple to read [syntax](https://en.wikipedia.org/wiki/Python_syntax_and_semantics). I've heard the phrase "executable pseudocode" thrown around before, and its easy to see where the comparisons come from. 

A great side effect of sporting such a relatively simple to understand syntax is its [mass appeal](https://www.economist.com/science-and-technology/2018/07/21/python-has-brought-computer-programming-to-a-vast-new-audience), with people jumping in with little programming knowledge and using Python to jump start their new coding adventures. 

Its not hard to get carried away and forget that, despite the focus on readability, code is not the same as prose. Its always worthwhile to keep the subtleties of a particular language in mind. That being said, this post is about the bug I created when I forgot about the (perhaps not so subtle) distinction between identity and equality in Python, and what I learned from that mistake.

Let's review the fundamentals before diving into the particulars.

# Object Equality

Object equality refers to the intuitive notion of equality from mathematics. Sounds simple enough. 

```python
x = 3
y = 3
x == y  # True
```

The equality operator is part of Python's built-in [comparison operators](https://docs.python.org/3/library/stdtypes.html?highlight=comparison#comparisons).

From the docs, we see that _"objects of different types, except different numeric types, never compare equal."_ We can test this out as follows:

```python
# Comparison between objects of different types, one non-numeric
x = 1
y = '1'
x == y  # False, x and y are different objects

# Comparison between different numeric types
y = 1.0
type(x)  # <class 'int'>
type(y)  # <class 'float'>
x == y   # True
```

We can also define equality on our own objects by writing an `__eq__()` dunder method:

```python
class Goomba:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        """
        Goomba is equal to other if the sum of their values is even 
        """
        if (self.value + other.value) % 2 == 0:
            return True
        return False

class Koopa:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        """
        Koopa is equal to other if the sum of their values is odd
        """
        if (self.value + other.value) % 2 == 0:
            return False
        return True

goombario = Goomba(1)
goombella = Goomba(2)
kooper = Koopa(1)
koops = Koopa(2)

goombella == goombario  # False, 1 + 2 = 3, 3 % 2 = 1
goombario == goombario  # True,  1 + 1 = 2, 2 % 2 = 0

goombario == kooper     # True,  1 + 1 = 2, 2 % 2 = 0
goombella == kooper     # False, 2 + 1 = 3, 3 % 2 = 1
goombella == koops      # True,  2 + 2 = 4, 4 % 2 = 0
```

You may have noticed something peculiar from the example: due to the way equality was defined in the above classes, the order of the operands matters (the operation is not symmetric in this case).

```python
goombella == kooper     # False, 3 % 2 = 1 (odd for Goomba = false)
kooper == goombella     # True,  3 % 2 = 1 (odd for Koopa = true)
```

[Syntactic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar) is to blame for any confusion here. You can read more [in the Python docs](https://docs.python.org/3/reference/datamodel.html#object.__eq__). 

Digging a bit further, we can see from the [value comparisons for expressions](https://docs.python.org/3/reference/expressions.html#value-comparisons) docs page that it is intended for the `==` operator to be a test for an [equivalence relation](https://en.wikipedia.org/wiki/Equivalence_relation). So the above example, where symmetry is not observed, would not be consistent with the way Python defines equality. In any case, object equality is pretty straightforward from a practical point of view.


# Object Identity

For me, the notion of "identity" is a bit more vague than "equality". What does it mean for two objects to share an identity? While perhaps not as intuitive as object equality, object identity is not much more complicated. In Python, the identity operator is appropriately known as the `is` [operator](https://docs.python.org/3/reference/expressions.html#is).

Basically, `a is b` if and only if `id(a) == id(b)`, where `a` and `b` are objects and `id(x)` is [the memory address of x](https://docs.python.org/3/library/functions.html#id). So, for two objects to be "identical", it must be the case that they are the same exact object! In other words, if two variables share the same object address, there are in fact _not_ two objects but rather two _references_ to the same object.

```python
1 is 1  # True


x = [1, 2, 3]
y = [1, 2, 3]

x == y  # True
x is y  # False
```

There are some subtleties to this that may not be immediately apparent. For example, `[1, 2, 3] is [1, 2, 3]` = `False`. Meanwhile, `(1, 2, 3) is (1, 2, 3)` = `True`. The reason is, as you may suspect, that [lists](https://docs.python.org/3/library/stdtypes.html?highlight=comparison#lists) are mutable while [tuples](https://docs.python.org/3/library/stdtypes.html?highlight=comparison#tuples) are not. 


# Equality vs Identity in Python Strings

Well, what about strings? We know that strings in Python are immutable objects. And as we might expect, `'hello, world' is 'hello, world'` = `True`! But here's where things start to get interesting...

```python
# Example 1
'hello, world' is 'hello, world'  # True

# Example 2
str_1 = 'hello, world'
str_2 = 'hello, world'
str_1 is str_2  # False (!)

# Example 3
str_1 = 'helloworld'
str_2 = 'helloworld'
str_1 is str_2  # True (?!)

# Example 4
str_1 = 'hello, world'
str_2 = 'hello, world'
str_1.replace(', ', '') is str_2.replace(', ', '')  # False(!?!)
```

What gives? And to make things more interesting, the above code was executed line-by-line on the interactive shell. If you copy the above code into a source file and run the entire file (while printing the results), you will find that the first three conditions are `True` (the last one remains `False`). Which means that the second identity operation just changed truth values! And how come removing the comma and whitespace from both strings at the end there didn't make the identity check `True` again? The key to answering all these questions is: [string interning](https://en.wikipedia.org/wiki/String_interning)! Let's talk about it.

## String Interning, or "Compare strings in O(1) instead of O(n)!"

This concept was completely unknown to me until very recently. _String interning_ is the process by which a particular `string` object can be stored in an internal dictionary for faster lookups. Further assignments of the same string contents will yield a reference to this stored object instead of creating a new object.

In practical terms, interning a string allows for lower memory usage as well as a performance boost in matching via string equality. That is, instead of relying on [standard string matching algorithms](https://en.wikipedia.org/wiki/Category:String_matching_algorithms) to determine whether or not two strings are the same (i.e., contain the same characters in the same order), you can simply check whether or not they are references to the same object. This allows an _equality_ check to be optimized as an _identity_ check, which typically means that an _O(n)_ character-by-character operation has been optimized all the way down to an _O(1)_ numerical address comparison. This is quite the optimization, which is why Python natively interns strings based on a set of internal rules. And if we examine some of these rules, we'll find answers to the questions left unsolved in the previous section.

For example, it turns out that Python natively interns all strings which contain only [ASCII](https://en.wikipedia.org/wiki/ASCII) letters, digits and the underscore character. This explains what happened in _Example 3_. Both strings are pure ASCII and therefore got interned by Python (conversely, their comma-and-whitespace-containing `hello, world` counterparts from _Example 2_ were not interned by this rule). Also, it's important to note that native interning occurs at compilation time. This fact explains why `False` was the result in _Example 4_. It would seem that the `replace` method turned our comma-and-whitespace-containing strings into intern-me-ASCII strings, but in fact the string replacement occurred at runtime, and thus never got the chance to be interned natively. 

But how does this explain _Example 1_? Well, Python was smart enough to realize that `'hello, world' is 'hello, world'` is an attempt to compare the reference of two immutable objects which happen to be the same and it optimized accordingly. Now, how come the code exhibits completely different behavior when running in the shell versus in a source file for _Example 2_?  Notice that this same scenario plays out a little differently depending on the execution environment. This is because, in the shell, the code is fed to the Python interpreter line-by-line, as opposed to file execution, where the Python has access to all the code in the file at once. Again, Python was smart enough to optimize the strings when it had forward-lookup capabilities available, but not so when it did not "know" what the next line would be (which was the case for _Example 1_, where it did optimize).

Phew! Now, let's look at how we use manual string interning and get the `is` operator to work as we expected it to originally:
```python
from sys import intern

str_1 = intern('hello, world')
str_2 = intern('hello, world')

print(type(str_1), type(str_2))  # <class 'str'> <class 'str'>
print(str_1 is str_2)  # True
```

There it is! Two different references to the same object. We saved memory by not creating two different objects for the same string, we achieved a performance boost by comparing references instead of the contents of the strings, and we learned a lot about Python strings and objects along the way.

# From a bug, knowledge

I mentioned at the top that I became interested in this whole string identity vs equality thing because of a bug I found (a.k.a created) at work. Here it is, in all its glory:

```python
if database is not 'some_database_alias':
    # ...
```
At first glance, there may not seem to be much of a problem here. However, if the code that is expected to run after the conditional expression is of critical importance, then it pays to make sure that the conditions under which the expression evaluates to true are well understood.

Then came the time for that line of code to do its one job...

```python
database = request.user.database
print(database)  # 'some_database_alias'
print(type(database))  # <class 'str'>
print(database == 'some_database_alias')  # True

print(database is 'some_database_alias')  # False
```

It didn't work. I wrote an identity comparison where I should have written an equality comparison instead. The moral of the story here: __`is` is not `==`__.

# Conclusion

What started out as a casual review of Python syntax caused by a simple enough bug turned into a curiosity-driven deep dive into Python string internals and comparison operators. All in good fun. The following article by Adrien Guillo was very helpful and goes into the lower-level goings on of CPython's string interning mechanisms: [The internals of Python string interning](http://guilload.com/python-string-interning/). Satwik Kansal wrote another, higher-level introduction to the topic: [Do you really think you know strings in Python?](https://www.codementor.io/satwikkansal/do-you-really-think-you-know-strings-in-python-fnxh8mtha) 
