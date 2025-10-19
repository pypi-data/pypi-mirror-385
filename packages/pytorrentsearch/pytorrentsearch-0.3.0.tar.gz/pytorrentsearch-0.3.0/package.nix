{ buildPythonPackage, hatchling, pytest, pytest-cov, mypy }:
buildPythonPackage {
  pname = "pytorrentsearch";
  version = builtins.readFile ./pytorrentsearch/VERSION;

  pyproject = true;
  src = ./.;

  build-system = [ hatchling ];

  nativeCheckInputs = [ pytest pytest-cov mypy ];
}
