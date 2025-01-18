from typing import Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PostInput(BaseModel):
    content: str = Field(description="The content to create a post about")
    style: Optional[str] = Field(
        description="Style of the post (professional, casual, technical)", 
        default="professional"
    )

class LinkedInPoster:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        # Add headless mode option for production
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        
    def login_to_linkedin(self, email: str, password: str):
        try:
            self.driver.get('https://www.linkedin.com/login')
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module"))
            )
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
            
    def create_post(self, content: str):
        """Create a new post on LinkedIn with improved element detection"""
        try:
            # Wait for the feed page to fully load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module"))
            )
            
            print("Feed loaded, looking for post button...")
            
            # Updated selectors to match the exact button structure
            start_post_selectors = [
                # Primary selector matching the exact structure
                "//button[contains(@class, 'artdeco-button--tertiary')]//span[@class='artdeco-button__text']//span[@class='truncate']//span[@class='t-normal']//strong[contains(text(), 'Start a post')]",
                # Broader selectors as fallbacks
                "//button[contains(@class, 'artdeco-button--tertiary')]//strong[contains(text(), 'Start a post')]",
                "//button[contains(@class, 'artdeco-button')]//span[contains(text(), 'Start a post')]",
                # Additional backup selectors
                "//button[contains(@class, 'artdeco-button--tertiary')]",
                "//div[contains(@class, 'share-box-feed-entry__trigger')]"
            ]
            
            start_post = None
            for selector in start_post_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    start_post = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"Found element with selector: {selector}")
                    break
                except Exception as e:
                    print(f"Selector failed: {selector} - {str(e)}")
                    continue
                    
            if not start_post:
                raise Exception("Could not find start post button")
                
            print("Found start post button, attempting to click...")
            
            # Try multiple click methods
            try:
                # Method 1: Direct click
                start_post.click()
            except:
                try:
                    # Method 2: JavaScript click
                    self.driver.execute_script("arguments[0].click();", start_post)
                except:
                    try:
                        # Method 3: Action chains
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(start_post).click().perform()
                    except Exception as e:
                        print(f"All click methods failed: {str(e)}")
                        raise
            
            time.sleep(3)
            print("Clicked start post, looking for input field...")
            
            post_field_selectors = [
                "//div[@role='textbox']",
                "//div[contains(@class, 'editor-content')]",
                "//div[contains(@class, 'ql-editor')]",
                "//div[contains(@data-placeholder, 'What do you want to talk about?')]"
            ]
            
            post_field = None
            for selector in post_field_selectors:
                try:
                    post_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"Found post field with selector: {selector}")
                    break
                except:
                    continue
                    
            if not post_field:
                raise Exception("Could not find post input field")
                
            # Enter content
            self.driver.execute_script(
                'arguments[0].innerHTML = arguments[1];',
                post_field,
                content
            )
            time.sleep(2)
            
            post_button_selectors = [
                "//button[contains(@class, 'share-actions__primary-action')]//span[@class='artdeco-button__text'][text()='Post']",
                "//button[contains(@class, 'artdeco-button--primary')]//span[text()='Post']",
                "//button[contains(@class, 'share-actions__primary-action')]",
                "//span[text()='Post']/parent::button"
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"Found post button with selector: {selector}")
                    break
                except:
                    continue
                    
            if not post_button:
                raise Exception("Could not find post button")
                
            # Try to click the post button
            try:
                post_button.click()
            except:
                self.driver.execute_script("arguments[0].click();", post_button)
                
            time.sleep(3)
            
            return True
        except Exception as e:
            print(f"Failed to create post: {str(e)}")
            return False
            
    def close(self):
        if self.driver:
            self.driver.quit()

@tool(args_schema=PostInput)
def create_linkedin_post(content: str, style: str = "professional") -> str:
    """Creates a LinkedIn post with proper formatting and hashtags."""
    prompt = f"""Create a {style} LinkedIn post about:
    {content}
    
    Include:
    - Engaging opening line with relevant emoji
    - 3 key points using these exact bullet points:
      • (for first point)
      ◆ (for second point)
      → (for third point)
    - Brief call to action
    - 3-5 relevant hashtags
    
    Use simple, widely-supported emojis like: 
    🚀 💡 🌟 ⚡ 🔍 💪 🎯 🌐 ⭐ 🔧
    
    Keep it concise and impactful, ensuring all emojis are properly encoded."""
    
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        model_name="mixtral-8x7b-32768"
    )
    response = llm.invoke(prompt)
    return response.content

@tool
def get_feedback() -> str:
    """Gets user feedback on the post."""
    feedback = input("\nWhat do you think about this post? Share your thoughts: ")
    return feedback.strip()

@tool
def analyze_feedback(feedback: str) -> Dict:
    """Analyzes user feedback to determine sentiment and next action."""
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
        model_name="mixtral-8x7b-32768"
    )
    
    prompt = f"""Analyze this feedback for a LinkedIn post and determine the next action:
    
    Feedback: "{feedback}"
    
    Classify the feedback as one of:
    1. POSITIVE - User likes the post (proceed to posting)
    2. SUGGESTIONS - User wants changes (needs revision)
    3. NEGATIVE - User dislikes post (needs major revision)
    4. QUIT - User wants to stop
    
    Return your analysis as JSON with these fields:
    - sentiment: The classification above
    - reasoning: Brief explanation of your classification
    - action: "post", "revise", or "quit"
    """
    
    response = llm.invoke(prompt)
    # Convert response to dict - in real implementation you'd want to parse this more robustly
    import json
    try:
        return json.loads(response.content)
    except:
        return {
            "sentiment": "SUGGESTIONS",
            "reasoning": "Failed to parse feedback properly",
            "action": "revise"
        }

@tool
def regenerate_post(original_post: str, feedback: str) -> str:
    """Regenerates the post based on feedback."""
    prompt = f"""Improve this LinkedIn post based on the feedback:
    
    Original post:
    {original_post}
    
    Feedback:
    {feedback}
    
    Provide an improved version that addresses the feedback while maintaining professionalism and impact."""
    
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        model_name="mixtral-8x7b-32768"
    )
    response = llm.invoke(prompt)
    return response.content

@tool
def post_to_linkedin(post: str) -> bool:
    """Post content to LinkedIn using Selenium"""
    poster = LinkedInPoster()
    try:
        poster.setup_driver()
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        
        if not email or not password:
            raise ValueError("LinkedIn credentials not found in environment variables")
        
        if not poster.login_to_linkedin(email, password):
            raise Exception("Failed to login to LinkedIn")
        
        if not poster.create_post(post):
            raise Exception("Failed to create post")
            
        return True
    except Exception as e:
        print(f"Error posting to LinkedIn: {str(e)}")
        return False
    finally:
        poster.close()

def setup_agent():
    """Set up the LinkedIn post creation agent."""
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        model_name="mixtral-8x7b-32768"
    )

    tools = [create_linkedin_post, get_feedback, analyze_feedback, regenerate_post, post_to_linkedin]
    
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

def main():
    print("\n=== LinkedIn Post Creator ===")
    
    try:
        agent = setup_agent()
        
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
                    if "agent" in chunk:
                        messages = chunk["agent"].get("messages", [])
                        for msg in messages:
                            # Skip if this is just echoing the generated post
                            if isinstance(msg.content, str) and msg.content.strip():
                                if not current_post or msg.content != current_post:
                                    print(f"\n🤖 Agent: {msg.content}")
                            elif isinstance(msg.content, list):
                                for content_item in msg.content:
                                    if isinstance(content_item, dict):
                                        if content_item.get("type") == "text":
                                            print(f"\n💭 Thinking: {content_item['text']}")
                                        elif content_item.get("type") == "tool_use":
                                            print(f"\n🔧 Using tool: {content_item['name']}")
                    
                    elif "tools" in chunk:
                        messages = chunk["tools"].get("messages", [])
                        for msg in messages:
                            if hasattr(msg, "content") and msg.content.strip():
                                if not current_post:  # Only print if this is the first time
                                    print(f"\n📝 Generated post:")
                                    print(f"{msg.content}")
                                    current_post = msg.content
                                    print("\n--- End of Generation ---")
                
                # Feedback loop
                while current_post and not post_approved:
                    print("\n✍️ Please review the post above.")
                    feedback_tool = get_feedback
                    feedback = feedback_tool.invoke({})
                    print(f"\n📣 Your feedback: {feedback}")
                    
                    # Analyze feedback
                    analysis = analyze_feedback.invoke({"feedback": feedback})
                    print(f"\n🔍 Analysis: {analysis}")
                    
                    # Take action based on analysis
                    if analysis.get("action") == "post":
                        print("\n📤 Preparing to post to LinkedIn...")
                        confirm = input("Are you sure you want to post this? (y/n): ").lower()
                        if confirm == 'y':
                            success = post_to_linkedin.invoke({"post": current_post})
                            if success:
                                print("✅ Posted successfully!")
                                post_approved = True
                            else:
                                print("❌ Failed to post.")
                        else:
                            print("🔄 Continuing revision...")
                            
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
            
            if input("\nCreate another post? (y/n): ").lower() != 'y':
                break
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()