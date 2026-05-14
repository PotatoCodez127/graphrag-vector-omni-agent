# core/agent.py
import os
import json
import re
from dotenv import load_dotenv
from ollama import Client
from core.tools import tools_schema, search_company_documents, search_org_chart
from core.schemas import AgentOutput

# Load environment variables
load_dotenv()

# Initialize Ollama Cloud Client
client = Client(
    host='https://ollama.com',
    headers={'Authorization': f"Bearer {os.getenv('OLLAMA_API_KEY')}"}
)

def run_autonomous_agent(user_prompt: str) -> AgentOutput:
    print(f"\n🧠 Agent is analyzing request: '{user_prompt}'")
    
    # =========================================================
    # STEP 1: The ReAct Loop (Information Gathering)
    # =========================================================
    messages = [
        {
            "role": "system", 
            "content": "You are Omni-Agent, an internal enterprise assistant. Use your tools to search company documents and the organizational chart to gather factual information to answer the user's questions."
        },
        {
            "role": "user", 
            "content": user_prompt
        }
    ]
    
    # Run the loop for a maximum of 5 steps to prevent infinite loops
    for step in range(5):
        print(f"   [AGENT] Thinking (Step {step + 1})...")
        
        # We use a smart model for reasoning and tool selection
        response = client.chat(
            model="qwen3-next:80b-cloud", # You can swap this to "gemma3:27b-cloud" or your preferred model
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
    
    # Instruct the LLM to format its findings
    messages.append({
        "role": "user",
        "content": "You have gathered the necessary information. Now, synthesize your final answer into the exact JSON schema required."
    })
    
    # We call the model again, this time forcing the Pydantic schema format
    synth_response = client.chat(
        model="qwen3-next:80b-cloud", 
        messages=messages,
        format=AgentOutput.model_json_schema()
    )
    
    raw_content = synth_response['message']['content'].strip()
    
    # Defensive parsing: Clean markdown code blocks if the model wrapped the JSON
    if raw_content.startswith("```json"):
        raw_content = raw_content[7:-3].strip()
    elif raw_content.startswith("```"):
        raw_content = raw_content[3:-3].strip()
    
    # Validate and return the final Pydantic object
    try:
        parsed_json = json.loads(raw_content)
        return AgentOutput(**parsed_json)
    except json.JSONDecodeError as e:
        print(f"   [ERROR] Failed to parse final output: {e}")
        print(f"   [DEBUG RAW OUTPUT] {raw_content}")
        
        # Graceful fallback so the API doesn't crash entirely
        return AgentOutput(
            conversational_reply="I found the information, but an error occurred while formatting it for the dashboard.",
            documents_cited=[],
            suggested_contacts=[]
        )