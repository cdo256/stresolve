# stresolve

Resolve syncthing conflicts interactively.

Part of this script is based off [solarkraft's script](https://gist.github.com/solarkraft/26fe291a3de075ae8d96e1ada928fb7d).

Flake is included. You can run the script by using `nix`:

```
$ nix run -- /path/to/syncthing/dir
```

Alternatively, to edit the script you can use a nix shell:

```
$ nix develop
$ poetry run python -m stresolve -- /path/to/syncthing/dir
```
