#!/bin/bash -e
mkdir MathHub
cd MathHub
mkdir HelloWorld
cd HelloWorld
for i in coursematerials hwexam meta-inf smglom
do
    git clone http://gl.mathhub.info/HelloWorld/$i.git
done
cd ..
lmh pdf --depsFirst HelloWorld
lmh omdoc --depsFirst --test HelloWorld
