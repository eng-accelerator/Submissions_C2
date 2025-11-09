"""Basic keyword extraction utilities."""
from collections import Counter
import re
from typing import List, Set

def extract_keywords(text: str, min_length: int = 4, max_length: int = 25) -> List[str]:
    """Extract candidate keywords from text.
    
    Args:
        text: Input text to analyze
        min_length: Minimum word length to consider
        max_length: Maximum phrase length to consider
        
    Returns:
        List of extracted keyword phrases sorted by frequency
    """
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out short words and common stopwords
    stopwords = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
                'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
                'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
                'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
                'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
                'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
                'just', 'him', 'know', 'take', 'into', 'year', 'your', 'some'}
    
    words = [w for w in words if len(w) >= min_length and w not in stopwords]
    
    # Get word frequencies
    freq = Counter(words)
    
    # Extract 2-3 word phrases
    phrases = []
    for i in range(len(words)-1):
        phrase2 = ' '.join(words[i:i+2])
        if len(phrase2) <= max_length:
            phrases.append(phrase2)
        if i < len(words)-2:
            phrase3 = ' '.join(words[i:i+3]) 
            if len(phrase3) <= max_length:
                phrases.append(phrase3)
                
    # Combine frequencies
    freq.update(Counter(phrases))
    
    # Return top keywords/phrases
    return [item for item, count in freq.most_common(20)]

def extract_topics(text: str, min_support: int = 2) -> Set[str]:
    """Extract topic phrases that appear multiple times."""
    # Find repeated phrases of 2-4 words
    words = text.lower().split()
    topics = set()
    
    for n in range(2, 5):  # Length of phrases to look for
        for i in range(len(words) - n):
            phrase = ' '.join(words[i:i+n])
            count = text.lower().count(phrase)
            if count >= min_support:
                topics.add(phrase)
                
    return topics