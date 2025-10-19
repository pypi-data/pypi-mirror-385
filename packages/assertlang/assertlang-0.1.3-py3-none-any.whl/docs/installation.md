# AssertLang Installation Guide

Complete guide to installing and configuring AssertLang.

## Quick Install

```bash
# Clone repository
git clone https://github.com/assertlang/assertlang.git
cd assertlang

# Install
pip install -e .
```

## Global CLI Access

### Option 1: Add bin/ to PATH (Recommended)

Add AssertLang's bin directory to your PATH for single-word `assertlang` command:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/path/to/assertlang/bin:$PATH"

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

Now you can use `assertlang` from anywhere:

```bash
assertlang --version
assertlang list-tools
assertlang generate agent.al --lang python
```

### Option 2: Symlink to /usr/local/bin

```bash
sudo ln -s $(pwd)/bin/assertlang /usr/local/bin/assertlang

# Test
assertlang --version
```

### Option 3: Use Python Module

If you prefer not to modify PATH:

```bash
python3 -m assertlang.cli --version
python3 -m assertlang.cli generate agent.al --lang python
```

## System Requirements

### Core Requirements

- **Python**: 3.8 or higher
- **pip**: 20.0 or higher

### Language-Specific Requirements

Install runtimes for the languages you want to use:

**Python:**
```bash
# Already installed if you can run assertlang
python3 --version
```

**Node.js:**
```bash
# macOS (Homebrew)
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm

# Verify
node --version  # v18+ recommended
```

**Go:**
```bash
# macOS (Homebrew)
brew install go

# Ubuntu/Debian
sudo apt install golang

# Verify
go version  # 1.20+ recommended
```

**C#/.NET:**
```bash
# macOS (Homebrew)
brew install dotnet

# Ubuntu/Debian
sudo apt install dotnet-sdk-8.0

# Verify
dotnet --version  # 8.0+ recommended
```

**Rust:**
```bash
# All platforms
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify
cargo --version  # 1.70+ recommended
```

## Dependencies

### Core Dependencies (Auto-Installed)

```
fastapi>=0.104.0
uvicorn>=0.24.0
```

### Production Features (Optional)

```bash
pip install assertlang[production]
```

Includes:
- `slowapi` - Rate limiting
- `python-multipart` - Form data handling

### AI Features (Optional)

```bash
pip install assertlang[ai]
```

Includes:
- `langchain` - LLM framework
- `langchain-anthropic` - Anthropic integration

Configure:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Observability Features (Optional)

```bash
pip install assertlang[observability]
```

Includes:
- `opentelemetry-api` - Tracing/metrics API
- `opentelemetry-sdk` - SDK implementation
- `opentelemetry-instrumentation-fastapi` - FastAPI auto-instrumentation

### Development Tools (Optional)

```bash
pip install assertlang[dev]
```

Includes:
- `pytest` - Testing framework
- `black` - Code formatter
- `mypy` - Type checker

## Verification

Verify your installation:

```bash
# Check CLI
assertlang --version

# List available tools
assertlang list-tools

# Create test agent
assertlang init test --template basic

# Validate
assertlang validate test.al

# Generate server
assertlang generate test.al --lang python

# Clean up
rm test.al
rm -rf generated/
```

## Configuration

### Environment Variables

Create `.env` file in your project:

```bash
# AI Configuration
ANTHROPIC_API_KEY=your-key-here

# Security
ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
ALLOWED_HOSTS=example.com,www.example.com
DEBUG=false
RATE_LIMIT=100

# Server
DEFAULT_PORT=3000
LOG_LEVEL=INFO
```

### Shell Completion (Optional)

#### Bash

```bash
# Add to ~/.bashrc
eval "$(_ASSERTLANG_COMPLETE=bash_source assertlang)"
```

#### Zsh

```bash
# Add to ~/.zshrc
eval "$(_ASSERTLANG_COMPLETE=zsh_source assertlang)"
```

#### Fish

```bash
# Add to ~/.config/fish/completions/assertlang.fish
_ASSERTLANG_COMPLETE=fish_source assertlang | source
```

## Troubleshooting

### Command Not Found

If `assertlang` command is not found:

1. Check PATH includes bin directory:
   ```bash
   echo $PATH | grep assertlang
   ```

2. Use absolute path:
   ```bash
   ~/path/to/assertlang/bin/assertlang --version
   ```

3. Use Python module:
   ```bash
   python3 -m assertlang.cli --version
   ```

### Import Errors

If you get module import errors:

```bash
# Reinstall in development mode
cd /path/to/assertlang
pip install -e . --force-reinstall

# Or add to PYTHONPATH
export PYTHONPATH="/path/to/assertlang:$PYTHONPATH"
```

### Permission Denied

If you get permission errors:

```bash
# Make bin/assertlang executable
chmod +x bin/assertlang

# Or install to user directory
pip install --user -e .
```

### Language Runtime Issues

If generated servers fail to build/run:

**Node.js:**
```bash
# Ensure npm is in PATH
which npm
npm --version

# Clear cache if needed
npm cache clean --force
```

**Go:**
```bash
# Ensure GOPATH is set
echo $GOPATH
go env

# Clear module cache if needed
go clean -modcache
```

**.NET:**
```bash
# Ensure dotnet is in PATH
which dotnet
dotnet --info

# Clear NuGet cache if needed
dotnet nuget locals all --clear
```

**Rust:**
```bash
# Ensure cargo is in PATH
which cargo
rustup show

# Update Rust if needed
rustup update
```

## Uninstall

To completely remove AssertLang:

```bash
# Uninstall pip package
pip uninstall assertlang

# Remove source (if cloned)
rm -rf /path/to/assertlang

# Remove from PATH (edit ~/.bashrc or ~/.zshrc)
# Remove: export PATH="$HOME/path/to/assertlang/bin:$PATH"

# Remove symlink (if created)
sudo rm /usr/local/bin/assertlang
```

## Upgrade

To upgrade to the latest version:

```bash
cd /path/to/assertlang

# Pull latest changes
git pull origin main

# Reinstall
pip install -e . --upgrade
```

## Next Steps

- [CLI Guide](./cli-guide.md) - Complete CLI reference
- [Quick Start Tutorial](./quickstart.md) - Build your first agent
- [Production Deployment](./production-hardening.md) - Production setup

## Support

- **Documentation**: [docs/](./README.md)
- **Issues**: https://github.com/assertlang/assertlang/issues
- **Discussions**: https://github.com/assertlang/assertlang/discussions
