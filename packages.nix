{
  self,
  inputs,
  ...
}:
let
  inherit (inputs.nixpkgs.lib.attrsets)
    mapAttrs
    mergeAttrsList
    ;
  inherit (inputs.nixpkgs.lib) genAttrs;
in
{
  perSystem =
    { pkgs, poetry2nix-instance, ... }:
    let
      inherit (poetry2nix-instance) mkPoetryApplication mkPoetryEnv;

      extraPackages = [ pkgs.gcc ];
    in
    {
      packages = rec {
        stresolve = mkPoetryApplication {
          projectDir = self;
          inherit extraPackages;
        };
        default = stresolve;
      };
    };
}
