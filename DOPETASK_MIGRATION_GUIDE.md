# dopeTask Migration Guide (Moved)

Canonical migration and upgrade docs now live in:

- `docs/24_UPGRADE_GUIDE.md`
- `docs/23_INTEGRATION_GUIDE.md`

This older root file no longer defines the current migration path. Keep it only as a compatibility pointer for historical references.
dopetask --version  # Should still work

# Run your test suite
pytest
```

### Step 4: Update Documentation

```bash
# Find documentation references
grep -r "dopetask-kernel" . --include="*.md"
grep -r "dopeTask" . --include="*.md" | grep -i package

# Update them manually or with sed
sed -i 's/dopetask-kernel/dopetask/g' $(find . -name "*.md")
```

## Backward Compatibility

### What Still Works

- ✅ `dopetask` CLI command (points to same binary as `dopetask`)
- ✅ All existing functionality
- ✅ All CLI commands and flags
- ✅ Configuration file formats

### What Changed

- ❌ `import dopetask` in Python code (must use `import dopetask`)
- ❌ `pip install dopetask-kernel` (must use `pip install dopetask`)

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'dopetask'`

**Solution**: Update imports to use `dopetask`:
```python
# Change this
import dopetask

# To this
import dopetask
```

### Installation Errors

**Error**: `Could not find a version that satisfies the requirement dopetask-kernel`

**Solution**: Install the new package:
```bash
pip install dopetask
```

### CLI Command Not Found

**Error**: `command not found: dopetask`

**Solution**: Reinstall the package:
```bash
pip install --upgrade dopetask
```

## Verification Checklist

- [ ] `import dopetask` works in Python
- [ ] `dopetask --version` shows 0.1.4
- [ ] `dopetask --version` still works (backward compatibility)
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CI/CD pipelines updated
- [ ] Dependencies updated in all environment files

## Support

For issues with the migration:

1. Check the [dopetask documentation](https://github.com/hu3mann/dopeTask)
2. Review this migration guide
3. Test in a staging environment first
4. Open an issue if you encounter problems

---

*Generated: 2024-02-24*  
*dopeTask Version: 0.1.4*
