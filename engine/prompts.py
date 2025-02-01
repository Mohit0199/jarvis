import re

def generate_prompt(query):
    """
    A function to automatically generate prompts based on the content of the query.
    The function attempts to classify the query type and generate the relevant prompt accordingly.
    """
    query = query.lower()

    # Heuristic classification of the query type
    if any(word in query for word in ["summarize", "summary", "brief", "shorten"]):
        return f"""
        You are an expert summarizer. Please summarize the following text in a concise manner, preserving the key details and ideas.
        
        Text to summarize: {query}
        """

    elif any(word in query for word in ["sentiment", "emotion", "feel", "opinion"]):
        return f"""
        You are a sentiment analysis expert. Please analyze the sentiment of the following text and categorize it as positive, negative, or neutral. Provide a brief explanation of the sentiment.

        Text: {query}
        """

    elif "coding" in query or any(word in query for word in ["python", "java", "html", "code", "debug", "program"]):
        return f"""
        You are a programming expert. Please provide detailed guidance or a solution to the following coding issue. Include relevant code snippets or explanations.
        
        Issue: {query}
        """

    elif "business" in query or any(word in query for word in ["startup", "entrepreneur", "market", "scalability", "business model"]):
        return f"""
        You are a business consultant. Evaluate the following business idea and provide insights about its potential, scalability, and any challenges. Suggest improvements if necessary.

        Business Idea: {query}
        """

    elif any(word in query for word in ["compare", "difference", "contrast", "vs"]):
        return f"""
        You are an expert at comparisons. Compare the following two items based on their features, advantages, and drawbacks.

        Item 1: {query}
        """

    elif any(word in query for word in ["career", "job", "resume", "interview", "skills"]):
        return f"""
        You are a career advisor. Offer detailed advice on the following query related to career development, job search, or professional growth.

        Career Query: {query}
        """

    elif any(word in query for word in ["health", "wellness", "fitness", "exercise", "nutrition"]):
        return f"""
        You are a health expert. Provide practical tips for improving health, fitness, or wellness. Make sure to include actionable advice that can be followed easily.

        Health Query: {query}
        """

    elif any(word in query for word in ["recipe", "cook", "meal", "ingredient"]):
        return f"""
        You are a chef. Suggest some recipes based on the following ingredient or type of meal. Provide clear, easy-to-follow instructions and be creative with your suggestions.

        Ingredient: {query}
        """

    elif any(word in query for word in ["travel", "destination", "vacation", "trip", "tour"]):
        return f"""
        You are a travel expert. Suggest a travel itinerary or destination based on the following query. Provide tips, activities, and recommendations for the traveler.

        Location: {query}
        """

    elif any(word in query for word in ["troubleshoot", "fix", "problem", "solution", "error"]):
        return f"""
        You are a troubleshooting assistant. Provide a step-by-step solution for the following problem, including possible causes and resolutions.

        Issue: {query}
        """

    elif any(word in query for word in ["explain", "define", "meaning", "concept", "understand"]):
        return f"""
        You are an educator. Break down the following concept or term in simple, easy-to-understand language. Avoid jargon and make it clear for beginners.

        Concept: {query}
        """

    elif "data science" in query or any(word in query for word in ["statistics", "machine learning", "algorithm", "AI", "data"]):
        return f"""
        You are a data science expert. Provide an in-depth explanation of the following data science concept, including examples and key insights.

        Query: {query}
        """

    elif any(word in query for word in ["creative", "story", "poem", "narrative", "imagine"]):
        return f"""
        You are a creative writer. Create a captivating story or narrative based on the following input. Use vivid language and creativity to engage the reader.

        Input: {query}
        """

    # Default: If the query doesn't match any of the above, return a general query prompt
    else:
        return f"""
        You are a helpful assistant. Respond to the following query clearly and concisely, providing useful information and insights.
        
        Query: {query}
        """

def clean_response(response):
    """
    This function cleans the chatbot's response by removing unwanted characters
    like special symbols, hashtags, asterisks, and other markdown-related symbols.
    """
    # Remove non-alphanumeric characters, asterisks, hashtags, and markdown symbols
    cleaned = re.sub(r"[^\w\s,.,-]", "", str(response))  # Keeps letters, numbers, spaces, commas, periods, and hyphens
    cleaned = cleaned.replace("#", "")  # Remove hashtags
    cleaned = cleaned.replace("*", "")  # Remove asterisks
    cleaned = cleaned.replace("\n", " ")  # Remove newlines for a cleaner output
    cleaned = cleaned.strip()  # Trim any leading/trailing spaces
    return cleaned
