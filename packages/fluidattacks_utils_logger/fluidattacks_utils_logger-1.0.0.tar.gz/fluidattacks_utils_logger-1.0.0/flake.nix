{
  description = "Log utils for observes packages";

  inputs = {
    observes_flake_builder = {
      url =
        "github:fluidattacks/universe/eff07528e7f89f6ea1a626c74dfeb14d86244dfe?shallow=1&dir=observes/common/std_flake";
    };
  };

  outputs = { self, ... }@inputs:
    let
      build_args = { system, python_version, nixpkgs, pynix }:
        import ./build {
          inherit nixpkgs pynix;
          src = import ./build/filter.nix nixpkgs.nix-filter self;
        };
    in { packages = inputs.observes_flake_builder.outputs.build build_args; };
}
