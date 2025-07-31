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
    },
    {
        "name": "tinyllama",
        "icon": "assets/models_logo/llama.png",
        "description": "The TinyLlama project is an open endeavor to train a compact 1.1B Llama model on 3 trillion tokens.",
        "tags": ["llama"],
        "sizes": ["1.1b"]
    },
    {
        "name": "llama3.3",
        "icon": "assets/models_logo/llama.png",
        "description": "New state of the art 70B model. Llama 3.3 70B offers similar performance compared to the Llama 3.1 405B model.",
        "tags": ["llama", "tools"],
        "sizes": ["70b"]
    },
    {
        "name": "llama3.2-vision",
        "icon": "assets/models_logo/llama.png",
        "description": "Llama 3.2 Vision is a collection of instruction-tuned image reasoning generative models in 11B and 90B sizes.",
        "tags": ["llama", "vision"],
        "sizes": ["11b", "90b"]
    },
    {
        "name": "dolphin3",
        "icon": "assets/models_logo/dolphin.png",
        "description": "Dolphin 3.0 Llama 3.1 8B 🐬 is the next generation of the Dolphin series for general purpose use, including coding and agentic reasoning.",
        "tags": ["dolphin"],
        "sizes": ["8b"]
    },
    {
        "name": "mistral-nemo",
        "icon": "assets/models_logo/mistral.png",
        "description": "A state-of-the-art 12B model with 128k context length, built by Mistral AI in collaboration with NVIDIA.",
        "tags": ["mistral", "tools"],
        "sizes": ["12b"]
    },
    {
        "name": "olmo2",
        "icon": "assets/models_logo/olmo.png",
        "description": "OLMo 2 is a family of 7B and 13B models trained on up to 5T tokens, competitive with Llama 3.1.",
        "tags": ["olmo"],
        "sizes": ["7b", "13b"]
    },
    {
        "name": "deepseek-v3",
        "icon": "assets/models_logo/deepseek.png",
        "description": "A strong Mixture-of-Experts (MoE) language model with 671B total parameters with 37B activated for each token.",
        "tags": ["deepseek"],
        "sizes": ["671b"]
    },
    {
        "name": "bge-m3",
        "icon": "assets/models_logo/bge.png",
        "description": "BGE-M3 is a new model from BAAI for Multi-Functionality, Multi-Linguality, and Multi-Granularity.",
        "tags": ["bge", "embedding"],
        "sizes": ["567m"]
    },
    {
        "name": "qwq",
        "icon": "assets/models_logo/qwq.png",
        "description": "QwQ is the reasoning model of the Qwen series.",
        "tags": ["qwq", "tools"],
        "sizes": ["32b"]
    },
    {
        "name": "mistral-small",
        "icon": "assets/models_logo/mistral.png",
        "description": "Mistral Small 3 sets a new benchmark in the 'small' LLM category below 70B.",
        "tags": ["mistral", "tools"],
        "sizes": ["22b", "24b"]
    },
    {
        "name": "llava-llama3",
        "icon": "assets/models_logo/llava.png",
        "description": "A LLaVA model fine-tuned from Llama 3 Instruct with better benchmark scores.",
        "tags": ["llava", "vision"],
        "sizes": ["8b"]
    },
    {
        "name": "smollm2",
        "icon": "assets/models_logo/smoll.png",
        "description": "SmolLM2 is a family of compact language models in 135M, 360M, and 1.7B sizes.",
        "tags": ["smoll", "tools"],
        "sizes": ["135m", "360m", "1.7b"]
    },
    {
        "name": "llama2-uncensored",
        "icon": "assets/models_logo/llama.png",
        "description": "Uncensored Llama 2 model by George Sung and Jarrad Hope.",
        "tags": ["llama"],
        "sizes": ["7b", "70b"]
    },
    {
        "name": "mixtral",
        "icon": "assets/models_logo/mistral.png",
        "description": "A set of Mixture of Experts models with open weights from Mistral AI.",
        "tags": ["mistral", "tools"],
        "sizes": ["8x7b", "8x22b"]
    },
    {
        "name": "starcoder2",
        "icon": "assets/models_logo/starcoder.png",
        "description": "StarCoder2 is the next generation of transparently trained open code LLMs.",
        "tags": ["star"],
        "sizes": ["3b", "7b", "15b"]
    },
    {
        "name": "deepseek-coder-v2",
        "icon": "assets/models_logo/deepseek.png",
        "description": "An open-source MoE code model achieving GPT-4 Turbo-level performance on code tasks.",
        "tags": ["deepseek"],
        "sizes": ["16b", "236b"]
    },
    {
        "name": "all-minilm",
        "icon": "assets/models_logo/phi.png",
        "description": "Embedding models trained on very large sentence-level datasets.",
        "tags": ["minilm", "embedding"],
        "sizes": ["22m", "33m"]
    },
    {
        "name": "deepseek-coder",
        "icon": "assets/models_logo/deepseek.png",
        "description": "DeepSeek Coder is a capable coding model trained on two trillion code and natural language tokens.",
        "tags": ["deepseek"],
        "sizes": ["1.3b", "6.7b", "33b"]
    },
    {
        "name": "snowflake-arctic-embed",
        "icon": "assets/models_logo/snowflake.png",
        "description": "Text embedding models by Snowflake, optimized for performance.",
        "tags": ["snowflake", "embedding"],
        "sizes": ["22m", "33m", "110m", "137m", "335m"]
    },
    {
        "name": "codegemma",
        "icon": "assets/models_logo/gemma.png",
        "description": "Powerful, lightweight models that perform a variety of coding tasks including reasoning and instruction following.",
        "tags": ["gemma"],
        "sizes": ["2b", "7b"]
    },
    {
        "name": "phi",
        "icon": "assets/models_logo/phi.png",
        "description": "Phi-2: a 2.7B language model by Microsoft Research with outstanding reasoning capabilities.",
        "tags": ["phi"],
        "sizes": ["2.7b"]
    },
    {
        "name": "dolphin-mixtral",
        "icon": "assets/models_logo/dolphin.png",
        "description": "Uncensored, 8x7b and 8x22b fine-tuned models based on Mixtral by Eric Hartford.",
        "tags": ["dolphin"],
        "sizes": ["8x7b", "8x22b"]
    },
    {
        "name": "openthinker",
        "icon": "assets/models_logo/openthinker.png",
        "description": "An open-source reasoning model family derived from DeepSeek-R1.",
        "tags": ["openthinker"],
        "sizes": ["7b", "32b"]
    },
    {
        "name": "llama4",
        "icon": "assets/models_logo/llama.png",
        "description": "Meta's latest collection of multimodal models.",
        "tags": ["llama", "vision", "tools"],
        "sizes": ["16x17b", "128x17b"]
    },
    {
        "name": "orca-mini",
        "icon": "assets/models_logo/phi.png",
        "description": "A general-purpose model for entry-level hardware ranging from 3B to 70B.",
        "tags": [],
        "sizes": ["3b", "7b", "13b", "70b"]
    },
    {
        "name": "wizardlm2",
        "icon": "assets/models_logo/wizardlm.png",
        "description": "Microsoft's LLM with improved multilingual, reasoning and agent use case performance.",
        "tags": ["wizardlm"],
        "sizes": ["7b", "8x22b"]
    },
    {
        "name": "smollm",
        "icon": "assets/models_logo/smoll.png",
        "description": "A family of small models trained on a new high-quality dataset.",
        "tags": ["smoll"],
        "sizes": ["135m", "360m", "1.7b"]
    },
    {
        "name": "dolphin-mistral",
        "icon": "assets/models_logo/dolphin.png",
        "description": "Uncensored Dolphin model based on Mistral for coding tasks. Version 2.8.",
        "tags": ["dolphin"],
        "sizes": ["7b"]
    },
    {
        "name": "codestral",
        "icon": "assets/models_logo/mistral.png",
        "description": "Mistral AI’s first code model designed for generation tasks.",
        "tags": ["mistral"],
        "sizes": ["22b"]
    },
    {
        "name": "dolphin-llama3",
        "icon": "assets/models_logo/dolphin.png",
        "description": "Dolphin 2.9 based on Llama 3 for coding and instruction, available in 8B and 70B sizes.",
        "tags": ["dolphin"],
        "sizes": ["8b", "70b"]
    },
    {
        "name": "command-r",
        "icon": "assets/models_logo/command.png",
        "description": "Command R is a LLM optimized for conversational and long-context tasks.",
        "tags": ["command", "tools"],
        "sizes": ["35b"]
    },
    {
        "name": "hermes3",
        "icon": "assets/models_logo/hermes.png",
        "description": "Hermes 3 is the latest LLM from Nous Research with improved reasoning and agentic skills.",
        "tags": ["hermes", "tools"],
        "sizes": ["3b", "8b", "70b", "405b"]
    },
    {
        "name": "phi3.5",
        "icon": "assets/models_logo/phi.png",
        "description": "Phi-3.5: A 3.8B model outperforming similarly and larger-sized models.",
        "tags": ["phi"],
        "sizes": ["3.8b"]
    },
    {
        "name": "yi",
        "icon": "assets/models_logo/yi.png",
        "description": "Yi 1.5 is a bilingual high-performing LLM.",
        "tags": ["yi"],
        "sizes": ["6b", "9b", "34b"]
    },
    {
        "name": "zephyr",
        "icon": "assets/models_logo/zephyr.jpeg",
        "description": "Zephyr is a series of fine-tuned Mistral and Mixtral models trained as helpful assistants.",
        "tags": ["zephyr"],
        "sizes": ["7b", "141b"]
    },

]