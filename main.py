from src.shantabaiagent.services.llm.agent import setup_agent
from src.shantabaiagent.services.llm.tools import get_feedback, analyze_feedback, regenerate_post, post_to_linkedin
from langchain_core.messages import HumanMessage, AIMessage
import json

def serialize_message(msg):
    """Helper function to serialize LangChain messages"""
    if isinstance(msg, (HumanMessage, AIMessage)):
        return {
            "type": msg.__class__.__name__,
            "content": msg.content
        }
    return str(msg)

def main():
    print("\n=== LinkedIn Post Creator ===")
    
    try:
        print("\n🔧 Setting up agent...")
        agent = setup_agent()
        print("✅ Agent setup complete")
        
        while True:
            topic = input("\nWhat would you like to post about? (or 'quit' to exit): ")
            
            if topic.lower() == 'quit':
                break
                
            print("\n=== Starting Post Creation ===")
            current_post = None
            post_approved = False
            
            try:
                # Initial post generation
                for chunk in agent.stream({
                    "messages": [HumanMessage(content=f"Create a LinkedIn post about: {topic}")]
                }):
                    if "tools" in chunk and not current_post:
                        messages = chunk["tools"].get("messages", [])
                        for msg in messages:
                            if hasattr(msg, "content") and msg.content.strip():
                                current_post = msg.content
                                print(f"\n📝 Generated Post:")
                                print(f"{current_post}")
                                print("\n--- End of Generation ---")
                                break
                
                # Feedback loop
                while current_post and not post_approved:
                    print("\n✍️ Please review the post above.")
                    
                    feedback = get_feedback.invoke({})
                    print(f"\n📣 Your feedback: {feedback}")
                    
                    analysis = analyze_feedback.invoke({"feedback": feedback})
                    print(f"\n🔍 Analysis: {json.dumps(analysis, indent=2)}")
                    
                    # Take action based on analysis
                    if analysis.get("action") == "post":
                        print("\n📤 Posting to LinkedIn...")
                        success = post_to_linkedin.invoke({"post": current_post})
                        if success:
                            print("\n✅ Posted successfully!")
                            post_approved = True
                        else:
                            print("\n❌ Failed to post.")
                            
                    elif analysis.get("action") == "revise":
                        print("\n🔄 Regenerating post based on feedback...")
                        current_post = regenerate_post.invoke({
                            "original_post": current_post,
                            "feedback": feedback
                        })
                        print(f"\n📝 Updated post:\n{current_post}")
                        
                    elif analysis.get("action") == "quit":
                        print("\n⚠️ Canceling post creation...")
                        break
                
            except Exception as e:
                print(f"\n❌ Error during post creation: {str(e)}")
                print(f"\nError details: {type(e).__name__}")
                import traceback
                traceback.print_exc()
            
            if input("\nCreate another post? (y/n): ").lower() != 'y':
                break
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()