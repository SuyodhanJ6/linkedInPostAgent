from typing import Dict, List
from dataclasses import dataclass
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from shantabaiagent.models.schemas import PostInput
from shantabaiagent.services.linkedin.poster import LinkedInPoster
from shantabaiagent.config.settings import GROQ_API_KEY, LINKEDIN_EMAIL, LINKEDIN_PASSWORD, MODEL_NAME, TEMPERATURE, TAVILY_API_KEY
import json
from datetime import datetime



@dataclass
class ResearchResult:
    title: str
    url: str
    content: str
    date: str

class ResearchCache:
    _instance = None
    
    def __init__(self):
        self.results: List[ResearchResult] = []
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ResearchCache()
        return cls._instance
    
    def update_results(self, results: List[ResearchResult]):
        self.results = results
    
    def get_results(self) -> List[ResearchResult]:
        return self.results

@tool
def research_topic(topic: str) -> str:
    """Research current information about a topic using Tavily."""
    try:
        print("\n🔍 Starting research using Tavily...")
        
        # Initialize Tavily through LangChain
        search = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY)
        
        # Get current year for context
        current_year = datetime.now().year
        search_query = f"latest news and developments about {topic} {current_year}"
        print(f"\n📊 Searching for: {search_query}")
        
        # Perform the search
        search_results = search.results(
            search_query,
            search_depth="advanced",
            max_results=2
        )
        
        print(f"\n📚 Found {len(search_results)} relevant articles")
        
        # Extract and format the results
        research_results = []
        for i, result in enumerate(search_results, 1):
            research_result = ResearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", "")[:200] + "...",
                date=result.get("published_date", "")
            )
            research_results.append(research_result)
            print(f"\n📰 Article {i}:")
            print(f"Title: {research_result.title}")
            print(f"Date: {research_result.date}")
            print(f"URL: {research_result.url}")
        
        # Store results in cache
        ResearchCache.get_instance().update_results(research_results)
        
        print("\n🤖 Summarizing research findings...")
        
        # Use LLM to summarize the research
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            temperature=0.3,
            model_name=MODEL_NAME
        )
        
        research_prompt = f"""Based on these recent search results about {topic}, create a concise summary of the latest developments and key points:

        Search Results:
        {json.dumps([{
            "title": result.title,
            "content": result.content,
            "url": result.url,
            "published_date": result.date
        } for result in research_results], indent=2)}

        Please provide:
        1. 2-3 key recent developments
        2. Important statistics or numbers (if any)
        3. Any significant trends or future predictions
        
        Format the response in a way that can be easily incorporated into a LinkedIn post.
        """
        
        summary = llm.invoke(research_prompt)
        print("\n📋 Research Summary:")
        print(summary.content)
        return summary.content
        
    except Exception as e:
        error_msg = f"Error performing research: {str(e)}"
        print(f"\n❌ {error_msg}")
        return error_msg

@tool(args_schema=PostInput)
def create_linkedin_post(content: str, style: str = "professional") -> str:
    """Creates a LinkedIn post with proper formatting and hashtags."""
    # First, research current information if needed
    current_info = ""
    if any(keyword in content.lower() for keyword in ["current", "latest", "recent", "news", "trend"]):
        print("\n🔍 Detected request for current information. Starting research...")
        try:
            current_info = research_topic(content)
            print("\n✅ Research completed successfully")
        except Exception as e:
            print(f"\n❌ Research error: {str(e)}")
    
    print("\n📝 Generating LinkedIn post...")
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        temperature=TEMPERATURE,
        model_name=MODEL_NAME
    )
    
    prompt = f"""Create a {style} LinkedIn post about: {content}
    
    {f'Here is some recent information to include: {current_info}' if current_info else ''}
    
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
        api_key=GROQ_API_KEY,
        temperature=0.3,
        model_name=MODEL_NAME
    )
    
    prompt = f"""Analyze this feedback for a LinkedIn post and determine the next action:
    
    Feedback: "{feedback}"
    
    Classify the feedback as one of:
    1. POSITIVE - User wants to post (examples: "post it", "looks good", "share it", "go ahead")
    2. SUGGESTIONS - User wants changes (needs revision)
    3. NEGATIVE - User dislikes post (needs major revision)
    4. QUIT - User wants to stop
    
    Return your analysis as JSON with these fields:
    - sentiment: The classification above
    - reasoning: Brief explanation of your classification
    - action: "post", "revise", or "quit"
    
    If the user indicates any intention to post (like "post it", "share it", "looks good", etc),
    classify it as POSITIVE with action "post".
    """
    
    response = llm.invoke(prompt)
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
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        temperature=TEMPERATURE,
        model_name=MODEL_NAME
    )
    
    if "article" in feedback.lower() or "link" in feedback.lower():
        # Get cached research results
        research_results = ResearchCache.get_instance().get_results()
        
        # Format article sources dynamically
        article_sources = "\n".join([
            f"{i+1}. {result.url} - {result.title}"
            for i, result in enumerate(research_results)
        ])
        
        prompt = f"""Improve this LinkedIn post by adding relevant article links:

        Original post:
        {original_post}
        
        Recent article sources:
        {article_sources}
        
        Create an improved version that:
        1. Maintains the original structure and key points
        2. Adds 2-3 most relevant article links after related points
        3. Uses this format for links: "🔗 Learn more: [link]"
        4. Keeps the engaging style and emojis
        5. Maintains these bullet points:
           • (for first point)
           ◆ (for second point)
           → (for third point)
        
        Keep it professional and impactful while ensuring readability.
        Add only the most relevant links - not every link needs to be used."""
    else:
        prompt = f"""Improve this LinkedIn post based on the feedback:
        
        Original post:
        {original_post}
        
        Feedback:
        {feedback}
        
        Provide an improved version that addresses the feedback while maintaining:
        - Engaging opening line with relevant emoji
        - 3 key points using these exact bullet points:
          • (for first point)
          ◆ (for second point)
          → (for third point)
        - Brief call to action
        - 3-5 relevant hashtags
        
        Keep the style professional and impactful."""
    
    response = llm.invoke(prompt)
    return response.content

@tool
def post_to_linkedin(post: str) -> bool:
    """Post content to LinkedIn using Selenium"""
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        raise ValueError("LinkedIn credentials not found in environment variables")
    
    poster = LinkedInPoster()
    try:
        poster.setup_driver()
        
        if not poster.login_to_linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
            raise Exception("Failed to login to LinkedIn")
        
        if not poster.create_post(post):
            raise Exception("Failed to create post")
            
        return True
        
    except Exception as e:
        print(f"Error posting to LinkedIn: {str(e)}")
        return False
        
    finally:
        poster.close()

def get_all_tools():
    """Returns all available tools."""
    return [
        create_linkedin_post,
        get_feedback,
        analyze_feedback,
        regenerate_post,
        post_to_linkedin,
        research_topic
    ]
