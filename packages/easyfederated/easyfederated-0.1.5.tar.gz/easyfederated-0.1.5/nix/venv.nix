{
  inputs,
  pkgs,
  lib,
  ...
}: let
  workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = ../.;
  };
  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  pyprojectOverrides = import "${inputs.mkdocs-flake}/uv-overrides.nix";

  hacks = pkgs.callPackage inputs.pyproject-nix.build.hacks {};

  ov = final: prev: {
    antlr4-python3-runtime = prev.antlr4-python3-runtime.overrideAttrs (old: {
      buildInputs = (old.buildInputs or []) ++ final.resolveBuildSystem {setuptools = [];};
    });
    pytorch-triton-rocm = prev.pytorch-triton-rocm.overrideAttrs (old: {
      buildInputs =
        old.buildInputs
        ++ [
          pkgs.zstd
          pkgs.xz
          pkgs.libz
          pkgs.bzip2
        ];
    });
    nvidia-cufile-cu12 = prev.nvidia-cufile-cu12.overrideAttrs (old: {
      buildInputs =
        old.buildInputs
        ++ [
          pkgs.rdma-core
          pkgs.rocmPackages.rocblas
        ];
    });
    bitsandbytes = hacks.nixpkgsPrebuilt {
      from = pkgs.python312Packages.bitsandbytes;
    };
    torch = hacks.nixpkgsPrebuilt {
      from = pkgs.python312Packages.torch;
    };
    torchvision = hacks.nixpkgsPrebuilt {
      from = pkgs.python312Packages.torchvision;
    };
    nvidia-cusolver-cu12 = prev.nvidia-cusolver-cu12.overrideAttrs (old: {
      buildInputs =
        old.buildInputs
        ++ [
          pkgs.rdma-core
          pkgs.rocmPackages.rocblas
          pkgs.cudatoolkit
        ];
    });
    nvidia-cusparse-cu12 = prev.nvidia-cusparse-cu12.overrideAttrs (old: {
      buildInputs =
        old.buildInputs
        ++ [
          pkgs.rdma-core
          pkgs.rocmPackages.rocblas
          pkgs.cudatoolkit
        ];
    });
  };

  python = pkgs.python312;

  pythonSet =
    (pkgs.callPackage inputs.pyproject-nix.build.packages {
      inherit python;
    }).overrideScope
    (
      lib.composeManyExtensions [
        ov
        inputs.pyproject-build-systems.overlays.default
        overlay
        pyprojectOverrides
      ]
    );
in {
  inherit workspace;
  pythonSet = pythonSet.overrideScope ov;
}
