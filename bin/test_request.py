from openai import OpenAI

client = OpenAI(
    base_url = "https://api.scaleway.ai/f515e043-422b-48bf-95a7-2da7063d7858/v1",
    api_key = "a3c535e8-93ba-46bf-847e-7115853dcc0e" 
)


response = client.chat.completions.create(
  model="qwen3-235b-a22b-instruct-2507",
  messages=[
        { "role": "system", "content": "You are a helpful assistant" },
    #     { "role": "user", "content": """You are a critical content relevance filter for a telecommunications intelligence system focused on the Polish market.
    # Your task: Analyze the provided text and determine with high confidence whether it is directly relevant to:
    # - The Polish telecommunications market and its dynamics
    # - Major Polish telecom operators (Play, Orange, T-Mobile, Plus) and their strategic initiatives
    # - Polish regulatory bodies (UKE - President of Office of Electronic Communications, UOKiK - President of Office of Competition and Consumer Protection)
    # - Government decisions, policy announcements, or legislative initiatives affecting the Polish telecom sector
    # - Infrastructure development (5G rollout, fiber expansion, spectrum allocation)
    # - Regulatory framework changes (net neutrality, roaming policies, spectrum licensing)
    # - Market competition dynamics specific to Poland

    # Important considerations:
    # 1. Content must be DIRECTLY relevant to Polish market - not general global telecom trends
    # 2. Operator news must relate to their Polish operations or strategy
    # 3. Regulatory content must be applicable to Polish jurisdiction
    # 4. Consider both explicit mentions of Poland and contextual relevance

    # Respond ONLY with "YES" or "NO" - no explanation needed.

    # Content to analyze:"""},
    {"role": "system", "content": "Who are you"}
  ],
  max_tokens=512,
  temperature=0.7,
  top_p=0.8,
  presence_penalty=0,
  stream=True
)

for chunk in response:
  if chunk.choices and chunk.choices[0].delta.content:
   print(chunk.choices[0].delta.content, end="", flush=True)