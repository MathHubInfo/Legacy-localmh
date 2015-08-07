# lmh ls-remote

Lmh ls-remote lists repositories that are available remotely.

All repositories installable by lmh are located on [gl.mathhub.info](http://gl.mathhhub.info). They are simple Git repositories managed by a gitlab instance. The exact location can be configured with the ```install::sources``` setting of [lmh config](config).

For organisational reasons, each repository has a name (for example `sets`) and a group (for example `smglom`) it belongs to. The repositories are refered to by both of these names in a form like `smglom/sets`.

When lmh ls-remote is given a list of parameters, it treats them as globs and then matches these against the list of available repositories. This means when "smglom/\*" is given, all repositories in the smglom group will be matched. The glob syntax expands  \*, ?, and character ranges expressed with []. For a literal match, the meta-characters should be wrapped in brackets. Because most \*nix shells automatically try to expand these globs, it is required to quote them manually:

```
lmh ls-remote ‘smglom/*'
```

Because no login into gitlab is required, private and internal repositories might not be caught by ```lmh ls-remote``` globs. When an exact name is given to ls-remote, it automatically determines that this repository exists and will return the given repository.
