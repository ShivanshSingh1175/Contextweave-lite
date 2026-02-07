# LLM Provider Configuration Guide

ContextWeave Lite supports any OpenAI-compatible LLM API. Here's how to configure different providers.

## OpenAI (Default)

```bash
export LLM_API_KEY="sk-your-openai-api-key"
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_MODEL="gpt-3.5-turbo"  # or gpt-4, gpt-4-turbo
```

**Cost**: ~$0.001-0.03 per request depending on model and file size

**Pros**: High quality, reliable, fast
**Cons**: Requires internet, costs money

## Azure OpenAI

```bash
export LLM_API_KEY="your-azure-api-key"
export LLM_API_BASE="https://your-resource.openai.azure.com/openai/deployments/your-deployment-name"
export LLM_MODEL="gpt-35-turbo"  # or gpt-4
```

**Note**: Azure uses different model names (e.g., `gpt-35-turbo` instead of `gpt-3.5-turbo`)

## AWS Bedrock (Claude)

For AWS Bedrock, you'll need to modify `llm_client.py` to use boto3 instead of HTTP requests.

Example modification:

```python
import boto3
import json

def call_llm_bedrock(prompt: str) -> dict:
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    content = response_body['content'][0]['text']
    
    return json.loads(content)
```

## Local Models (LM Studio, Ollama)

### LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download a model (e.g., Mistral, Llama 2)
3. Start local server (it provides OpenAI-compatible API)
4. Configure:

```bash
export LLM_API_KEY="not-needed"
export LLM_API_BASE="http://localhost:1234/v1"
export LLM_MODEL="local-model"
```

### Ollama with OpenAI Compatibility

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull mistral`
3. Use a compatibility layer like [ollama-openai-proxy](https://github.com/ollama/ollama/blob/main/docs/openai.md)
4. Configure:

```bash
export LLM_API_KEY="not-needed"
export LLM_API_BASE="http://localhost:11434/v1"
export LLM_MODEL="mistral"
```

**Pros**: Free, private, works offline
**Cons**: Slower, lower quality than GPT-4, requires powerful hardware

## Anthropic Claude (Direct API)

To use Claude's direct API (not through Bedrock), you'll need to modify `llm_client.py`:

```python
import anthropic

def call_llm_claude(prompt: str) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("LLM_API_KEY"))
    
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    content = message.content[0].text
    return json.loads(content)
```

Then set:
```bash
export LLM_API_KEY="sk-ant-your-anthropic-key"
```

## Google Gemini

For Gemini, you'll need to modify `llm_client.py` to use Google's API:

```python
import google.generativeai as genai

def call_llm_gemini(prompt: str) -> dict:
    genai.configure(api_key=os.getenv("LLM_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    
    response = model.generate_content(prompt)
    return json.loads(response.text)
```

Then set:
```bash
export LLM_API_KEY="your-google-api-key"
```

## Hugging Face Inference API

```bash
export LLM_API_KEY="hf_your-huggingface-token"
export LLM_API_BASE="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
export LLM_MODEL="mistralai/Mistral-7B-Instruct-v0.2"
```

**Note**: Hugging Face API format may differ from OpenAI. You might need to adjust `call_llm()` function.

## Testing Different Providers

After configuring a provider, test it:

```bash
# Start backend
python main.py

# Test health endpoint
curl http://localhost:8000/health

# Test with a real file
curl -X POST http://localhost:8000/context/file \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "file_path": "/path/to/repo/file.py"
  }'
```

## Choosing a Provider

### For Development/Testing
- **Local models** (LM Studio, Ollama) - Free, private
- **Mock mode** (no API key) - Free, instant

### For Production
- **OpenAI GPT-3.5-turbo** - Good balance of cost and quality
- **OpenAI GPT-4** - Best quality, higher cost
- **Azure OpenAI** - Enterprise features, data residency
- **AWS Bedrock** - AWS integration, data residency

### For India-Specific Deployment
- **AWS Bedrock (Mumbai region)** - Data stays in India
- **Azure OpenAI (India regions)** - Data residency compliance
- **Local models** - Complete data privacy

## Cost Comparison (Approximate)

| Provider | Model | Cost per 1K tokens | Cost per analysis |
|----------|-------|-------------------|-------------------|
| OpenAI | GPT-3.5-turbo | $0.001 | $0.002-0.01 |
| OpenAI | GPT-4 | $0.03 | $0.06-0.30 |
| Azure | GPT-3.5 | Similar to OpenAI | Similar |
| AWS Bedrock | Claude 3 | $0.003-0.015 | $0.01-0.05 |
| Local | Any | $0 (electricity) | $0 |

**Note**: Costs vary based on file size and commit history length.

## Troubleshooting

### "Invalid API key"
- Check key is correct and not expired
- Verify key has proper permissions

### "Model not found"
- Check model name is correct for your provider
- Some providers use different naming conventions

### "Rate limit exceeded"
- Wait a few minutes
- Upgrade to paid tier
- Use caching to reduce requests

### "Timeout"
- Increase timeout in `llm_client.py`
- Use faster model
- Reduce `commit_limit` in request

## Custom Provider Integration

To add a completely custom provider:

1. Edit `backend/llm_client.py`
2. Add a new function `call_llm_custom()`
3. Modify `call_llm()` to detect and use your provider
4. Update environment variable handling

Example:

```python
async def call_llm(prompt: str) -> dict:
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "openai":
        return await call_llm_openai(prompt)
    elif provider == "custom":
        return await call_llm_custom(prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

## Need Help?

- Check provider documentation for API details
- Review `backend/llm_client.py` for implementation
- Test with `curl` or Python script first
- Check backend logs for detailed errors
