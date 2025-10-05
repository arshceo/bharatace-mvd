"""
Test script for BharatAce API
Demonstrates how to interact with the FastAPI endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check Endpoint")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"\nDetailed Health Check:")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_add_knowledge():
    """Test adding knowledge to the database"""
    print("\n" + "="*50)
    print("Testing Add Knowledge Endpoint")
    print("="*50)
    
    knowledge_items = [
        {
            "content": "BharatAce University offers undergraduate programs in Computer Science, Electronics, and Mechanical Engineering.",
            "category": "courses"
        },
        {
            "content": "The university library is open from 8 AM to 10 PM on weekdays and 9 AM to 6 PM on weekends.",
            "category": "facilities"
        },
        {
            "content": "Admission process requires 12th-grade marks, entrance exam scores, and a personal interview.",
            "category": "admission"
        }
    ]
    
    for item in knowledge_items:
        response = requests.post(f"{BASE_URL}/knowledge", json=item)
        print(f"\nAdding: {item['content'][:50]}...")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            print(f"✓ Successfully added!")
        else:
            print(f"✗ Error: {response.text}")


def test_get_knowledge():
    """Test retrieving all knowledge"""
    print("\n" + "="*50)
    print("Testing Get All Knowledge Endpoint")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/knowledge")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal knowledge items: {len(data)}")
        for idx, item in enumerate(data, 1):
            print(f"\n{idx}. Category: {item['category']}")
            print(f"   Content: {item['content'][:80]}...")


def test_ask_questions():
    """Test the chatbot endpoint"""
    print("\n" + "="*50)
    print("Testing Chatbot Ask Endpoint")
    print("="*50)
    
    questions = [
        "What programs does the university offer?",
        "What are the library timings?",
        "How can I get admission to the university?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"query": question}
        )
        
        if response.status_code == 200:
            answer = response.json()["response"]
            print(f"Answer: {answer}")
        else:
            print(f"Error: {response.text}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("BharatAce API Test Suite")
    print("="*50)
    print("\nMake sure the FastAPI server is running on http://localhost:8000")
    input("\nPress Enter to continue...")
    
    try:
        # Test 1: Health Check
        test_health_check()
        
        # Test 2: Add Knowledge
        test_add_knowledge()
        
        input("\nPress Enter to continue to get all knowledge...")
        
        # Test 3: Get All Knowledge
        test_get_knowledge()
        
        input("\nPress Enter to continue to ask questions...")
        
        # Test 4: Ask Questions
        test_ask_questions()
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
