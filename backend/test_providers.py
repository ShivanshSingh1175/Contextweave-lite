"""
Test script to verify LLM providers are working correctly
"""
import asyncio
import os
from llm.provider_factory import get_llm_provider, get_available_providers


async def test_provider(provider_name: str):
    """Test a specific provider"""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()} Provider")
    print(f"{'='*60}")
    
    try:
        # Get provider
        provider = get_llm_provider(provider_name)
        print(f"✓ Provider initialized: {provider.get_provider_name()}")
        
        # Check availability
        is_available = provider.is_available()
        print(f"{'✓' if is_available else '✗'} Provider available: {is_available}")
        
        if not is_available:
            if provider_name == "groq":
                print("  → Set LLM_API_KEY environment variable")
            elif provider_name == "ollama":
                print("  → Start Ollama: ollama serve")
                print("  → Pull model: ollama pull llama3")
            elif provider_name == "localai":
                print("  → Start LocalAI: docker run -p 8080:8080 localai/localai")
            return False
        
        # Test generation with minimal data
        print("\nTesting generation...")
        test_commits = [
            {
                'hash': 'abc123',
                'author': 'Test User',
                'date': '2026-02-10',
                'message': 'Initial commit',
                'lines_changed': 10
            }
        ]
        
        test_related = {
            'imports': ['module1.py', 'module2.py'],
            'co_changed': []
        }
        
        result = await provider.generate(
            file_path="test.py",
            file_content="def hello():\n    print('Hello, World!')",
            commits=test_commits,
            related_files_data=test_related,
            selected_code=None
        )
        
        print(f"✓ Generation successful")
        print(f"  Summary: {result.summary[:100]}...")
        print(f"  Decisions: {len(result.decisions)}")
        print(f"  Related files: {len(result.related_files)}")
        print(f"  Metadata: {result.metadata}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Main test function"""
    print("ContextWeave LLM Provider Test")
    print("="*60)
    
    # Check available providers
    print("\nChecking provider availability...")
    available = get_available_providers()
    for name, status in available.items():
        print(f"  {name}: {'✓ Available' if status else '✗ Not available'}")
    
    # Test each provider
    results = {}
    
    # Test Groq
    results['groq'] = await test_provider('groq')
    
    # Test Ollama
    results['ollama'] = await test_provider('ollama')
    
    # Test LocalAI
    results['localai'] = await test_provider('localai')
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    for provider, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {provider}: {status}")
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print(f"{'='*60}")
    
    if not any(results.values()):
        print("No providers are working. Please:")
        print("  1. For Groq: Set LLM_API_KEY in .env file")
        print("  2. For Ollama: Run 'ollama serve' and 'ollama pull llama3'")
        print("  3. For LocalAI: Run 'docker run -p 8080:8080 localai/localai'")
    elif results['groq']:
        print("✓ Groq is working! You can use cloud AI.")
    elif results['ollama']:
        print("✓ Ollama is working! You can use local AI (privacy-first).")
    elif results['localai']:
        print("✓ LocalAI is working! You can use local AI (privacy-first).")
    
    print("\nTo use a specific provider:")
    print("  1. Set LLM_PROVIDER=groq|ollama|localai in .env")
    print("  2. Or configure in VS Code settings")
    print("  3. Start backend: python main.py")


if __name__ == "__main__":
    asyncio.run(main())
