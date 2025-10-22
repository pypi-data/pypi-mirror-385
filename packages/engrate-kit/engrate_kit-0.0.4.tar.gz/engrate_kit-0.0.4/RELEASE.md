## Release new versions to PyPI

To release a new version of the `engrate-kit` package to PyPI, follow these
steps:

1. **Update version** in `pyproject.toml`

2. **Tag the release** (this will trigger the GitHub Action to publish to PyPI).
   For example, to release version `0.0.7`, run:

   ```bash
   git tag v0.0.7 && git push origin v0.0.7
   ```

3. **Verify** at [PyPI](https://pypi.org/project/engrate-kit/)
