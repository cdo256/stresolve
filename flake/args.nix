{ inputs, ... }:
let
  inherit (inputs.nixpkgs.lib.attrsets)
    mapAttrs
    mergeAttrsList
    ;
  inherit (inputs.nixpkgs.lib) genAttrs;
  inherit (inputs.poetry2nix.lib) mkPoetry2Nix mkPoetryApplication;
in
{
  systems = [
    "x86_64-linux"
  ];
  perSystem =
    { system, ... }:
    {
      _module.args = rec {
        pkgs = import inputs.nixpkgs { inherit system; };
        poetry2nix-instance = mkPoetry2Nix { inherit pkgs; };
        extraPackages = [ pkgs.gcc ];
      };
    };
}
