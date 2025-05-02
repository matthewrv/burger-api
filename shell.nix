let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.python313
    pkgs.uv
    pkgs.python312Packages.ruff
    pkgs.py-spy
  ];
  # required for numpy to work correctly
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib/";
  shellHook = ''
    uv sync --frozen --no-install-package ruff
    source .venv/bin/activate

    echo "Python version: $(python --version)"
    echo "Python executable: $(which python)"
  '';
}