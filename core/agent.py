# core/agent.py
import os
import json
import re
from dotenv import load_dotenv
from ollama import AsyncClient # Changed to AsyncClient
from core.tools import tools_schema, search_company_documents, search_org_chart
from core.schemas import AgentOutput
from pydantic import ValidationError

load_dotenv()

client = AsyncClient( # Initialized as Async
    host='https://ollama.com',
    headers={'Authorization': f"Bearer {os.getenv('OLLAMA_API_KEY')}"}
)

async def run_autonomous_agent(user_prompt: str) -> AgentOutput:
    print(f"\n🧠 Agent is analyzing request: '{user_prompt}'")
    
    messages = [
        {"role": "system", "content": "You are Omni-Agent..."},
        {"role": "user", "content": user_prompt}
    ]
    
    for step in range(5):
        # Await the chat call
        response = await client.chat(
            model="qwen3-next:80b-cloud",
            messages=messages,
            tools=tools_schema
        )
        
        message = response['message']
        messages.append(message) # Save the AI's thought/action to history
        
        tool_calls_to_execute = []
        
        # --- UNIVERSAL OUTPUT PARSER ---
        # 1. Check if the model used the native API structure
        if message.get('tool_calls'):
            tool_calls_to_execute = message['tool_calls']
            
        # 2. Check if the model went rogue and leaked XML or JSON directly into the text
        elif message.get('content'):
            raw_text = message['content']
            if "<tools>" in raw_text or "<tool_call>" in raw_text:
                matches = re.findall(r'\{.*?\}', raw_text, re.DOTALL)
                for match in matches:
                    try:
                        parsed = json.loads(match)
                        if "name" in parsed and "arguments" in parsed:
                            tool_calls_to_execute.append({'function': parsed})
                    except json.JSONDecodeError:
                        pass
        # -------------------------------
                    
        # If no tools were requested, the agent believes it has all the info!
        if not tool_calls_to_execute:
            print("   [AGENT] Information gathering complete.")
            break
            
        # Execute the requested Tools
        for tool_call in tool_calls_to_execute:
            func_name = tool_call['function']['name']
            args = tool_call['function']['arguments']
            
            # Route to our actual Python functions
            if func_name == "search_company_documents":
                result = search_company_documents(args.get('query', ''))
            elif func_name == "search_org_chart":
                result = search_org_chart(args.get('target_entity', ''))
            else:
                result = "Error: Unknown tool."
                
            # Feed the data back to the LLM
            messages.append({"role": "tool", "content": result, "name": func_name})

    # =========================================================
    # STEP 2: The Synthesizer (Structured Output Formatting)
    # =========================================================
    print("   [AGENT] Synthesizing final structured JSON output...")
    
    # Explicitly stringify the schema so the model can read it in the prompt
    schema_string = json.dumps(AgentOutput.model_json_schema(), indent=2)
    
    # Reinforce the prompt with explicit instructions and the schema
    messages.append({
        "role": "user",
        "content": (
            "You have gathered the necessary information. Now, synthesize your final answer.\n"
            "CRITICAL: You MUST format your response using EXACTLY this JSON schema:\n"
            f"{schema_string}\n\n"
            "Do NOT invent your own keys like 'rules'. You must use 'conversational_reply', "
            "'documents_cited', and 'suggested_contacts'."
        )
    })
    
    # We call the model again, keeping the format constraint as a backup
    synth_response = await client.chat(
        model="qwen3-next:80b-cloud", 
        messages=messages,
        format=AgentOutput.model_json_schema()
    )
    
    raw_content = synth_response['message']['content'].strip()
    
    # Defensive parsing: Clean markdown code blocks
    if raw_content.startswith("```json"):
        raw_content = raw_content[7:-3].strip()
    elif raw_content.startswith("```"):
        raw_content = raw_content[3:-3].strip()
    
    # Validate and return the final Pydantic object
    try:
        parsed_json = json.loads(raw_content)
        return AgentOutput(**parsed_json)
    # CATCH BOTH JSON ERRORS AND PYDANTIC VALIDATION ERRORS!
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"   [ERROR] Failed to parse or validate final output: {e}")
        print(f"   [DEBUG RAW OUTPUT] {raw_content}")
        
        # Graceful fallback so the API doesn't crash 
        return AgentOutput(
            conversational_reply="I found the information, but an error occurred while formatting it for the dashboard.",
            documents_cited=[],
            suggested_contacts=[]
        )