# lmh selfupdate

The selfupdate command can be used to upgrade lmh itself. Internally, this is equivalent to:
```
lmh setup --update self
```

and just runs a ```git pull``` on the lmh root directory as well as some post-update scripts. 
