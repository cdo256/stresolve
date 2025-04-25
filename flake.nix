{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix,
    }:
    let
      inherit (nixpkgs.lib.attrsets)
        mapAttrs
        mergeAttrsList
        ;
      inherit (nixpkgs.lib) genAttrs;
      systems = [
        "x86_64-linux"
      ];
      # FIXME: This is clobbering other systems when more than one system is included.
      # Use flake-utils?
      forEachSystem =
        fn:
        mergeAttrsList (
          map (
            system:
            let
              res = fn nixpkgs.legacyPackages.${system};
            in
            mapAttrs (name: value: {
              ${system} = value;
            }) res
          ) systems
        );
    in
    forEachSystem (
      pkgs:
      let
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication mkPoetryEnv;

        extraPackages = [ pkgs.gcc ];
      in
      {
        packages = {
          default = mkPoetryApplication {
            projectDir = self;
            inherit extraPackages;
          };
        };

        devShells = {
          default = pkgs.mkShellNoCC {
            packages = [
              (mkPoetryEnv {
                projectDir = self;
                #inherit extraPackages;
              })
              pkgs.poetry
            ];
          };
        };
      }
    );
}
