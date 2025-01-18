from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from shantabaiagent.services.llm.tools import (
    create_linkedin_post, 
    get_feedback, 
    analyze_feedback, 
    regenerate_post, 
    post_to_linkedin
)
from shantabaiagent.config.settings import GROQ_API_KEY

def setup_agent():
    """Set up the LinkedIn post creation agent."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        temperature=0.7,
        model_name="mixtral-8x7b-32768"
    )

    tools = [
        create_linkedin_post, 
        get_feedback, 
        analyze_feedback, 
        regenerate_post, 
        post_to_linkedin
    ]
    
    system_message = """You are a LinkedIn post creation expert. Your goal is to help create engaging posts.
    
    Follow these steps:
    1. First, create a post using create_linkedin_post
    2. Get user feedback using get_feedback
    3. Analyze the feedback using analyze_feedback
    4. Based on the analysis:
       - If POSITIVE: Use post_to_linkedin
       - If SUGGESTIONS/NEGATIVE: Use regenerate_post and return to step 2
       - If QUIT: End the conversation
    
    Always explain what you're doing before taking any action."""
    
    return create_react_agent(llm, tools)
