"""
Test script for DuckDuckGo Search using duckduckgo-search package
"""

from core.keyword_search import KeywordSearcher

def test_search():
    """Test web search with different max_results values"""

    searcher = KeywordSearcher()

    # Test cases
    test_queries = [
        ("tourism Bangladesh", 10),
        ("travel news", 15),
        ("Cox Bazar", 20),
        ("Bangladesh tourism", 30)
    ]

    print("=" * 80)
    print("Testing DuckDuckGo Search with duckduckgo-search package")
    print("=" * 80)

    for query, max_results in test_queries:
        print(f"\n\nQuery: '{query}' | Max Results: {max_results}")
        print("-" * 80)

        try:
            articles = searcher.search_web(keyword=query, max_results=max_results)

            print(f"Found {len(articles)} articles")

            # Show first 3 results
            for idx, article in enumerate(articles[:3], 1):
                print(f"\n{idx}. {article['headline'][:80]}...")
                print(f"   Source: {article['source']} | Language: {article['language']}")
                print(f"   URL: {article['url'][:80]}...")
                print(f"   Snippet: {article['snippet'][:100]}...")

            if len(articles) > 3:
                print(f"\n   ... and {len(articles) - 3} more results")

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)


if __name__ == '__main__':
    test_search()
