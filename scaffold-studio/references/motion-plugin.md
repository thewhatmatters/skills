# Motion plugin — machine-wide install

Source: https://github.com/motiondivision/cursor-plugin (no token).

Destination (override with `MOTION_PLUGIN_DIR`): `~/.cursor/plugins/local/motion`

## Commands (NATIVE fallback)

```bash
git clone --depth 1 https://github.com/motiondivision/cursor-plugin /tmp/motion-cursor-plugin
mkdir -p ~/.cursor/plugins/local
# Remove only this plugin dir, never siblings
rm -rf ~/.cursor/plugins/local/motion
cp -R /tmp/motion-cursor-plugin/plugins/motion ~/.cursor/plugins/local/motion
rm -rf /tmp/motion-cursor-plugin
```

Verify `~/.cursor/plugins/local/motion/.cursor-plugin/plugin.json` exists and
`"name"` is `"motion"`.

Do **not** edit `~/.cursor/mcp.json`. The plugin's `mcp.json` already lists:

- `Motion` → `https://mcp.motion.dev`
- `Motion+` → `https://mcp.motion.dev/plus`

After a **new** copy: fully quit Cursor, reopen, enable **Motion** in
Settings → Plugins if it is off.
