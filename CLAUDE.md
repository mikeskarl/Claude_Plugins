# Claude Code Plugins Repository

## Repository Info

- **GitHub:** https://github.com/mikeskarl/Claude_Plugins
- **Local Path:** /Users/mkarl/Claude_Plugins
- **Marketplace Name:** claude-plugins
- **Owner:** mikeskarl

## Quick Commands

### Push Changes to GitHub
```bash
cd /Users/mkarl/Claude_Plugins
git add .
git commit -m "Your commit message"
git push
```

### Update Installed Plugin (after pushing changes)
```
/plugin marketplace update claude-plugins
```
Then restart Claude Code.

## Repository Structure

```
Claude_Plugins/
  .claude-plugin/
    marketplace.json      # Marketplace definition (required)
    plugin.json           # Optional root plugin config
  meeting-transcriber-plugin/
    .claude-plugin/
      plugin.json         # Plugin manifest
    agents/
      meeting-transcriber.md   # Agent definition (exposed to Claude)
    skills/                    # Supporting skills (internal use)
    scripts/                   # Python scripts
    README.md
  README.md
  CLAUDE.md               # This file
```

## Marketplace Schema

The `.claude-plugin/marketplace.json` must follow this schema:

```json
{
  "name": "marketplace-name",        // kebab-case, no spaces (required)
  "owner": {                         // object, not string (required)
    "name": "Your Name",
    "email": "email@example.com"
  },
  "metadata": {                      // optional
    "description": "Description",
    "version": "1.0.0"
  },
  "plugins": [                       // array of plugins (required)
    {
      "name": "plugin-name",         // kebab-case (required)
      "source": "./path-to-plugin",  // must start with ./ (required)
      "description": "...",
      "version": "1.0.0",
      "author": { "name": "..." },
      "strict": false                // false = plugin.json optional
    }
  ]
}
```

## Plugin Schema

Each plugin's `.claude-plugin/plugin.json`:

```json
{
  "name": "plugin-name",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": { "name": "Your Name" },
  "keywords": ["tag1", "tag2"],
  "agents": ["./agents/agent-name.md"],
  "commands": ["./commands/"],
  "hooks": {},
  "mcpServers": {}
}
```

## Key Concepts

### Agents vs Skills
- **Agents** are exposed to Claude Code users (defined in `agents/` folder)
- **Skills** are internal components that agents can reference
- Plugin functionality is exposed via **agents**, not skills directly

### Plugin Sources
- Relative paths: `"./path/to/plugin"` (must start with `./`)
- GitHub: `{ "source": "github", "repo": "owner/repo" }`
- Git URL: `{ "source": "url", "url": "https://..." }`

### strict: false vs true
- `strict: true` (default): Plugin must have its own plugin.json
- `strict: false`: Marketplace entry serves as the manifest if plugin.json missing

## Adding a New Plugin

1. Create plugin directory under repository root:
   ```
   mkdir -p new-plugin/.claude-plugin
   mkdir -p new-plugin/agents
   ```

2. Create plugin.json:
   ```json
   {
     "name": "new-plugin",
     "description": "...",
     "version": "1.0.0",
     "agents": ["./agents/main-agent.md"]
   }
   ```

3. Create agent markdown file in `agents/`

4. Add to marketplace.json plugins array:
   ```json
   {
     "name": "new-plugin",
     "source": "./new-plugin",
     "description": "...",
     "version": "1.0.0",
     "strict": false
   }
   ```

5. Commit and push:
   ```bash
   git add .
   git commit -m "Add new-plugin"
   git push
   ```

6. Update marketplace:
   ```
   /plugin marketplace update claude-plugins
   ```

## Version Management

**IMPORTANT:** When updating plugin versions, you must update BOTH version fields:

1. **Plugin version** in marketplace.json `plugins[].version`
2. **Marketplace metadata version** in marketplace.json `metadata.version`

Claude Code appears to display the marketplace metadata version in the UI, so both must be kept in sync for version updates to be visible to users.

Example: To release v1.0.1 of a plugin:
```json
{
  "metadata": {
    "version": "1.0.1"  // ← Update this
  },
  "plugins": [
    {
      "name": "meeting-transcriber",
      "version": "1.0.1"  // ← And this
    }
  ]
}
```

## Common Issues

### "Marketplace file not found"
- Ensure `.claude-plugin/marketplace.json` exists at repo root

### "Invalid schema" errors
- `name`: Must be kebab-case (no spaces)
- `owner`: Must be object `{ "name": "..." }`, not string
- `source`: Must start with `./` for relative paths

### Plugin version not updating
- Update both `metadata.version` and `plugins[].version` in marketplace.json
- Commit and push changes to GitHub
- Run `/plugin marketplace update claude-plugins`
- Uninstall and reinstall the plugin if needed

### Plugin not recognized after install
- Ensure `agents` array in plugin.json points to valid .md files
- Restart Claude Code after installation
- Run `/plugin marketplace update claude-plugins`

### Agent not found
- Plugins expose functionality via `agents/`, not `skills/`
- Agent files must be .md format
- Check plugin.json has correct path in `agents` array

## Testing Changes Locally

1. Make changes to plugin files
2. Commit and push to GitHub
3. Run `/plugin marketplace update claude-plugins`
4. Restart Claude Code
5. Test the plugin

## Documentation References

- Plugin Marketplaces: https://docs.anthropic.com/en/docs/claude-code/plugins-marketplaces
- Plugin Development: https://docs.anthropic.com/en/docs/claude-code/plugins
- Plugin Reference: https://docs.anthropic.com/en/docs/claude-code/plugins-reference
