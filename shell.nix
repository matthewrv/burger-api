let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.python313
    pkgs.uv
    pkgs.python312Packages.ruff
  ];
  shellHook = ''
    uv sync --frozen --no-install-package ruff
    source .venv/bin/activate

    echo "Python version: $(python --version)"
    echo "Python executable: $(which python)"
  '';
}