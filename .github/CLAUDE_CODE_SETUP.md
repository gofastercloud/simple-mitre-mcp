# Claude Code GitHub Action Setup Guide

## 🚀 Quick Setup Instructions

### 1. Add Your Anthropic API Key to GitHub Secrets

You need to add your Anthropic API key as a repository secret:

1. Go to your repository: https://github.com/gofastercloud/simple-mitre-mcp
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `ANTHROPIC_API_KEY`
6. Value: Your Anthropic API key (starts with `sk-ant-api03-...`)
7. Click **Add secret**

### 2. Get Your Anthropic API Key

If you don't have an API key yet:

1. Go to https://console.anthropic.com/
2. Sign in to your account
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy the key (it starts with `sk-ant-api03-...`)

### 3. Test the Setup

Once you've added the secret:

1. Create a test branch and make a small change
2. Open a Pull Request
3. The Claude Code Review action should automatically run
4. You'll see Claude's review comments on your PR

## 🔧 Workflow Configuration

The workflow is configured in `.github/workflows/claude-code-review.yml` with these features:

### Triggers
- **Pull Request Events**: opened, synchronize, reopened
- **Review Comments**: responds to review comment discussions

### File Types Reviewed
- Python files (`.py`)
- JavaScript files (`.js`) 
- HTML templates (`.html`)
- CSS stylesheets (`.css`)
- YAML/YML config files
- Markdown documentation (`.md`)

### Excluded Files
- Python cache files (`__pycache__`, `.pyc`)
- Test cache directories (`.pytest_cache`)
- Virtual environments (`.venv`)
- Lock files (`uv.lock`)
- Log files (`.log`)

### Custom Review Focus
The action is configured to focus on:
- Code quality and maintainability
- Security vulnerabilities
- Performance implications  
- Testing coverage
- Documentation completeness
- MCP protocol compliance
- Compatibility with existing codebase

## 🛠️ Troubleshooting

### Common Issues

1. **Action fails with "Invalid API key"**
   - Verify the `ANTHROPIC_API_KEY` secret is set correctly
   - Make sure the key starts with `sk-ant-api03-`

2. **No review comments appear**
   - Check the Actions tab for any workflow failures
   - Ensure the PR contains changes to reviewable file types
   - Verify repository permissions allow PR comments

3. **Rate limiting issues**
   - The action respects Anthropic API rate limits
   - Large PRs may be reviewed in chunks

### Manual Trigger

You can manually trigger the workflow by:
1. Going to Actions tab
2. Selecting "Claude Code Review" workflow
3. Clicking "Run workflow"

## 📝 Customization

You can customize the review behavior by editing `.github/workflows/claude-code-review.yml`:

- **system-prompt**: Modify the review focus and instructions
- **include-patterns**: Change which file types to review
- **exclude-patterns**: Add more files/directories to skip
- **model**: Switch to different Claude models if available
- **max-tokens**: Adjust response length limits

## 🔒 Security

- API keys are stored securely as GitHub secrets
- The action only has read access to repository contents
- Review comments are posted with write access to PRs only

## 📚 Additional Resources

- [Claude Code Action Documentation](https://github.com/anthropics/claude-code-action)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Anthropic API Documentation](https://docs.anthropic.com/)