# lammy

`lammy` is a streamlined command line tool for managing Lambda Cloud GPU instances.
Launch, connect, and manage your VMs with zero configuration required.

## Quick Start

1. **Install**

   ```bash
   uv tool install lammy
   ```

2. **Authenticate**

   ```bash
   lammy auth
   ```

   You'll be prompted for:
   - Lambda API key (get from Lambda Cloud dashboard)
   - GitHub token (optional, enables auto git setup on VMs)
   - Git email/name (optional, for commit authorship)
   - Setup scripts (optional, run with `lammy setup`)

   The GitHub token should be a Personal Access Token (classic) with `repo` scope.
   Setup scripts can be URLs (e.g., https://example.com/install.sh) or local file paths.

   Tip: You can also set `LAMBDA_API_KEY` in your environment or `.env` file.

3. **Launch an instance**

   ```bash
   lammy up
   ```

   Interactive prompts will guide you through:
   - Selecting an instance type (from available capacity)
   - Choosing a region
   - Auto-detecting your SSH key (or choosing if you have multiple)
   - Setting an instance name (or using auto-generated)

4. **Connect via SSH**

   ```bash
   lammy ssh
   ```

   Connects to your most recent instance. SSH config is automatically set up.

5. **Terminate when done**

   ```bash
   lammy down
   ```

   Terminates your most recent instance (with confirmation prompt).

## Commands

All commands are fully interactive when information is missing. No flags required!

### Core Commands

```bash
lammy auth               # Authenticate and configure (API key, git, setup scripts)
lammy list               # Show instance types with available capacity
lammy vms                # List your running VMs (use --all for team VMs)
lammy up                 # Launch a new VM (auto-configures git)
lammy down [identifier]  # Terminate a VM
lammy ssh [identifier]   # Connect to a VM via SSH
lammy setup [identifier] # Run setup scripts on a VM (interactive selection)
lammy sync               # Sync SSH configs (clean up terminated VMs)
```

### Command Details

**`lammy auth`**
- Prompts for Lambda API key and GitHub token (optional)
- Optionally configure git email/name for commits
- Optionally configure setup scripts (URLs or local paths)
- Setup scripts can be run with `lammy setup` (interactive selection)
- Stores everything in `~/.config/lammy/config.json`
- Flags: `--api-key`, `--github-token` to skip prompts

**`lammy list`**
- Shows only instance types that currently have capacity
- Displays specs, pricing, and available regions

**`lammy vms`**
- Shows your currently running VMs (filtered by your SSH key)
- Only shows VMs launched with your SSH key (not coworkers' VMs)
- Use `--all` flag to see all team VMs
- Displays instance ID, name, type, IP, status, and region
- Clean output without table borders for easy copy/paste

**`lammy up`**
- Fully interactive instance launch
- Auto-detects SSH key if you only have one
- Auto-generates instance name if not provided
- Waits for IP assignment and sets up SSH config
- Auto-configures git if GitHub token is set
- Options: `--type`, `--region`, `--ssh-key`, `--name`

**`lammy down [identifier]`**
- Terminates an instance
- Without identifier: uses most recent instance
- With multiple instances: shows interactive prompt
- Options: `--force` to skip confirmation

**`lammy ssh [identifier]`**
- Connects to an instance via SSH
- Without identifier: uses most recent instance
- Automatically sets up SSH config on connect
- Pass through extra SSH args: `lammy ssh -L 8080:localhost:8080`

**`lammy setup [identifier]`**
- Run setup scripts on a VM (interactive selection)
- Shows list of configured scripts and lets you pick which to run
- Can select one, multiple (e.g., "1,3"), or "all"
- Without identifier: uses most recent instance
- Configure scripts once with `lammy auth`

**`lammy sync`**
- Syncs SSH config with your currently running VMs
- Removes stale SSH entries for terminated instances
- Only manages VMs launched with your SSH key (ignores coworkers' VMs)
- Updates SSH config for all your running VMs
- Clears cached last instance if it's no longer running

### Smart Features

**Auto SSH Key Detection**
- If you have exactly 1 SSH key registered: auto-selected
- If you have multiple: interactive prompt shown
- Selected key is remembered for future launches and used to filter your VMs

**Last Instance Tracking**
- `lammy` remembers your most recent instance
- `lammy ssh`, `lammy down` use it by default
- No need to specify instance ID repeatedly

**Interactive Fallbacks**
- All commands work without flags
- Missing information? You'll be prompted interactively
- Numbered selection for quick picking

**Auto Git Configuration**
- Configure GitHub token once during `lammy auth`
- New VMs automatically get git configured
- Clone private repos immediately after launch
- Custom git email/name for commits
- `GITHUB_TOKEN` exported to environment (persists in `.bashrc`/`.zshrc`)

**Setup Scripts**
- Configure once during `lammy auth`
- Run with `lammy setup` (interactive selection)
- Support URLs (curl + bash) or local file paths
- Perfect for installing dependencies, tools, dotfiles, etc.
- Example: `https://raw.githubusercontent.com/user/repo/main/install.sh`

## Configuration

Minimal configuration stored in `~/.config/lammy/config.json`:

```json
{
  "api_key": "your-lambda-api-key",
  "github_token": "your-github-token",
  "git_email": "you@example.com",
  "git_name": "Your Name",
  "setup_scripts": [
    "https://raw.githubusercontent.com/user/repo/main/install.sh",
    "~/dotfiles/setup.sh"
  ],
  "last_instance_id": "instance-id",
  "ssh_user": "ubuntu",
  "ssh_identity_file": null
}
```

- `api_key`: Your Lambda Cloud API key
- `github_token`: GitHub Personal Access Token (optional, enables auto git setup)
- `git_email`: Git commit email (optional)
- `git_name`: Git commit name (optional)
- `setup_scripts`: List of scripts to run on new VMs (URLs or local paths)
- `last_instance_id`: Most recently used instance (auto-tracked)
- `ssh_user`: SSH username (default: "ubuntu")
- `ssh_identity_file`: Path to SSH key file (optional, auto-detected)

## SSH Config

`lammy` automatically manages your `~/.ssh/config` file. When you launch or connect to an instance,
an entry is created:

```
# Lammy lammy-gpu-1x-a10-xy start
Host lammy-gpu-1x-a10-xy
  HostName 123.45.67.89
  User ubuntu
  ServerAliveInterval 60
  ServerAliveCountMax 5
  StrictHostKeyChecking accept-new
# Lammy lammy-gpu-1x-a10-xy end
```

You can then connect from your IDE or editor using the host alias.

## Examples

**Quick launch and connect flow:**
```bash
lammy up          # Launch interactively
lammy ssh         # Connect to it
lammy down        # Terminate when done
```

**Non-interactive launch:**
```bash
lammy up --type gpu_1x_a10 --region us-west-1 --name my-training-job
```

**SSH with port forwarding:**
```bash
lammy ssh -L 8888:localhost:8888
```

**Manage specific instance:**
```bash
lammy vms                 # List all running VMs
lammy ssh instance-xyz    # Connect to specific one
lammy down instance-xyz   # Terminate it
```

**Work with private repos:**
```bash
lammy auth                # Configure GitHub token once
lammy up                  # Launch VM (git auto-configured!)
lammy ssh                 # Connect and start cloning
```

**Configure and run custom setup scripts:**
```bash
lammy auth                # During auth, add setup scripts like:
                         # https://raw.githubusercontent.com/camfer-dev/BlobLearn/main/scripts/install.sh
lammy setup               # Run scripts on your VM (pick which ones to run)
```

**Clean up after terminated VMs:**
```bash
lammy sync                # Remove SSH entries for terminated VMs
```

## Publishing

```bash
uv build
source .env && uv publish --token $PYPI_TOKEN 
```
