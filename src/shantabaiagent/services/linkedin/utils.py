def format_post(content: str, hashtags: list[str]) -> str:
    """Format the post content with hashtags"""
    formatted_hashtags = " ".join([f"#{tag}" for tag in hashtags])
    return f"{content}\n\n{formatted_hashtags}"

def validate_post_length(content: str) -> bool:
    """Check if post meets LinkedIn's character limit"""
    return len(content) <= 3000

START_POST_SELECTORS = [
                "//span[contains(@class, 'truncate')]//strong[contains(text(), 'Start a post')]",
                "//span[contains(text(), 'Start a post')]",
                "//button[contains(@class, 'share-box-feed-entry__trigger')]",
                "//div[contains(@class, 'share-box-feed-entry__trigger')]"
            ]

POST_FIELD_SELECTORS = [
                "div.ql-editor[data-placeholder='What do you want to talk about?']",
                "div.share-creation-state__editor div[role='textbox']",
                "div.editor-content div[role='textbox']",
                "div[contenteditable='true']"
            ]
POST_BUTTON_SELECTORS = [
                "//button[contains(@class, 'share-actions__primary-action') and not(@disabled)]",
                "//button[contains(@class, 'share-actions__primary-action')]//span[text()='Post']/parent::button",
                "//div[contains(@class, 'share-box_actions')]//button[contains(@class, 'primary')]"
            ]
