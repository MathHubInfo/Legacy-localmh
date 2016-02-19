#!/bin/bash -e
mkdir -p MathHub
for i in coursematerials hwexam meta-inf smglom
do
    lmh install -y HelloWorld/$i
done
cd MathHub
lmh pdf --depsFirst HelloWorld
lmh omdoc --depsFirst --test --expire=-1 HelloWorld
