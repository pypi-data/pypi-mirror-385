{inputs, ...}: {
  imports = [
    inputs.devshell.flakeModule
  ];
  perSystem = {
    config,
    system,
    ...
  }: let
    pkgs = import inputs.nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };
  in {
    devshells.default = {
      packages = with pkgs; [
        config.treefmt.build.wrapper
        git
        gitRepo
        gnupg
        autoconf
        curl
        procps
        gnumake
        util-linux
        m4
        gperf
        unzip
        cudatoolkit
        linuxPackages.nvidia_x11
        libGLU
        libGL
        xorg.libXi
        xorg.libXmu
        freeglut
        xorg.libXext
        xorg.libX11
        xorg.libXv
        xorg.libXrandr
        zlib
        ncurses5
        stdenv.cc
        binutils
        uv
      ];
      devshell.startup.pre-commit.text = config.pre-commit.installationScript;
      env = [
        {
          name = "CUDA_PATH";
          value = pkgs.cudatoolkit;
        }
        {
          name = "LD_LIBRARY_PATH";
          value = "${pkgs.linuxPackages.nvidia_x11}/lib:${pkgs.ncurses5}/lib";
        }
        {
          name = "EXTRA_LDFLAGS";
          value = "-L/lib -L${pkgs.linuxPackages.nvidia_x11}/lib";
        }
        {
          name = "EXTRA_CCFLAGS";
          value = "-I/usr/include";
        }
        # export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
      ];
    };
  };
}
