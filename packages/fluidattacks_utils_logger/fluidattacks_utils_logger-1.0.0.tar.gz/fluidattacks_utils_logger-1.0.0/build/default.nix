{ nixpkgs, pynix, src, }:
let
  deps = import ./deps { inherit nixpkgs pynix; };
  requirements = python_pkgs: {
    runtime_deps = with deps.python_pkgs; [ bugsnag fa-purity ];
    build_deps = with deps.python_pkgs; [ flit-core ];
    test_deps = with deps.python_pkgs; [
      arch-lint
      mypy
      pytest
      pytest-cov
      ruff
    ];
  };
in {
  inherit src requirements;
  root_path = "observes/common/utils-logger";
  module_name = "fluidattacks_utils_logger";
  pypi_token_var = "UTILS_LOGGER_TOKEN";
  defaultDeps = deps.python_pkgs;
  override = b: b;
}
