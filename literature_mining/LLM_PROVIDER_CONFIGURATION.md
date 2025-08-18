# OntoGPT LLM Provider Configuration Guide

This guide shows how to configure OntoGPT to use different LLM providers and models.

## Overview

OntoGPT uses **LiteLLM** as the underlying framework, which supports many providers and OpenAI-compatible endpoints.

## Supported Providers

From the code and documentation:
- **OpenAI** (default)
- **Anthropic** (`anthropic-key`)
- **Mistral** (`mistral-key`)
- **Groq** (`groq-key`)
- **HuggingFace** (`huggingface-key`)
- **Azure OpenAI** (`azure-key`, `azure-base`, `azure-version`)
- **Ollama** (local models - `ollama/modelname`)

## Setting Up API Keys

### Basic Provider Setup

```bash
# For Anthropic
runoak set-apikey -e anthropic-key <your-key>

# For Mistral
runoak set-apikey -e mistral-key <your-key>

# For Groq
runoak set-apikey -e groq-key <your-key>

# For HuggingFace
runoak set-apikey -e huggingface-key <your-key>
```

### Azure OpenAI Setup

```bash
runoak set-apikey -e azure-key <your-azure-api-key>
runoak set-apikey -e azure-base <your-azure-base-url>
runoak set-apikey -e azure-version <your-azure-api-version>
```

Example Azure URLs:
- Base: `https://example-endpoint.openai.azure.com`
- Version: `2023-05-15`

### Custom OpenAI-Compatible Endpoints

```bash
runoak set-apikey -e <provider>-key <your-key>
runoak set-apikey -e <provider>-base <endpoint-url>
```

## Using Different Models

### 1. Local Models (Ollama)

**Setup:**
```bash
# Install ollama (see https://github.com/ollama/ollama)
# Start ollama service
ollama serve  # or sudo systemctl start ollama

# Download a model
ollama pull llama3

# List downloaded models
ollama list
```

**Usage:**
```bash
ontogpt extract -t drug -i ~/path/to/abstract.txt -m ollama/llama3
```

### 2. Direct Provider Support

```bash
# Anthropic Claude
ontogpt extract -t template -i input.txt -m anthropic/claude-3-sonnet-20240229

# Mistral
ontogpt extract -t template -i input.txt -m mistral/mistral-large

# Groq
ontogpt extract -t template -i input.txt -m groq/llama3-70b-8192
```

### 3. OpenAI-Compatible Endpoints

For custom endpoints that implement OpenAI's API:

```bash
ontogpt extract -t your_template \
  -i input.txt \
  -m model_name \
  --model-provider openai \
  --api-base "https://your-endpoint.com"
```

## CBORG (LBL) Configuration

To use **CBORG** at Lawrence Berkeley National Laboratory:

```bash
ontogpt extract -t your_template \
  -i input.txt \
  -m anthropic/claude-opus \
  --model-provider openai \
  --api-base "https://api.cborg.lbl.gov"
```

**Note:** Replace `anthropic/claude-opus` with whatever model names CBORG supports.

## Example Commands for Literature Mining

### Using Anthropic Claude

```bash
# Extract with Anthropic Claude
ontogpt extract -t growth_conditions \
  -i abstracts/sample.txt \
  -m anthropic/claude-3-sonnet-20240229 \
  -o outputs/growth_conditions_claude.yaml
```

### Using Local Llama3

```bash
# Extract with local Llama3
ontogpt extract -t growth_conditions \
  -i abstracts/sample.txt \
  -m ollama/llama3 \
  -o outputs/growth_conditions_llama3.yaml
```

### Using CBORG Endpoint

```bash
# Extract using CBORG
ontogpt extract -t growth_conditions \
  -i abstracts/sample.txt \
  -m <cborg_model_name> \
  --model-provider openai \
  --api-base "https://api.cborg.lbl.gov" \
  -o outputs/growth_conditions_cborg.yaml
```

## Performance Notes

From the OntoGPT documentation:
- Models can vary significantly in performance
- Larger models will not always perform more accurately or efficiently
- Local models may be slower but provide privacy and cost benefits
- Different models may excel at different types of extraction tasks

## Troubleshooting

### Common Issues

1. **Authentication errors**: Check API keys with `runoak set-apikey`
2. **Model not found**: Verify model name and provider compatibility
3. **Rate limiting**: Consider switching to local models or different providers
4. **Performance issues**: Try different model sizes or providers

### Debug Information

Enable debug output:
```bash
ontogpt extract --verbose -t template -i input.txt -m model_name
```

### Testing Model Availability

Test a simple extraction to verify model setup:
```bash
echo "The bacteria grows at 37°C in aerobic conditions." | ontogpt extract -t growth_conditions -m your_model_name
```

## Integration with Makefile

To use different models in your literature mining pipeline, modify your Makefile targets to include model parameters:

```makefile
# Example: Use Anthropic Claude for extractions
extract-claude:
	ontogpt extract -t $(TEMPLATE) \
		-i $(INPUT_DIR) \
		-m anthropic/claude-3-sonnet-20240229 \
		-o outputs/$(TEMPLATE)_claude_$(shell date +%Y%m%d_%H%M%S).yaml

# Example: Use local model
extract-local:
	ontogpt extract -t $(TEMPLATE) \
		-i $(INPUT_DIR) \
		-m ollama/llama3 \
		-o outputs/$(TEMPLATE)_local_$(shell date +%Y%m%d_%H%M%S).yaml
```

## API Key Security and Management

### Secure Storage Options

**For CBORG and other API keys, use these secure methods:**

#### 1. OntoGPT Built-in Key Manager (Recommended)

```bash
# Store CBORG key securely (encrypted)
runoak set-apikey -e cborg-key <your-cborg-api-key>

# Store other provider keys
runoak set-apikey -e anthropic-key <your-anthropic-key>
runoak set-apikey -e openai-key <your-openai-key>
```

Keys stored this way are encrypted and managed by the Ontology Access Kit.

#### 2. Environment Variables

```bash
# In your shell profile (.bashrc, .zshrc, etc.)
export CBORG_API_KEY="your-cborg-key-here"
export ANTHROPIC_API_KEY="your-anthropic-key-here"

# Or temporarily for one session
export CBORG_API_KEY="your-key" && ontogpt extract ...
```

#### 3. Team Sharing Best Practices

**✅ DO use:**
- **Shared password manager** (1Password, Bitwarden, LastPass)
- **Secure team wiki** with access controls
- **Environment-specific config files** (not tracked in git)
- **CI/CD secret management** (for automation)
- **Direct key distribution** from service providers

**❌ DO NOT use:**
- Git repositories (public or private)
- Makefiles or configuration files in version control
- Public documentation or wikis
- Email, Slack, or other messaging platforms
- Hardcoded values in scripts

### Security Checklist

- [ ] Store API keys using `runoak set-apikey` or environment variables
- [ ] Add `*.key`, `*.env`, and similar files to `.gitignore`
- [ ] Use team password manager for key sharing
- [ ] Regularly rotate API keys
- [ ] Monitor usage and costs for each key
- [ ] Limit key permissions when possible

### Testing Key Setup

After setting up your keys, test the connection:

```bash
# Test CBORG connection
echo "The bacteria grows at 37°C." | ontogpt extract -t growth_conditions \
  --model-provider openai \
  --api-base "https://api.cborg.lbl.gov" \
  -m <model_name>

# Test other providers
echo "The bacteria grows at 37°C." | ontogpt extract -t growth_conditions \
  -m anthropic/claude-3-sonnet-20240229
```