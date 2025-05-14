{
  self,
  inputs,
  ...
}:
{
  perSystem =
    { pkgs, poetry2nix-instance, ... }:
    let
      inherit (poetry2nix-instance) mkPoetryApplication;

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
