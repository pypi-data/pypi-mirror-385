from dataclasses import dataclass

@dataclass
class LLMModel:
    name: str
    input_cost: float = 0
    output_cost: float = 0


# OpenAI
gpt_4o = LLMModel(name='openai/gpt-4o', input_cost=2.5, output_cost=10.0)
gpt_4o_mini = LLMModel(name='openai/gpt-4o-mini', input_cost=0.15, output_cost=0.60)
gpt_4_1 = LLMModel(name='openai/gpt-4.1', input_cost=2, output_cost=8.0)
gpt_4_1_mini = LLMModel(name='openai/gpt-4.1-mini', input_cost=0.4, output_cost=1.6)
gpt_4_1_nano = LLMModel(name='openai/gpt-4.1-nano', input_cost=0.1, output_cost=0.4)
o4_mini = LLMModel(name='openai/o4-mini', input_cost=1.1, output_cost=4.4)
o4_mini_high = LLMModel(name='openai/o4-mini-high', input_cost=1.1, output_cost=4.4)
o3 = LLMModel(name='openai/o3', input_cost=2, output_cost=8)
gpt_5_nano = LLMModel(name='openai/gpt-5-nano', input_cost=0.05, output_cost=0.4)
gpt_5_mini = LLMModel(name='openai/gpt-5-mini', input_cost=0.25, output_cost=2)
gpt_5 = LLMModel(name='openai/gpt-5', input_cost=1.25, output_cost=10)
gpt_oss_20B_free = LLMModel(name='openai/gpt-oss-20b:free', input_cost=0, output_cost=0)
gpt_oss_20B = LLMModel(name='openai/gpt-oss-20b', input_cost=0.06, output_cost=0.2)
gpt_oss_120B = LLMModel(name='openai/gpt-oss-120b', input_cost=0.25, output_cost=0.69)

# Anthropic
claude_3_7_sonnet = LLMModel(name='anthropic/claude-3.7-sonnet', input_cost=3.0, output_cost=15.0)
claude_3_7_sonnet_thinking = LLMModel(name='anthropic/claude-3.7-sonnet:thinking', input_cost=3.0, output_cost=15.0)
claude_3_5_haiku = LLMModel(name='anthropic/claude-3.5-haiku', input_cost=0.8, output_cost=4.0)
claude_4_sonnet = LLMModel(name='anthropic/claude-sonnet-4', input_cost=3.0, output_cost=15.0)
claude_4_opus = LLMModel(name='anthropic/claude-opus-4', input_cost=15, output_cost=75)
claude_4_1_opus = LLMModel(name='anthropic/claude-opus-4.1', input_cost=15, output_cost=75)

# Google
gemini_2_0_flash = LLMModel(name='google/gemini-2.0-flash-001', input_cost=0.1, output_cost=0.4)
gemini_2_5_flash_lite = LLMModel(name='google/gemini-2.5-flash-lite', input_cost=0.1, output_cost=0.4)
gemini_2_5_flash = LLMModel(name='google/gemini-2.5-flash', input_cost=0.3, output_cost=2.5)
gemini_2_5_pro = LLMModel(name='google/gemini-2.5-pro', input_cost=1.25, output_cost=10)

# Deepseek
deepseek_v3_free = LLMModel(name='deepseek/deepseek-chat-v3-0324:free', input_cost=0, output_cost=0)
deepseek_v3 = LLMModel(name='deepseek/deepseek-chat-v3-0324', input_cost=0.3, output_cost=1.2)
deepseek_r1_free = LLMModel(name='deepseek/deepseek-r1:free', input_cost=0, output_cost=0)
deepseek_r1 = LLMModel(name='deepseek/deepseek-r1', input_cost=0.5, output_cost=2.2)
deepseek_v3_1 = LLMModel(name='deepseek/deepseek-chat-v3.1', input_cost=0.55, output_cost=1.68)

# xAI
grok_3_mini = LLMModel(name='x-ai/grok-3-mini-beta', input_cost=0.3, output_cost=0.5)
grok_3 = LLMModel(name='x-ai/grok-3-beta', input_cost=3, output_cost=15)
grok_4 = LLMModel(name='x-ai/grok-4', input_cost=3, output_cost=15)

# Microsoft
mai_ds_r1_free = LLMModel(name="microsoft/mai-ds-r1:free", input_cost=0, output_cost=0)

# Others
llama_4_maverick_free = LLMModel(name="meta-llama/llama-4-maverick:free", input_cost=0, output_cost=0)
llama_4_scout = LLMModel(name="meta-llama/llama-4-scout", input_cost=0.11, output_cost=0.34)
mistral_small_3_1_24B_free = LLMModel(name="mistralai/mistral-small-3.1-24b-instruct:free", input_cost=0, output_cost=0)

