# AUPL
## Introduction
AUPL is a stack-based programming language like Forth.\
It is inspired somewhat by Forth.
## Example
Unlike Forth, AUPL uses `out` to print, not `.`.\
```
1; % pushes 1 to stack
out; % remove last inserted element from stack and print
```
The syntax also differs when printing strings
> in AUPL
```
"Hello World"; % pushes "Hello World" to stack
out;
```
> in Forth
```
." Hello World"
```
Use `:` to define a function
```
:helloWorld "Hello World" out.
```
No `;` is needed to end a function definition.
