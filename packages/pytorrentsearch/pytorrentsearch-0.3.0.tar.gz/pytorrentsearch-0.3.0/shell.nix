{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python3Packages.pylsp-mypy
    python3Packages.flake8
    python3Packages.black
    python3Packages.coverage
    python3Packages.pytest
    isort
  ];
}
