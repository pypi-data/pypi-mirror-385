{inputs, ...}: {
  imports = [
    inputs.mkdocs-flake.flakeModules.default
  ];
  perSystem = {
    pkgs,
    lib,
    ...
  }: let
    python = (import ./venv.nix) {inherit inputs pkgs lib;};
  in {
    documentation.mkdocs-root = ../docs;
    documentation.mkdocs-package = python.pythonSet.mkVirtualEnv "mkdocs-env" python.workspace.deps.all;
  };
}
