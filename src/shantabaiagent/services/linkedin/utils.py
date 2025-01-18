def format_post(content: str, hashtags: list[str]) -> str:
    """Format the post content with hashtags"""
    formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
    return f"{content}\n\n{formatted_hashtags}"

def validate_post_length(content: str) -> bool:
    """Check if post meets LinkedIn's character limit"""
    return len(content) <= 3000

START_POST_SELECTORS = [
    "//button[contains(@class, 'artdeco-button--tertiary')]//span[@class='artdeco-button__text']//span[@class='truncate']//span[@class='t-normal']//strong[contains(text(), 'Start a post')]",
    "//button[contains(@class, 'artdeco-button--tertiary')]//strong[contains(text(), 'Start a post')]",
    "//button[contains(@class, 'artdeco-button')]//span[contains(text(), 'Start a post')]",
    "//button[contains(@class, 'artdeco-button--tertiary')]",
    "//div[contains(@class, 'share-box-feed-entry__trigger')]"
]

POST_FIELD_SELECTORS = [
    "//div[@role='textbox']",
    "//div[contains(@class, 'editor-content')]",
    "//div[contains(@class, 'ql-editor')]",
    "//div[contains(@data-placeholder, 'What do you want to talk about?')]"
]

POST_BUTTON_SELECTORS = [
    "//button[contains(@class, 'share-actions__primary-action')]//span[@class='artdeco-button__text'][text()='Post']",
    "//button[contains(@class, 'artdeco-button--primary')]//span[text()='Post']",
    "//button[contains(@class, 'share-actions__primary-action')]",
    "//span[text()='Post']/parent::button"
]
