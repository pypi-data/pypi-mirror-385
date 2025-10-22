# Usage

`pip install revisitpy_server`

or

`uv add revisitypy_server`

```python
```

# Development

1. Pulling latest copy of the study repo
2. Changing env files to use "/" instead of "/study/"
3. `yarn run build`
4. Copy "dist" directory into "src/revisitpy_server"
5. Delete static directory
6. Rename dist to static
7. Update pyproject.toml with new version
8. build and push