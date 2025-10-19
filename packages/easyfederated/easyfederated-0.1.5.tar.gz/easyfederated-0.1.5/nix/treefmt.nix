{inputs, ...}: {
  imports = [
    inputs.treefmt-nix.flakeModule
  ];
  perSystem = {pkgs, ...}: {
    treefmt.config = {
      projectRootFile = "flake.nix";
      package = pkgs.treefmt;
      programs = {
        alejandra.enable = true;
        deadnix.enable = true;
        statix.enable = true;
        mypy = {
          enable = true;
          directories = {
            "easyfed".modules = [
              "src"
            ];
          };
        };
        ruff-check.enable = true;
        ruff-format.enable = true;
      };
    };
  };
}
