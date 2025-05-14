{
  self,
  inputs,
  ...
}:
{
  perSystem =
    { pkgs, poetry2nix-instance, ... }:
    let
      inherit (poetry2nix-instance) mkPoetryEnv;
      extraPackages = ps: [ pkgs.gcc ];
    in
    {
      devShells.default = pkgs.mkShellNoCC {
        packages = [
          (mkPoetryEnv {
            projectDir = self;
            inherit extraPackages;
          })
          pkgs.poetry
        ];
      };
    };

}
