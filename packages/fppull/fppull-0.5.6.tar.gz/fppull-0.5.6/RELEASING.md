# Releasing

This project uses `setuptools-scm`. The version comes from the tag.

## Steps
1. Land commits on `main`.
2. Tag the release:
   ```bash
   git tag -a vX.Y.Z -m vX.Y.Z
   git push origin vX.Y.Z

### Patch cut (one-liner)

### Safety flags

- `--dry-run`: print commands without executing
- `--confirm`: interactive y/N before tagging/pushing
- `--force`: bypass dirty-tree guard (use sparingly)

#### Examples
```bash
scripts/release-cut.sh v0.5.5 v0.5.4 --dry-run
scripts/release-cut.sh v0.5.5 v0.5.4 --confirm
scripts/release-cut.sh v0.5.5 v0.5.4 --force
```

```bash
scripts/release-cut.sh v0.5.4 v0.5.3
```
