# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.


from llama_stack.providers.datatypes import (
    Api,
    InlineProviderSpec,
    ProviderSpec,
    RemoteProviderSpec,
)

META_REFERENCE_DEPS = [
    "accelerate",
    "fairscale",
    "torch",
    "torchvision",
    "transformers",
    "zmq",
    "lm-format-enforcer",
    "sentence-transformers",
    "torchao==0.8.0",
    "fbgemm-gpu-genai==1.1.2",
]


def available_providers() -> list[ProviderSpec]:
    return [
        InlineProviderSpec(
            api=Api.inference,
            provider_type="inline::meta-reference",
            pip_packages=META_REFERENCE_DEPS,
            module="llama_stack.providers.inline.inference.meta_reference",
            config_class="llama_stack.providers.inline.inference.meta_reference.MetaReferenceInferenceConfig",
            description="Meta's reference implementation of inference with support for various model formats and optimization techniques.",
        ),
        InlineProviderSpec(
            api=Api.inference,
            provider_type="inline::sentence-transformers",
            # CrossEncoder depends on torchao.quantization
            pip_packages=[
                "torch torchvision torchao>=0.12.0 --extra-index-url https://download.pytorch.org/whl/cpu",
                "sentence-transformers --no-deps",
                # required by some SentenceTransformers architectures for tensor rearrange/merge ops
                "einops",
                # fast HF tokenization backend used by SentenceTransformers models
                "tokenizers",
                # safe and fast file format for storing and loading tensors
                "safetensors",
            ],
            module="llama_stack.providers.inline.inference.sentence_transformers",
            config_class="llama_stack.providers.inline.inference.sentence_transformers.config.SentenceTransformersInferenceConfig",
            description="Sentence Transformers inference provider for text embeddings and similarity search.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="cerebras",
            provider_type="remote::cerebras",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.cerebras",
            config_class="llama_stack.providers.remote.inference.cerebras.CerebrasImplConfig",
            description="Cerebras inference provider for running models on Cerebras Cloud platform.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="ollama",
            provider_type="remote::ollama",
            pip_packages=["ollama", "aiohttp", "h11>=0.16.0"],
            config_class="llama_stack.providers.remote.inference.ollama.OllamaImplConfig",
            module="llama_stack.providers.remote.inference.ollama",
            description="Ollama inference provider for running local models through the Ollama runtime.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="vllm",
            provider_type="remote::vllm",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.vllm",
            config_class="llama_stack.providers.remote.inference.vllm.VLLMInferenceAdapterConfig",
            provider_data_validator="llama_stack.providers.remote.inference.vllm.VLLMProviderDataValidator",
            description="Remote vLLM inference provider for connecting to vLLM servers.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="tgi",
            provider_type="remote::tgi",
            pip_packages=["huggingface_hub", "aiohttp"],
            module="llama_stack.providers.remote.inference.tgi",
            config_class="llama_stack.providers.remote.inference.tgi.TGIImplConfig",
            description="Text Generation Inference (TGI) provider for HuggingFace model serving.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="hf::serverless",
            provider_type="remote::hf::serverless",
            pip_packages=["huggingface_hub", "aiohttp"],
            module="llama_stack.providers.remote.inference.tgi",
            config_class="llama_stack.providers.remote.inference.tgi.InferenceAPIImplConfig",
            description="HuggingFace Inference API serverless provider for on-demand model inference.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            provider_type="remote::hf::endpoint",
            adapter_type="hf::endpoint",
            pip_packages=["huggingface_hub", "aiohttp"],
            module="llama_stack.providers.remote.inference.tgi",
            config_class="llama_stack.providers.remote.inference.tgi.InferenceEndpointImplConfig",
            description="HuggingFace Inference Endpoints provider for dedicated model serving.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="fireworks",
            provider_type="remote::fireworks",
            pip_packages=[
                "fireworks-ai<=0.17.16",
            ],
            module="llama_stack.providers.remote.inference.fireworks",
            config_class="llama_stack.providers.remote.inference.fireworks.FireworksImplConfig",
            provider_data_validator="llama_stack.providers.remote.inference.fireworks.FireworksProviderDataValidator",
            description="Fireworks AI inference provider for Llama models and other AI models on the Fireworks platform.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="together",
            provider_type="remote::together",
            pip_packages=[
                "together",
            ],
            module="llama_stack.providers.remote.inference.together",
            config_class="llama_stack.providers.remote.inference.together.TogetherImplConfig",
            provider_data_validator="llama_stack.providers.remote.inference.together.TogetherProviderDataValidator",
            description="Together AI inference provider for open-source models and collaborative AI development.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="bedrock",
            provider_type="remote::bedrock",
            pip_packages=["boto3"],
            module="llama_stack.providers.remote.inference.bedrock",
            config_class="llama_stack.providers.remote.inference.bedrock.BedrockConfig",
            description="AWS Bedrock inference provider for accessing various AI models through AWS's managed service.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="databricks",
            provider_type="remote::databricks",
            pip_packages=["databricks-sdk"],
            module="llama_stack.providers.remote.inference.databricks",
            config_class="llama_stack.providers.remote.inference.databricks.DatabricksImplConfig",
            description="Databricks inference provider for running models on Databricks' unified analytics platform.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="nvidia",
            provider_type="remote::nvidia",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.nvidia",
            config_class="llama_stack.providers.remote.inference.nvidia.NVIDIAConfig",
            description="NVIDIA inference provider for accessing NVIDIA NIM models and AI services.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="runpod",
            provider_type="remote::runpod",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.runpod",
            config_class="llama_stack.providers.remote.inference.runpod.RunpodImplConfig",
            description="RunPod inference provider for running models on RunPod's cloud GPU platform.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="openai",
            provider_type="remote::openai",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.openai",
            config_class="llama_stack.providers.remote.inference.openai.OpenAIConfig",
            provider_data_validator="llama_stack.providers.remote.inference.openai.config.OpenAIProviderDataValidator",
            description="OpenAI inference provider for accessing GPT models and other OpenAI services.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="anthropic",
            provider_type="remote::anthropic",
            pip_packages=["anthropic"],
            module="llama_stack.providers.remote.inference.anthropic",
            config_class="llama_stack.providers.remote.inference.anthropic.AnthropicConfig",
            provider_data_validator="llama_stack.providers.remote.inference.anthropic.config.AnthropicProviderDataValidator",
            description="Anthropic inference provider for accessing Claude models and Anthropic's AI services.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="gemini",
            provider_type="remote::gemini",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.gemini",
            config_class="llama_stack.providers.remote.inference.gemini.GeminiConfig",
            provider_data_validator="llama_stack.providers.remote.inference.gemini.config.GeminiProviderDataValidator",
            description="Google Gemini inference provider for accessing Gemini models and Google's AI services.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="vertexai",
            provider_type="remote::vertexai",
            pip_packages=[
                "google-cloud-aiplatform",
            ],
            module="llama_stack.providers.remote.inference.vertexai",
            config_class="llama_stack.providers.remote.inference.vertexai.VertexAIConfig",
            provider_data_validator="llama_stack.providers.remote.inference.vertexai.config.VertexAIProviderDataValidator",
            description="""Google Vertex AI inference provider enables you to use Google's Gemini models through Google Cloud's Vertex AI platform, providing several advantages:

• Enterprise-grade security: Uses Google Cloud's security controls and IAM
• Better integration: Seamless integration with other Google Cloud services
• Advanced features: Access to additional Vertex AI features like model tuning and monitoring
• Authentication: Uses Google Cloud Application Default Credentials (ADC) instead of API keys

Configuration:
- Set VERTEX_AI_PROJECT environment variable (required)
- Set VERTEX_AI_LOCATION environment variable (optional, defaults to us-central1)
- Use Google Cloud Application Default Credentials or service account key

Authentication Setup:
Option 1 (Recommended): gcloud auth application-default login
Option 2: Set GOOGLE_APPLICATION_CREDENTIALS to service account key path

Available Models:
- vertex_ai/gemini-2.0-flash
- vertex_ai/gemini-2.5-flash
- vertex_ai/gemini-2.5-pro""",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="groq",
            provider_type="remote::groq",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.groq",
            config_class="llama_stack.providers.remote.inference.groq.GroqConfig",
            provider_data_validator="llama_stack.providers.remote.inference.groq.config.GroqProviderDataValidator",
            description="Groq inference provider for ultra-fast inference using Groq's LPU technology.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="llama-openai-compat",
            provider_type="remote::llama-openai-compat",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.llama_openai_compat",
            config_class="llama_stack.providers.remote.inference.llama_openai_compat.config.LlamaCompatConfig",
            provider_data_validator="llama_stack.providers.remote.inference.llama_openai_compat.config.LlamaProviderDataValidator",
            description="Llama OpenAI-compatible provider for using Llama models with OpenAI API format.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="sambanova",
            provider_type="remote::sambanova",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.sambanova",
            config_class="llama_stack.providers.remote.inference.sambanova.SambaNovaImplConfig",
            provider_data_validator="llama_stack.providers.remote.inference.sambanova.config.SambaNovaProviderDataValidator",
            description="SambaNova inference provider for running models on SambaNova's dataflow architecture.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="passthrough",
            provider_type="remote::passthrough",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.passthrough",
            config_class="llama_stack.providers.remote.inference.passthrough.PassthroughImplConfig",
            provider_data_validator="llama_stack.providers.remote.inference.passthrough.PassthroughProviderDataValidator",
            description="Passthrough inference provider for connecting to any external inference service not directly supported.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            adapter_type="watsonx",
            provider_type="remote::watsonx",
            pip_packages=["litellm"],
            module="llama_stack.providers.remote.inference.watsonx",
            config_class="llama_stack.providers.remote.inference.watsonx.WatsonXConfig",
            provider_data_validator="llama_stack.providers.remote.inference.watsonx.config.WatsonXProviderDataValidator",
            description="IBM WatsonX inference provider for accessing AI models on IBM's WatsonX platform.",
        ),
        RemoteProviderSpec(
            api=Api.inference,
            provider_type="remote::azure",
            adapter_type="azure",
            pip_packages=[],
            module="llama_stack.providers.remote.inference.azure",
            config_class="llama_stack.providers.remote.inference.azure.AzureConfig",
            provider_data_validator="llama_stack.providers.remote.inference.azure.config.AzureProviderDataValidator",
            description="""
Azure OpenAI inference provider for accessing GPT models and other Azure services.
Provider documentation
https://learn.microsoft.com/en-us/azure/ai-foundry/openai/overview
""",
        ),
    ]
