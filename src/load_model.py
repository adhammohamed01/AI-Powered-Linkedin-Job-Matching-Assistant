from gensim.models import FastText
from transformers import AutoTokenizer, BitsAndBytesConfig
import torch
from transformers import AutoModelForCausalLM
# llama_token="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"
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

_model = None
LLAMA_MODEL = None

def get_model(path="fastext/fasttext_skills.model"):
    global _model
    if _model is None:
        print("Loading model...")
        _model = FastText.load(path)
        print("Model loaded.")
    return _model

# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_compute_dtype=torch.float16,
#     bnb_4bit_quant_storage=torch.uint8
# )


def get_llama_model(path="llama"):
    global LLAMA_MODEL
    if LLAMA_MODEL is None:
        print("Loading llama model")
        LLAMA_MODEL = AutoModelForCausalLM.from_pretrained(
            path,
            trust_remote_code=True,
            # quantization_config=bnb_config,
            device_map="cuda:0"  # Optional: automatically place on GPU if available
        )
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        print("Model loaded.")
    return LLAMA_MODEL, tokenizer


# def get_llama(path="llama"):
#     print("Loading model from local directory with bitsandbytes config...")
#     MODEL = AutoModelForCausalLM.from_pretrained(
#         path,
#         trust_remote_code=True,
#         #quantization_config=bnb_config,
#         device_map="cuda:0"  
#     )
#     return MODEL

# def get_tokenizer(path="llama"):
#     tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
#     return tokenizer



# "quantization_config": {
#     "_load_in_4bit": false,
#     "_load_in_8bit": false,
#     "bnb_4bit_compute_dtype": "float16",
#     "bnb_4bit_quant_storage": "uint8",
#     "bnb_4bit_quant_type": "nf4",
#     "bnb_4bit_use_double_quant": true,
#     "llm_int8_enable_fp32_cpu_offload": false,
#     "llm_int8_has_fp16_weight": false,
#     "llm_int8_skip_modules": null,
#     "llm_int8_threshold": 6.0,
#     "load_in_4bit": false,
#     "load_in_8bit": false,
#     "quant_method": "bitsandbytes"
#   },