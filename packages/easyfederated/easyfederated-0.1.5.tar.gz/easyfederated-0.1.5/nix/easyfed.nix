{inputs, ...}: {
  imports = [inputs.treefmt-nix.flakeModule inputs.pre-commit-hooks.flakeModule];
  perSystem = {
    pkgs,
    lib,
    ...
  }: let
    python = (import ./venv.nix) {inherit inputs pkgs lib;};
    venv = python.pythonSet.mkVirtualEnv "easyfed_venv" python.workspace.deps.all;
    easyfedPkg = pkgs.writeShellScriptBin "easyfed" ''
      exec -a easyfed ${venv}/bin/easyfed "$@"
    '';
    pytest = pkgs.stdenv.mkDerivation {
      name = "easyfed-pytest";
      src = ../.;
      nativeBuildInputs = [
        venv
      ];
      dontConfigure = true;
      # Because this package is running tests, and not actually building the main package
      # the build phase is running the tests.
      #
      # In this particular example we also output a HTML coverage report, which is used as the build output.
      buildPhase = ''
        runHook preBuild
        pytest
        runHook postBuild
      '';
      installPhase = ''
        mkdir -p $out
        # publish the coverage report to $out
        if [ -d htmlcov ]; then
          cp -r htmlcov $out/
        fi
        # at minimum, leave a success marker
        echo "pytest passed on $(date -u)" > $out/ok
      '';
    };
    # mypy = pkgs.stdenv.mkDerivation {
    #   name = "easyfed-mypy";
    #   src = ../src;
    #   nativeBuildInputs = [
    #     venv
    #   ];
    #   dontConfigure = true;
    #   buildPhase = ''
    #     runHook preBuild
    #     mypy .
    #     runHook postBuild
    #   '';
    #   installPhase = ''
    #     mkdir -p $out
    #     cp mypy.txt $out/
    #     # fail the build if mypy found errors (non-zero exit was already handled)
    #     echo "mypy passed on $(date -u)" > $out/ok
    #   '';
    # };
  in {
    packages.easyfed = easyfedPkg;
    apps.easyfed = {
      type = "app";
      program = easyfedPkg;
      meta.description = "EasyFed: A python library for making federated learning easy";
    };
    checks = {
      # TODO: Add mypy when we fix the issues
      # inherit mypy pytest;
      inherit pytest;
    };
  };
}
