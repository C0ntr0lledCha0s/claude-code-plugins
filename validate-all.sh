#!/bin/bash
# Quick plugin validation script

echo "Validating all plugins..."
echo ""

ERRORS=0

# Dynamically discover plugins by finding directories with .claude-plugin/plugin.json
PLUGINS=()
for plugin_json in */.claude-plugin/plugin.json; do
    if [ -f "$plugin_json" ]; then
        plugin_dir=$(dirname "$(dirname "$plugin_json")")
        PLUGINS+=("$plugin_dir")
    fi
done

if [ ${#PLUGINS[@]} -eq 0 ]; then
    echo "No plugins found!"
    exit 1
fi

# Validate each plugin's hooks
for plugin in "${PLUGINS[@]}"; do
    echo "Checking $plugin..."

    # Validate hooks if they exist
    if [ -f "$plugin/hooks/hooks.json" ]; then
        if python3 agent-builder/skills/building-hooks/scripts/validate-hooks.py "$plugin/hooks/hooks.json" 2>&1 | grep -q "is valid"; then
            echo "  ✓ hooks.json valid"
        else
            echo "  ✗ hooks.json invalid"
            ((ERRORS++))
        fi
    fi

    # Validate plugin.json
    if python3 -m json.tool "$plugin/.claude-plugin/plugin.json" >/dev/null 2>&1; then
        echo "  ✓ plugin.json valid"
    else
        echo "  ✗ plugin.json invalid"
        ((ERRORS++))
    fi
done

# Validate marketplace.json
echo ""
echo "Checking marketplace.json..."
if python3 -m json.tool .claude-plugin/marketplace.json >/dev/null 2>&1; then
    echo "  ✓ marketplace.json valid"
else
    echo "  ✗ marketplace.json invalid"
    ((ERRORS++))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✓ All validations passed!"
    exit 0
else
    echo "✗ Found $ERRORS error(s)"
    exit 1
fi
