Based on the documentation in your project, here is the information on environment variables and model choices for running OntoGPT with CBORG.

### Environment Variables for CBORG

To use CBORG, OntoGPT leverages its OpenAI-compatible API. This means you need to set the standard `OPENAI_API_KEY` environment variable to your CBORG API key.

You can set it for your session like this:
```bash
export OPENAI_API_KEY="your-cborg-api-key-here"
```
Then, when you run the extraction, you must also specify the CBORG API endpoint. The full command pattern is:
```bash
uv run ontogpt extract \
  -t templates/growth_conditions.yaml \
  -i abstracts/ \
  -m <model_name> \
  --model-provider openai \
  --api-base "https://api.cborg.lbl.gov"
```

### Model Choices and Recommendation

The documentation mentions several models that can be used via the CBORG endpoint. Here are your choices and my recommendation:

**Model Choices:**

*   **`lbl/cborg-mini`**: This is described as a "GPT-OSS 20B" model that is on a **free tier**.
*   **`openai/gpt-5`**: Mentioned as a model to try for comparison.
*   **`anthropic/claude-opus`**: Can also be used via the CBORG endpoint.

**Recommendation:**

I strongly recommend you start with the **`lbl/cborg-mini`** model.

The `CBORG_TESTING_RESULTS.md` file explicitly states that this model is on a **free tier**, which directly addresses your question about using the "free" credits. More importantly, the testing results in that document show that this model provides **"high-quality extraction"** and **"perfect ontology grounding"** for your specific tasks.

Given that it is both cost-free and has been shown to perform well on your data, `lbl/cborg-mini` is the ideal choice to start with for the extraction run.