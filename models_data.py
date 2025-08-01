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
    {
        "name": "granite3.3",
        "icon": "assets/models_logo/granite.png",
        "description": "IBM Granite 2B and 8B models with 128K context, fine-tuned for reasoning and instruction-following.",
        "tags": ["tools"],
        "sizes": ["2b", "8b"]
    },
    {
        "name": "phi4-mini",
        "icon": "assets/models_logo/phi.png",
        "description": "Phi-4-mini enhances multilingual support, reasoning, math, and adds function calling.",
        "tags": ["tools"],
        "sizes": ["3.8b"]
    },
    {
        "name": "moondream",
        "icon": "assets/models_logo/moondream.png",
        "description": "Moondream2 is a small vision-language model optimized for edge devices.",
        "tags": ["vision"],
        "sizes": ["1.8b"]
    },
    {
        "name": "granite-code",
        "icon": "assets/models_logo/granite.png",
        "description": "A family of open foundation models by IBM for code intelligence.",
        "tags": [],
        "sizes": ["3b", "8b", "20b", "34b"]
    },
    {
        "name": "wizard-vicuna-uncensored",
        "icon": "assets/models_logo/wizardlm.png",
        "description": "Uncensored versions of Llama 2 by Eric Hartford, with 7B, 13B, and 30B parameters.",
        "tags": [],
        "sizes": ["7b", "13b", "30b"]
    },
    {
        "name": "devstral",
        "icon": "assets/models_logo/mistral.png",
        "description": "Devstral: the best open source model for coding agents.",
        "tags": ["tools"],
        "sizes": ["24b"]
    },
    {
        "name": "magistral",
        "icon": "assets/models_logo/mistral.png",
        "description": "Small, efficient reasoning model with 24B parameters.",
        "tags": ["tools", "thinking"],
        "sizes": ["24b"]
    },
    {
        "name": "starcoder",
        "icon": "assets/models_logo/starcoder.png",
        "description": "StarCoder is a code generation model trained on 80+ programming languages.",
        "tags": [],
        "sizes": ["1b", "3b", "7b", "15b"]
    },
    {
        "name": "phi4-reasoning",
        "icon": "assets/models_logo/phi.png",
        "description": "Phi 4 reasoning models excel at complex tasks with 14B parameters.",
        "tags": [],
        "sizes": ["14b"]
    },
    {
        "name": "mistral-small3.1",
        "icon": "assets/models_logo/mistral.png",
        "description": "Mistral Small 3.1 enhances vision understanding and long-context capabilities.",
        "tags": ["vision", "tools"],
        "sizes": ["24b"]
    },
    {
        "name": "vicuna",
        "icon": "assets/models_logo/vicuna.jpeg",
        "description": "General use chat model based on Llama and Llama 2 with 2K to 16K context sizes.",
        "tags": [],
        "sizes": ["7b", "13b", "33b"]
    },
    {
        "name": "cogito",
        "icon": "assets/models_logo/cogito.png",
        "description": "Cogito v1 Preview is a hybrid reasoning model that outperforms top open models across most benchmarks.",
        "tags": ["tools"],
        "sizes": ["3b", "8b", "14b", "32b", "70b"]
    },
    {
        "name": "deepcoder",
        "icon": "assets/models_logo/deepcoder.png",
        "description": "DeepCoder is a fully open-source coder model, available in 1.5B and 14B sizes.",
        "tags": ["code"],
        "sizes": ["1.5b", "14b"]
    },
    {
        "name": "openchat",
        "icon": "assets/models_logo/openchat.png",
        "description": "OpenChat models outperform ChatGPT in benchmarks and support general-purpose chat capabilities.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "mistral-openorca",
        "icon": "assets/models_logo/phi.png",
        "description": "A 7B model fine-tuned with OpenOrca dataset on top of Mistral for improved instruction following.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "codegeex4",
        "icon": "assets/models_logo/codegeex.png",
        "description": "Versatile model for AI-assisted software development and code completion.",
        "tags": ["code"],
        "sizes": ["9b"]
    },
    {
        "name": "deepseek-llm",
        "icon": "assets/models_logo/deepseek.png",
        "description": "An advanced bilingual model trained on 2 trillion tokens for general language tasks.",
        "tags": [],
        "sizes": ["7b", "67b"]
    },
    {
        "name": "deepseek-v2",
        "icon": "assets/models_logo/deepseek.png",
        "description": "A strong and efficient Mixture-of-Experts language model by DeepSeek.",
        "tags": [],
        "sizes": ["16b", "236b"]
    },
    {
        "name": "openhermes",
        "icon": "assets/models_logo/hermes.png",
        "description": "OpenHermes 2.5 is a 7B model trained on open datasets, designed for chat and reasoning tasks.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "granite3.2-vision",
        "icon": "assets/models_logo/granite.png",
        "description": "Compact vision-language model designed for visual document understanding.",
        "tags": ["vision", "tools"],
        "sizes": ["2b"]
    },
    {
        "name": "codeqwen",
        "icon": "assets/models_logo/qwen.png",
        "description": "CodeQwen1.5 is pretrained on extensive code datasets for software generation.",
        "tags": ["code"],
        "sizes": ["7b"]
    },
    {
        "name": "mistral-large",
        "icon": "assets/models_logo/mistral.png",
        "description": "Mistral's flagship 123B model with strong performance in code, math, and reasoning.",
        "tags": ["tools"],
        "sizes": ["123b"]
    },
    {
        "name": "llama2-chinese",
        "icon": "assets/models_logo/llama.png",
        "description": "Llama 2 model fine-tuned to enhance Chinese dialogue performance.",
        "tags": [],
        "sizes": ["7b", "13b"]
    },
    {
        "name": "aya",
        "icon": "assets/models_logo/command.png",
        "description": "Aya is a multilingual model supporting 23 languages with competitive performance.",
        "tags": [],
        "sizes": ["8b", "35b"]
    },
    {
        "name": "tinydolphin",
        "icon": "assets/models_logo/dolphin.png",
        "description": "An experimental 1.1B model based on TinyLlama and trained on Dolphin 2.8 data.",
        "tags": [],
        "sizes": ["1.1b"]
    },
    {
        "name": "qwen2-math",
        "icon": "assets/models_logo/qwen.png",
        "description": "Specialized math model built on Qwen2 with superior mathematical reasoning.",
        "tags": [],
        "sizes": ["1.5b", "7b", "72b"]
    },
    {
        "name": "glm4",
        "icon": "assets/models_logo/codegeex.png",
        "description": "GLM4 is a strong multilingual LLM with performance competitive with Llama 3.",
        "tags": [],
        "sizes": ["9b"]
    },
    {
        "name": "stable-code",
        "icon": "assets/models_logo/stablecode.png",
        "description": "Stable Code 3B is a compact model for instruction and code completion.",
        "tags": ["code"],
        "sizes": ["3b"]
    },
    {
        "name": "nous-hermes2",
        "icon": "assets/models_logo/hermes.png",
        "description": "Family of models by Nous Research tailored for science and code.",
        "tags": [],
        "sizes": ["10.7b", "34b"]
    },
    {
        "name": "wizardcoder",
        "icon": "assets/models_logo/wizardlm.png",
        "description": "High-performance model for code generation tasks.",
        "tags": ["code"],
        "sizes": ["33b"]
    },
    {
        "name": "command-r-plus",
        "icon": "assets/models_logo/command.png",
        "description": "Scalable enterprise-grade LLM optimized for real-world use cases.",
        "tags": ["tools"],
        "sizes": ["104b"]
    },
    {
        "name": "bakllava",
        "icon": "assets/models_logo/llava.png",
        "description": "Multimodal model based on Mistral 7B with the LLaVA architecture.",
        "tags": ["vision"],
        "sizes": ["7b"]
    },
    {
        "name": "neural-chat",
        "icon": "assets/models_logo/neuralchat.png",
        "description": "Fine-tuned Mistral model with strong domain and language coverage.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "granite3.2",
        "icon": "assets/models_logo/granite.png",
        "description": "Long-context AI models fine-tuned for thinking and reasoning capabilities.",
        "tags": ["tools"],
        "sizes": ["2b", "8b"]
    },
    {
        "name": "stablelm2",
        "icon": "assets/models_logo/stablecode.png",
        "description": "StableLM 2 models trained on multilingual data with high performance.",
        "tags": [],
        "sizes": ["1.6b", "12b"]
    },
    {
        "name": "bge-large",
        "icon": "assets/models_logo/bge.png",
        "description": "BAAI’s large embedding model mapping texts to semantic vector space.",
        "tags": ["embedding"],
        "sizes": ["335m"]
    },
    {
        "name": "sqlcoder",
        "icon": "assets/models_logo/sqlcoder.png",
        "description": "SQLCoder is a specialized model for generating SQL from natural language.",
        "tags": ["code"],
        "sizes": ["7b", "15b"]
    },
    {
        "name": "llama3-chatqa",
        "icon": "assets/models_logo/llama.png",
        "description": "A model from NVIDIA based on Llama 3 that excels at conversational question answering (QA) and retrieval-augmented generation (RAG).",
        "tags": ["llama3", "qa", "rag"],
        "sizes": ["8b", "70b"]
    },
    {
        "name": "snowflake-arctic-embed2",
        "icon": "assets/models_logo/snowflake.png",
        "description": "Snowflake's frontier embedding model. Arctic Embed 2.0 adds multilingual support without sacrificing English performance or scalability.",
        "tags": ["embedding"],
        "sizes": ["568m"]
    },
    {
        "name": "reflection",
        "icon": "assets/models_logo/reflection.png",
        "description": "A high-performing model trained with a new technique called Reflection-tuning that teaches a LLM to detect mistakes in its reasoning and correct course.",
        "tags": [],
        "sizes": ["70b"]
    },
    {
        "name": "wizard-math",
        "icon": "assets/models_logo/wizardlm.png",
        "description": "Model focused on math and logic problems.",
        "tags": ["math"],
        "sizes": ["7b", "13b", "70b"]
    },
    {
        "name": "llava-phi3",
        "icon": "assets/models_logo/phi.png",
        "description": "A new small LLaVA model fine-tuned from Phi 3 Mini.",
        "tags": ["vision"],
        "sizes": ["3.8b"]
    },
    {
        "name": "granite3.1-dense",
        "icon": "assets/models_logo/granite.png",
        "description": "The IBM Granite 2B and 8B models are text-only dense LLMs trained on over 12 trillion tokens of data, demonstrating significant improvements over predecessors.",
        "tags": ["tools"],
        "sizes": ["2b", "8b"]
    },
    {
        "name": "granite3-dense",
        "icon": "assets/models_logo/granite.png",
        "description": "IBM Granite 2B and 8B models designed for RAG and code generation tasks.",
        "tags": ["tools"],
        "sizes": ["2b", "8b"]
    },
    {
        "name": "llama3-gradient",
        "icon": "assets/models_logo/llama.png",
        "description": "This model extends LLama-3 8B's context length from 8k to over 1M tokens.",
        "tags": [],
        "sizes": ["8b", "70b"]
    },
    {
        "name": "nous-hermes",
        "icon": "assets/models_logo/nous.png",
        "description": "General use models based on Llama and Llama 2 from Nous Research.",
        "tags": ["nous"],
        "sizes": ["7b", "13b"]
    },
    {
        "name": "dbrx",
        "icon": "assets/models_logo/dbrx.png",
        "description": "DBRX is an open, general-purpose LLM created by Databricks.",
        "tags": [],
        "sizes": ["132b"]
    },
    {
        "name": "exaone3.5",
        "icon": "assets/models_logo/exaone.png",
        "description": "EXAONE 3.5 is a collection of instruction-tuned bilingual models ranging from 2.4B to 32B by LG AI Research.",
        "tags": ["bilingual"],
        "sizes": ["2.4b", "7.8b", "32b"]
    },
    {
        "name": "samantha-mistral",
        "icon": "assets/models_logo/mistral.png",
        "description": "A companion assistant trained in philosophy, psychology, and personal relationships. Based on Mistral.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "yi-coder",
        "icon": "assets/models_logo/yi.png",
        "description": "Yi-Coder is a series of open-source code language models delivering SOTA performance under 10B params.",
        "tags": ["coder"],
        "sizes": ["1.5b", "9b"]
    },
    {
        "name": "dolphincoder",
        "icon": "assets/models_logo/dolphin.png",
        "description": "Uncensored 7B and 15B variant of the Dolphin model family, excelling at code tasks.",
        "tags": ["coding"],
        "sizes": ["7b", "15b"]
    },
    {
        "name": "nemotron-mini",
        "icon": "assets/models_logo/nemotron.png",
        "description": "Commercial-friendly small LLM by NVIDIA optimized for roleplay, RAG QA, and function calling.",
        "tags": ["tools"],
        "sizes": ["4b"]
    },
    {
        "name": "starling-lm",
        "icon": "assets/models_logo/starling.png",
        "description": "A large language model trained by reinforcement learning from AI feedback focused on chatbot helpfulness.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "falcon",
        "icon": "assets/models_logo/falcon.png",
        "description": "A model built by TII for summarization, text generation, and chat.",
        "tags": [],
        "sizes": ["7b", "40b", "180b"]
    },
    {
        "name": "phind-codellama",
        "icon": "assets/models_logo/llama.png",
        "description": "Code generation model based on Code Llama.",
        "tags": ["coding"],
        "sizes": ["34b"]
    },
    {
        "name": "solar",
        "icon": "assets/models_logo/solar.png",
        "description": "A compact, yet powerful 10.7B LLM designed for single-turn conversation.",
        "tags": [],
        "sizes": ["10.7b"]
    },
    {
        "name": "xwinlm",
        "icon": "assets/models_logo/xwin.png",
        "description": "Conversational model based on Llama 2 performing competitively on various benchmarks.",
        "tags": [],
        "sizes": ["7b", "13b"]
    },
    {
        "name": "internlm2",
        "icon": "assets/models_logo/internlm.png",
        "description": "InternLM2.5 is a 7B parameter model tailored for practical scenarios with outstanding reasoning capability.",
        "tags": [],
        "sizes": ["1m", "1.8b", "7b", "20b"]
    },
    {
        "name": "deepscaler",
        "icon": "assets/models_logo/deepseek.png",
        "description": "A fine-tuned version of Deepseek-R1-Distilled-Qwen-1.5B that surpasses the performance of OpenAI’s o1-preview with just 1.5B parameters on popular math evaluations.",
        "tags": [],
        "sizes": ["1.5b"]
    },
    {
        "name": "athene-v2",
        "icon": "assets/models_logo/athene.png",
        "description": "Athene-V2 is a 72B parameter model which excels at code completion, mathematics, and log extraction tasks.",
        "tags": ["tools"],
        "sizes": ["72b"]
    },
    {
        "name": "nemotron",
        "icon": "assets/models_logo/nemotron.png",
        "description": "Llama-3.1-Nemotron-70B-Instruct is a large language model customized by NVIDIA to improve the helpfulness of LLM generated responses to user queries.",
        "tags": ["tools"],
        "sizes": ["70b"]
    },
    {
        "name": "yarn-llama2",
        "icon": "assets/models_logo/llama.png",
        "description": "An extension of Llama 2 that supports a context of up to 128k tokens.",
        "tags": [],
        "sizes": ["7b", "13b"]
    },
    {
        "name": "opencoder",
        "icon": "assets/models_logo/opencoder.png",
        "description": "OpenCoder is an open and reproducible code LLM family which includes 1.5B and 8B models, supporting chat in English and Chinese languages.",
        "tags": [],
        "sizes": ["1.5b", "8b"]
    },
    {
        "name": "dolphin-phi",
        "icon": "assets/models_logo/dolphin.png",
        "description": "2.7B uncensored Dolphin model by Eric Hartford, based on the Phi language model by Microsoft Research.",
        "tags": [],
        "sizes": ["2.7b"]
    },
    {
        "name": "llama3-groq-tool-use",
        "icon": "assets/models_logo/llama.png",
        "description": "A series of models from Groq that represent a significant advancement in open-source AI capabilities for tool use/function calling.",
        "tags": ["tools"],
        "sizes": ["8b", "70b"]
    },
    {
        "name": "exaone-deep",
        "icon": "assets/models_logo/exaone.png",
        "description": "EXAONE Deep exhibits superior capabilities in various reasoning tasks including math and coding benchmarks, ranging from 2.4B to 32B parameters developed and released by LG AI Research.",
        "tags": [],
        "sizes": ["2.4b", "7.8b", "32b"]
    },
    {
        "name": "wizardlm",
        "icon": "assets/models_logo/wizardlm.png",
        "description": "General use model based on Llama 2.",
        "tags": [],
        "sizes": []
    },
    {
        "name": "paraphrase-multilingual",
        "icon": "assets/models_logo/paraphrase-multilingual.png",
        "description": "Sentence-transformers model that can be used for tasks like clustering or semantic search.",
        "tags": ["embedding"],
        "sizes": ["278m"]
    },
    {
        "name": "wizardlm-uncensored",
        "icon": "assets/models_logo/wizardlm.png",
        "description": "Uncensored version of Wizard LM model.",
        "tags": [],
        "sizes": ["13b"]
    },
    {
        "name": "aya-expanse",
        "icon": "assets/models_logo/aya.png",
        "description": "Cohere For AI's language models trained to perform well across 23 different languages.",
        "tags": ["tools"],
        "sizes": ["8b", "32b"]
    },
    {
        "name": "orca2",
        "icon": "assets/models_logo/orca.png",
        "description": "Orca 2 is built by Microsoft research, and are a fine-tuned version of Meta's Llama 2 models. The model is designed to excel particularly in reasoning.",
        "tags": [],
        "sizes": ["7b", "13b"]
    },
    {
        "name": "smallthinker",
        "icon": "assets/models_logo/smallthinker.png",
        "description": "A new small reasoning model fine-tuned from the Qwen 2.5 3B Instruct model.",
        "tags": [],
        "sizes": ["3b"]
    },
    {
        "name": "falcon3",
        "icon": "assets/models_logo/falcon.png",
        "description": "A family of efficient AI models under 10B parameters performant in science, math, and coding through innovative training techniques.",
        "tags": [],
        "sizes": ["1b", "3b", "7b", "10b"]
    },
    {
        "name": "llama-guard3",
        "icon": "assets/models_logo/llama.png",
        "description": "Llama Guard 3 is a series of models fine-tuned for content safety classification of LLM inputs and responses.",
        "tags": [],
        "sizes": ["1b", "8b"]
    },
    {
        "name": "granite-embedding",
        "icon": "assets/models_logo/granite.png",
        "description": "The IBM Granite Embedding 30M and 278M models are text-only dense biencoder embedding models, with 30M available in English only and 278M serving multilingual use cases.",
        "tags": ["embedding"],
        "sizes": ["30m", "278m"]
    },
    {
        "name": "medllama2",
        "icon": "assets/models_logo/llama.png",
        "description": "Fine-tuned Llama 2 model to answer medical questions based on an open source medical dataset.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "nous-hermes2-mixtral",
        "icon": "assets/models_logo/hermes.png",
        "description": "The Nous Hermes 2 model from Nous Research, now trained over Mixtral.",
        "tags": [],
        "sizes": ["8x7b"]
    },
    {
        "name": "stable-beluga",
        "icon": "assets/models_logo/stable-beluga.png",
        "description": "Llama 2 based model fine tuned on an Orca-style dataset. Originally called Free Willy.",
        "tags": [],
        "sizes": ["7b", "13b", "70b"]
    },
    {
        "name": "meditron",
        "icon": "assets/models_logo/llama.png",
        "description": "Open-source medical large language model adapted from Llama 2 to the medical domain.",
        "tags": [],
        "sizes": ["7b", "70b"]
    },
    {
        "name": "granite3-moe",
        "icon": "assets/models_logo/granite.png",
        "description": "The IBM Granite 1B and 3B models are the first mixture of experts (MoE) Granite models from IBM designed for low latency usage.",
        "tags": ["tools"],
        "sizes": ["1b", "3b"]
    },
    {
        "name": "r1-1776",
        "icon": "assets/models_logo/deepseek.png",
        "description": "A version of the DeepSeek-R1 model that has been post trained to provide unbiased, accurate, and factual information by Perplexity.",
        "tags": [],
        "sizes": ["70b", "671b"]
    },
    {
        "name": "deepseek-v2.5",
        "icon": "assets/models_logo/deepseek.png",
        "description": "An upgraded version of DeepSeek-V2 that integrates the general and coding abilities of both DeepSeek-V2-Chat and DeepSeek-Coder-V2-Instruct.",
        "tags": [],
        "sizes": ["236b"]
    },
    {
        "name": "granite3.1-moe",
        "icon": "assets/models_logo/granite.png",
        "description": "The IBM Granite 1B and 3B models are long-context mixture of experts (MoE) Granite models from IBM designed for low latency usage.",
        "tags": ["tools"],
        "sizes": ["1b", "3b"]
    },
    {
        "name": "reader-lm",
        "icon": "assets/models_logo/reader.png",
        "description": "A series of models that convert HTML content to Markdown content, which is useful for content conversion tasks.",
        "tags": [],
        "sizes": ["0.5b", "1.5b"]
    },
    {
        "name": "mistral-small3.2",
        "icon": "assets/models_logo/mistral.png",
        "description": "An update to Mistral Small that improves on function calling, instruction following, and less repetition errors.",
        "tags": ["vision", "tools"],
        "sizes": ["24b"]
    },
    {
        "name": "llama-pro",
        "icon": "assets/models_logo/llama.png",
        "description": "An expansion of Llama 2 that specializes in integrating both general language understanding and domain-specific knowledge, particularly in programming and mathematics.",
        "tags": [],
        "sizes": []
    },
    {
        "name": "yarn-mistral",
        "icon": "assets/models_logo/mistral.png",
        "description": "An extension of Mistral to support context windows of 64K or 128K.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "shieldgemma",
        "icon": "assets/models_logo/gemma.png",
        "description": "ShieldGemma is a set of instruction tuned models for evaluating the safety of text prompt input and text output responses against a set of defined safety policies.",
        "tags": [],
        "sizes": ["2b", "9b", "27b"]
    },
    {
        "name": "nexusraven",
        "icon": "assets/models_logo/nexusraven.png",
        "description": "Nexus Raven is a 13B instruction tuned model for function calling tasks.",
        "tags": [],
        "sizes": ["13b"]
    },
    {
        "name": "command-r7b",
        "icon": "assets/models_logo/command.png",
        "description": "The smallest model in Cohere's R series delivers top-tier speed, efficiency, and quality to build powerful AI applications on commodity GPUs and edge devices.",
        "tags": ["tools"],
        "sizes": ["7b"]
    },
    {
        "name": "mathstral",
        "icon": "assets/models_logo/mistral.png",
        "description": "MathΣtral: a 7B model designed for math reasoning and scientific discovery by Mistral AI.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "everythinglm",
        "icon": "assets/models_logo/everythinglm.jpg",
        "description": "Uncensored Llama2 based model with support for a 16K context window.",
        "tags": [],
        "sizes": ["13b"]
    },
    {
        "name": "codeup",
        "icon": "assets/models_logo/llama.png",
        "description": "Great code generation model based on Llama2.",
        "tags": [],
        "sizes": ["13b"]
    },
    {
        "name": "marco-o1",
        "icon": "assets/models_logo/marco.png",
        "description": "An open large reasoning model for real-world solutions by the Alibaba International Digital Commerce Group (AIDC-AI).",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "stablelm-zephyr",
        "icon": "assets/models_logo/zephyr.jpeg",
        "description": "A lightweight chat model allowing accurate, and responsive output without requiring high-end hardware.",
        "tags": [],
        "sizes": ["3b"]
    },
    {
        "name": "tulu3",
        "icon": "assets/models_logo/tulu.png",
        "description": "Tülu 3 is a leading instruction following model family, offering fully open-source data, code, and recipes by the The Allen Institute for AI.",
        "tags": [],
        "sizes": ["8b", "70b"]
    },
    {
        "name": "solar-pro",
        "icon": "assets/models_logo/solar.png",
        "description": "Solar Pro Preview: an advanced large language model (LLM) with 22 billion parameters designed to fit into a single GPU.",
        "tags": [],
        "sizes": ["22b"]
    },
    {
        "name": "duckdb-nsql",
        "icon": "assets/models_logo/duckdb.png",
        "description": "7B parameter text-to-SQL model made by MotherDuck and Numbers Station.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "falcon2",
        "icon": "assets/models_logo/falcon.png",
        "description": "Falcon2 is an 11B parameters causal decoder-only model built by TII and trained over 5T tokens.",
        "tags": [],
        "sizes": ["11b"]
    },
    {
        "name": "phi4-mini-reasoning",
        "icon": "assets/models_logo/phi4.png",
        "description": "Phi 4 mini reasoning is a lightweight open model that balances efficiency with advanced reasoning ability.",
        "tags": [],
        "sizes": ["3.8b"]
    },
    {
        "name": "magicoder",
        "icon": "assets/models_logo/magicoder.png",
        "description": "Magicoder is a family of 7B parameter models trained on 75K synthetic instruction data using OSS-Instruct.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "mistrallite",
        "icon": "assets/models_logo/mistral.png",
        "description": "MistralLite is a fine-tuned model based on Mistral with enhanced capabilities of processing long contexts.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "codebooga",
        "icon": "assets/models_logo/codebooga.png",
        "description": "A high-performing code instruct model created by merging two existing code models.",
        "tags": [],
        "sizes": ["34b"]
    },
    {
        "name": "bespoke-minicheck",
        "icon": "assets/models_logo/bespoke.png",
        "description": "A state-of-the-art fact-checking model developed by Bespoke Labs.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "wizard-vicuna",
        "icon": "assets/models_logo/vicuna.jpeg",
        "description": "Wizard Vicuna is a 13B parameter model based on Llama 2 trained by MelodysDreamj.",
        "tags": [],
        "sizes": ["13b"]
    },
    {
        "name": "nuextract",
        "icon": "assets/models_logo/phi.png",
        "description": "A 3.8B model fine-tuned on a private high-quality synthetic dataset for information extraction, based on Phi-3.",
        "tags": [],
        "sizes": ["3.8b"]
    },
    {
        "name": "granite3-guardian",
        "icon": "assets/models_logo/granite.png",
        "description": "The IBM Granite Guardian 3.0 2B and 8B models are designed to detect risks in prompts and/or responses.",
        "tags": [],
        "sizes": ["2b", "8b"]
    },
    {
        "name": "megadolphin",
        "icon": "assets/models_logo/dolphin.png",
        "description": "MegaDolphin-2.2-120b is a transformation of Dolphin-2.2-70b created by interleaving the model with itself.",
        "tags": [],
        "sizes": ["120b"]
    },
    {
        "name": "notux",
        "icon": "assets/models_logo/notux.png",
        "description": "A top-performing mixture of experts model, fine-tuned with high-quality data.",
        "tags": [],
        "sizes": ["8x7b"]
    },
    {
        "name": "open-orca-platypus2",
        "icon": "assets/models_logo/open-orca.png",
        "description": "Merge of the Open Orca OpenChat model and the Garage-bAInd Platypus 2 model. Designed for chat and code generation.",
        "tags": [],
        "sizes": ["13b"]
    },
    {
        "name": "notus",
        "icon": "assets/models_logo/notus.png",
        "description": "A 7B chat model fine-tuned with high-quality data and based on Zephyr.",
        "tags": [],
        "sizes": ["7b"]
    },
    {
        "name": "command-a",
        "icon": "assets/models_logo/command.png",
        "description": "111 billion parameter model optimized for demanding enterprises that require fast, secure, and high-quality AI.",
        "tags": ["tools"],
        "sizes": ["111b"]
    },
    {
        "name": "goliath",
        "icon": "assets/models_logo/goliath.png",
        "description": "A language model created by combining two fine-tuned Llama 2 70B models into one.",
        "tags": [],
        "sizes": []
    },
    {
        "name": "sailor2",
        "icon": "assets/models_logo/sailor.png",
        "description": "Sailor2 are multilingual language models made for South-East Asia. Available in 1B, 8B, and 20B parameter sizes.",
        "tags": [],
        "sizes": ["1b", "8b", "20b"]
    },
    {
        "name": "firefunction-v2",
        "icon": "assets/models_logo/firefunction.png",
        "description": "An open weights function calling model based on Llama 3, competitive with GPT-4o function calling capabilities.",
        "tags": ["tools"],
        "sizes": ["70b"]
    },
    {
        "name": "alfred",
        "icon": "assets/models_logo/alfred.png",
        "description": "A robust conversational model designed to be used for both chat and instruct use cases.",
        "tags": [],
        "sizes": ["40b"]
    },
    {
        "name": "command-r7b-arabic",
        "icon": "assets/models_logo/command.png",
        "description": "A new state-of-the-art version of the lightweight Command R7B model that excels in advanced Arabic language capabilities for enterprises in the Middle East and Northern Africa.",
        "tags": ["tools"],
        "sizes": ["7b"]
    }
]