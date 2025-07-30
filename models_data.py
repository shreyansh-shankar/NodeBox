models = [
    {
        "name": "deepseek-r1",
        "icon": "assets/models_logo/deepseek.png",
        "description": "DeepSeek-R1 is a family of open reasoning models with performance approaching that of leading models, such as O3 and Gemini 2.5 Pro.",
        "tags": ["deepseek", "thinking" "tools"],
        "sizes": ["1.5b", "7b", "8b", "14b", "32b", "70b", "671b"]
    },
    {
        "name": "gemma3n",
        "icon": "assets/models_logo/gemma.png",
        "description": "Gemma 3n models are designed for efficient execution on everyday devices such as laptops, tablets or phones. ",
        "tags": ["gemma"],
        "sizes": ["e2b", "e4b"]
    },
    {
        "name": "gemma3",
        "icon": "assets/models_logo/gemma.png",
        "description": "The current, most capable model that runs on a single GPU.",
        "tags": ["gemma", "vision"],
        "sizes": ["1b", "4b", "12b", "27b"]
    },
    {
        "name": "qwen3",
        "icon": "assets/models_logo/qwen.png",
        "description": "Qwen3 is the latest generation of large language models in Qwen series, offering a comprehensive suite of dense and mixture-of-experts (MoE) models.",
        "tags": ["qwen", "tools", "thinking"],
        "sizes": ["0.6b", "1.7b", "4b", "8b", "14b", "30b", "32b", "235b"]
    },
    {
        "name": "qwen2.5vl",
        "icon": "assets/models_logo/qwen.png",
        "description": "Flagship vision-language model of Qwen and also a significant leap from the previous Qwen2-VL.",
        "tags": ["qwen", "vision"],
        "sizes": ["3b", "7b", "32b", "72b"]
    },
    {
        "name": "llama3.1",
        "icon": "assets/models_logo/llama.png",
        "description": "Llama 3.1 is a new state-of-the-art model from Meta available in 8B, 70B and 405B parameter sizes.",
        "tags": ["llama", "tools"],
        "sizes": ["8b", "70b", "405b"]
    },
    {
        "name": "nomic-embed-text",
        "icon": "assets/models_logo/nomic.png",
        "description": "A high-performing open embedding model with a large token context window.",
        "tags": ["embedding"],
        "sizes": []
    },
    {
        "name": "llama3.2",
        "icon": "assets/models_logo/llama.png",
        "description": "Meta's Llama 3.2 goes small with 1B and 3B models.",
        "tags": ["tools"],
        "sizes": ["1b", "3b"]
    },
    {
        "name": "mistral",
        "icon": "assets/models_logo/mistral.png",
        "description": "The 7B model released by Mistral AI, updated to version 0.3.",
        "tags": ["tools"],
        "sizes": ["7b"]
    },
    {
        "name": "qwen2.5",
        "icon": "assets/models_logo/qwen.png",
        "description": "Qwen2.5 models are pretrained on Alibaba's latest large-scale dataset, encompassing up to 18 trillion tokens. The model supports up to 128K tokens and has multilingual support.",
        "tags": ["tools"],
        "sizes": ["0.5b", "1.5b", "3b", "7b", "14b", "32b", "72b"]
    },
    {
        "name": "llama3",
        "icon": "assets/models_logo/llama.png",
        "description": "Meta Llama 3: The most capable openly available LLM to date.",
        "tags": [],
        "sizes": ["8b", "70b"]
    },
    {
        "name": "llava",
        "icon": "assets/models_logo/llava.png",
        "description": "LLaVA is a novel end-to-end trained large multimodal model that combines a vision encoder and Vicuna for general-purpose visual and language understanding.",
        "tags": ["vision"],
        "sizes": ["7b", "13b", "34b"]
    },
        {
        "name": "phi3",
        "icon": "assets/models_logo/phi.png",
        "description": "Phi-3 is a family of lightweight 3B (Mini) and 14B (Medium) state-of-the-art open models by Microsoft.",
        "tags": ["phi"],
        "sizes": ["3.8b", "14b"]
    },
    {
        "name": "gemma2",
        "icon": "assets/models_logo/gemma.png",
        "description": "Google Gemma 2 is a high-performing and efficient model available in three sizes: 2B, 9B, and 27B.",
        "tags": ["gemma"],
        "sizes": ["2b", "9b", "27b"]
    },
    {
        "name": "qwen2.5-coder",
        "icon": "assets/models_logo/qwen.png",
        "description": "The latest series of Code-Specific Qwen models, with significant improvements in code generation, code reasoning, and code fixing.",
        "tags": ["qwen", "tools"],
        "sizes": ["0.5b", "1.5b", "3b", "7b", "14b", "32b"]
    },
    {
        "name": "gemma",
        "icon": "assets/models_logo/gemma.png",
        "description": "Gemma is a family of lightweight, state-of-the-art open models built by Google DeepMind. Updated to version 1.1.",
        "tags": ["gemma"],
        "sizes": ["2b", "7b"]
    },
    {
        "name": "qwen",
        "icon": "assets/models_logo/qwen.png",
        "description": "Qwen 1.5 is a series of large language models by Alibaba Cloud spanning from 0.5B to 110B parameters.",
        "tags": ["qwen"],
        "sizes": ["0.5b", "1.8b", "4b", "7b", "14b", "32b", "72b", "110b"]
    },
    {
        "name": "mxbai-embed-large",
        "icon": "assets/models_logo/mxbai.png",
        "description": "State-of-the-art large embedding model from mixedbread.ai.",
        "tags": ["mxbai", "embedding"],
        "sizes": ["335m"]
    },
    {
        "name": "qwen2",
        "icon": "assets/models_logo/qwen.png",
        "description": "Qwen2 is a new series of large language models from Alibaba group.",
        "tags": ["qwen", "tools"],
        "sizes": ["0.5b", "1.5b", "7b", "72b"]
    },
    {
        "name": "llama2",
        "icon": "assets/models_logo/llama.png",
        "description": "Llama 2 is a collection of foundation language models ranging from 7B to 70B parameters.",
        "tags": ["llama"],
        "sizes": ["7b", "13b", "70b"]
    },
    {
        "name": "phi4",
        "icon": "assets/models_logo/phi.png",
        "description": "Phi-4 is a 14B parameter, state-of-the-art open model from Microsoft.",
        "tags": ["phi"],
        "sizes": ["14b"]
    },
    {
        "name": "minicpm-v",
        "icon": "assets/models_logo/minicpm.png",
        "description": "A series of multimodal LLMs (MLLMs) designed for vision-language understanding.",
        "tags": ["minicpm", "vision"],
        "sizes": ["8b"]
    },
    {
        "name": "codellama",
        "icon": "assets/models_logo/llama.png",
        "description": "A large language model that can use text prompts to generate and discuss code.",
        "tags": ["llama"],
        "sizes": ["7b", "13b", "34b", "70b"]
    }
]