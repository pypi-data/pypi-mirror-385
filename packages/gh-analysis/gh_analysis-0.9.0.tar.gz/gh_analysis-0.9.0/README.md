# GitHub Issue Analysis

Collect GitHub issues and analyze them with AI to improve issue labeling and categorization.

## Quick Start

1. **Setup Environment**
   ```bash
   uv sync --all-extras
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Collect Issues**
   ```bash
   uv run gh-analysis collect --org YOUR_ORG --repo YOUR_REPO --labels bug --limit 5
   ```

3. **Process with AI (Batch Processing - Recommended)**
   ```bash
   # Submit batch job (50% cheaper than individual processing)
   uv run gh-analysis batch submit product-labeling --org YOUR_ORG --repo YOUR_REPO
   
   # Check status
   uv run gh-analysis batch list
   
   # Collect results when completed
   uv run gh-analysis batch collect <job-id>
   ```

   **Individual Processing** (for single issues or custom models):
   ```bash
   # Use default model
   uv run gh-analysis process product-labeling --org YOUR_ORG --repo YOUR_REPO --issue-number 123
   
   # Use custom model with settings
   uv run gh-analysis process product-labeling --org YOUR_ORG --repo YOUR_REPO \
     --model anthropic:claude-3-5-sonnet \
     --setting temperature=0.5 \
     --setting reasoning_effort=high
   
   # Show available model settings
   uv run gh-analysis process show-settings
   ```

4. **Update Labels** (with GitHub write token)
   ```bash
   # Preview changes first
   uv run gh-analysis update-labels --org YOUR_ORG --repo YOUR_REPO --dry-run
   
   # Apply changes
   uv run gh-analysis update-labels --org YOUR_ORG --repo YOUR_REPO
   ```

## Enhanced Analysis with Memory+Tool Agents

This tool provides enhanced troubleshooting agents (with `_mt` suffix) that use **historical case retrieval** and **evidence search** for improved analysis accuracy:

- `claude_sonnet_mt`: Claude Sonnet 4 with memory injection and evidence search tools
- `gpt5_mini_medium_mt`: GPT-5 Mini (medium reasoning) with memory and evidence search  
- `gpt5_mini_high_mt`: GPT-5 Mini (high reasoning) with memory and evidence search
- `gpt5_medium_mt`: GPT-5 (medium reasoning) with memory and evidence search
- `gpt5_high_mt`: GPT-5 (high reasoning) with memory and evidence search
- `gemini_25_pro_mt`: Gemini 2.5 Pro with memory injection and evidence search tools

### Snowflake Requirements

Memory+Tool agents require Snowflake access for historical case data:

```bash
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_PRIVATE_KEY_PATH="~/.snowflake/rsa_key.pem"
export SNOWFLAKE_PRIVATE_KEY_PASSPHRASE="your_passphrase"  # Optional: passphrase for private key
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
```

**Test Connection:**
```bash
uv run python -c "from github_issue_analysis.runners.utils.summary_retrieval import SummaryRetrievalClient; client = SummaryRetrievalClient(); print('✅ Snowflake connection successful')"
```

**Note:** Basic agents (`gpt5_mini_medium`, `gpt5_mini_high`, `gpt5_medium`, `gpt5_high`) work without Snowflake and provide standard troubleshooting analysis.

## Container Usage

For parallel processing and deployment scenarios, the CLI is available as a containerized solution:

```bash
# Build the container locally
podman build -f Containerfile -t gh-analysis .

# Test the build works
podman run --rm \
  -e ISSUE_URL="https://github.com/test/repo/issues/1" \
  -e CLI_ARGS="--help" \
  gh-analysis

# Process a single issue
podman run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e SBCTL_TOKEN=$SBCTL_TOKEN \
  -v $(pwd)/data:/app/data \
  -e ISSUE_URL="https://github.com/your-org/your-repo/issues/123" \
  -e CLI_ARGS="--agent gpt5_mini_medium" \
  gh-analysis
```

**Note:** Use `gh-analysis` for local builds or `ghcr.io/chris-sanders/github-issue-analysis:latest` for tagged releases.

### Environment Variables

**Required:**
- `ISSUE_URL`: Full GitHub issue URL (e.g., `https://github.com/org/repo/issues/123`)
- `GITHUB_TOKEN`: GitHub personal access token
- `SBCTL_TOKEN`: Required for all troubleshooting agents (MCP tool access)

**AI API Keys (at least one required):**
- `OPENAI_API_KEY`: For GPT-5 agents
- `ANTHROPIC_API_KEY`: For Claude agents  
- `GOOGLE_API_KEY`: For Gemini agents

**Optional:**
- `CLI_ARGS`: Additional command-line arguments (e.g., `--agent gpt5_high --interactive`)

**Memory+Tool Agents (optional, for `_mt` agents only):**
- `SNOWFLAKE_ACCOUNT`: Snowflake account identifier
- `SNOWFLAKE_USER`: Snowflake username  
- `SNOWFLAKE_WAREHOUSE`: Snowflake warehouse name
- `SNOWFLAKE_PRIVATE_KEY_PATH`: Path to private key file (local system path, will be mapped into container)

**Volume Mounts:**
- **Data caching**: `-v $(pwd)/data:/app/data` - Persistent storage for collected issues and results across container runs
- **Snowflake SSH keys**: `-v $(dirname $(eval echo $SNOWFLAKE_PRIVATE_KEY_PATH)):/home/appuser/.ssh:ro` - Mount directory containing the private key
- Map the key path: `-e SNOWFLAKE_PRIVATE_KEY_PATH=/home/appuser/.ssh/$(basename $SNOWFLAKE_PRIVATE_KEY_PATH)`

**Note:** Memory+Tool agents (`*_mt`) require Snowflake. If you don't have Snowflake access, use basic agents like `gpt5_mini_medium` instead of `gpt5_mini_medium_mt`.

### Parallel Processing

Run multiple containers simultaneously with different `ISSUE_URL` values to process multiple issues in parallel.

### Advanced Usage

**Interactive Mode:**
```bash
podman run --rm -it \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ISSUE_URL="$ISSUE_URL" \
  -e CLI_ARGS="--agent gpt5_mini_medium --interactive" \
  gh-analysis
```

**Memory+Tool Agent with Snowflake:**
```bash
# Option 1: With Snowflake (requires private key file)
podman run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e SBCTL_TOKEN=$SBCTL_TOKEN \
  -e SNOWFLAKE_ACCOUNT=$SNOWFLAKE_ACCOUNT \
  -e SNOWFLAKE_USER=$SNOWFLAKE_USER \
  -e SNOWFLAKE_WAREHOUSE=$SNOWFLAKE_WAREHOUSE \
  -v $(dirname $(eval echo $SNOWFLAKE_PRIVATE_KEY_PATH)):/home/appuser/.ssh:ro \
  -e SNOWFLAKE_PRIVATE_KEY_PATH=/home/appuser/.ssh/$(basename $SNOWFLAKE_PRIVATE_KEY_PATH) \
  -v $(pwd)/data:/app/data \
  -e ISSUE_URL="$ISSUE_URL" \
  -e CLI_ARGS="--agent gpt5_mini_medium_mt" \
  gh-analysis

# Option 2: Without Snowflake (use basic agents instead)
podman run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e SBCTL_TOKEN=$SBCTL_TOKEN \
  -v $(pwd)/data:/app/data \
  -e ISSUE_URL="$ISSUE_URL" \
  -e CLI_ARGS="--agent gpt5_mini_medium" \
  gh-analysis
```


### Container Testing

Run the included test script to validate container functionality:

```bash
# Run comprehensive container tests
./scripts/test-container-examples.sh

# Test specific functionality
podman run --rm gh-analysis  # Should exit with code 2 (missing ISSUE_URL)
podman run --rm -e ISSUE_URL="test" -e CLI_ARGS="--help" gh-analysis  # Should show help
```

## For AI Agents

**All agent instructions are in `CLAUDE.md`** - this is the single source of truth for development workflow, commands, and requirements.

## Documentation

See `docs/` directory for user documentation:
- `architecture.md` - System design overview
- `data-schemas.md` - JSON formats and data structures  
- `api-reference.md` - CLI commands and usage
