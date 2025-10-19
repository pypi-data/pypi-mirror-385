{inputs, ...}: {
  imports = [
    inputs.pre-commit-hooks.flakeModule
  ];
  perSystem = _: {
    pre-commit = {
      check.enable = true;
      settings = {
        enable = true;
        hooks = {
          commitizen.enable = true;
          treefmt = {
            enable = true;
            pass_filenames = false;
          };
        };
      };
    };
  };
}
