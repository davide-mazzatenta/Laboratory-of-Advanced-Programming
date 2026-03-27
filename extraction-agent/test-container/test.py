#!/usr/bin/env python3
"""
Unit Test for Extraction Agent with Gemini
Simulates orchestrator request through API Gateway
"""

import requests
import json
import sys
import time
from typing import List, Optional

class ExtractionAgentTester:
    def __init__(self, api_gateway_url: str = "http://localhost:8080"):
        self.api_gateway_url = api_gateway_url
        self.extraction_endpoint = f"{api_gateway_url}/api/v1/agents/extract"
        self.process_endpoint = f"{api_gateway_url}/api/v1/agents/process"
        self.health_endpoint = f"{api_gateway_url}/api/v1/agents/health"

    def check_health(self) -> bool:
        """Check if extraction agent is healthy"""
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health Check: {health_data}")
                return health_data.get("model_loaded", False)
            else:
                print(f"❌ Health check failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False

    def test_extraction_endpoint(self, document_ids: List[str], query: Optional[str] = None, execution_id: Optional[str] = None) -> Optional[dict]:
        """Test the main extraction endpoint"""
        print(f"\n🧪 Testing extraction endpoint with document IDs: {document_ids}")
        if query:
            print(f"📋 Query: {query}")
        
        payload = {
            "document_ids": document_ids,
            "agent_id": "extractor-agent"
        }
        
        if execution_id:
            payload["execution_id"] = execution_id
            
        if query:
            payload["query"] = query

        try:
            response = requests.post(
                self.extraction_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Extraction successful!")
                print(f"Raw extracted entities: {result['extracted_entities']}")
                
                if result.get('structured_summary'):
                    print(f"🤖 Gemini structured summary:\n{result['structured_summary']}")
                else:
                    print("ℹ️  No structured summary (no query provided or Gemini unavailable)")
                
                print(f"Message: {result['message']}")
                
                # Print detailed entities
                print("\n📋 Entities by category:")
                for entity_group in result.get('entities_by_label', []):
                    print(f"  {entity_group['label']}: {', '.join(entity_group['entities'])}")
                
                return result
            else:
                print(f"❌ Extraction failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None

    def test_orchestrator_compatibility(self, document_ids: List[str], query: Optional[str] = None, execution_id: Optional[str] = None) -> Optional[dict]:
        """Test the orchestrator compatibility endpoint"""
        print(f"\n🤖 Testing orchestrator compatibility endpoint with document IDs: {document_ids}")
        if query:
            print(f"📋 Query/Prompt: {query}")
        
        payload = {
            "agentId": "extractor-agent",
            "prompt": query if query else "Extract named entities from the provided documents",
            "documentIds": document_ids
        }
        
        if execution_id:
            payload["executionId"] = execution_id

        try:
            response = requests.post(
                self.process_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Orchestrator endpoint successful!")
                print(f"Agent Response: {result['response']}")
                
                # Print full result if available
                if 'fullResult' in result:
                    full_result = result['fullResult']
                    print(f"Message: {full_result['message']}")
                    if full_result.get('structured_summary'):
                        print(f"🤖 Has structured summary: Yes")
                    else:
                        print(f"ℹ️  Has structured summary: No")
                
                return result
            else:
                print(f"❌ Orchestrator endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None

    def run_comprehensive_test(self, document_ids: List[str], test_queries: List[str] = None):
        """Run comprehensive tests"""
        print("🚀 Starting Extraction Agent Tests (with Gemini)")
        print("=" * 50)
        
        # 1. Health check
        print("\n1. Health Check:")
        if not self.check_health():
            print("❌ Health check failed. Stopping tests.")
            return False
        
        # Wait a moment for model to be ready
        print("⏳ Waiting 2 seconds for model readiness...")
        time.sleep(2)
        
        if not test_queries:
            test_queries = [
                None,  # No query test
                "What are the main people mentioned in these documents?",
                "Find all organizations and locations in the text"
            ]
        
        results = []
        
        for i, query in enumerate(test_queries):
            print(f"\n{'='*20} TEST {i+1} {'='*20}")
            
            # 2. Test main extraction endpoint
            print(f"\n2.{i+1}. Main Extraction Endpoint:")
            extraction_result = self.test_extraction_endpoint(
                document_ids, 
                query, 
                f"test-extraction-{i+1:03d}"
            )
            
            # 3. Test orchestrator compatibility
            print(f"\n3.{i+1}. Orchestrator Compatibility Endpoint:")
            orchestrator_result = self.test_orchestrator_compatibility(
                document_ids, 
                query, 
                f"test-orchestrator-{i+1:03d}"
            )
            
            results.append({
                'query': query,
                'extraction': extraction_result,
                'orchestrator': orchestrator_result
            })
        
        # 4. Summary
        print(f"\n{'='*20} SUMMARY {'='*20}")
        successful_tests = 0
        for i, result in enumerate(results):
            query_desc = result['query'] if result['query'] else "No query"
            extraction_ok = result['extraction'] is not None
            orchestrator_ok = result['orchestrator'] is not None
            
            print(f"Test {i+1} ({query_desc}): ", end="")
            if extraction_ok and orchestrator_ok:
                print("✅ PASSED")
                successful_tests += 1
            else:
                print("❌ FAILED")
        
        print(f"\n🏁 Tests completed! {successful_tests}/{len(results)} passed")
        
        if successful_tests > 0:
            print("\n📊 Sample Results:")
            for i, result in enumerate(results):
                if result['extraction']:
                    query_desc = result['query'] if result['query'] else "No query"
                    print(f"\nTest {i+1} ({query_desc}):")
                    if result['extraction'].get('structured_summary'):
                        print(f"  🤖 Structured Summary: {result['extraction']['structured_summary'][:100]}...")
                    else:
                        print(f"  📝 Raw Entities: {result['extraction']['extracted_entities'][:100]}...")
        
        return successful_tests == len(results)

def main():
    """Main test function"""
    
    # Example document IDs (replace with actual IDs from your system)
    test_document_ids = [
        "2e6263a5-4238-488d-bdfe-77839ad24a67_provaprog1_16b79616-cf98-4628-a1af-d5ad84a8f9fd",  
        "2e6263a5-4238-488d-bdfe-77839ad24a67_provaprog1_5f4a9563-b76f-4782-869f-5c45fc710270"
    ]
    
    # Test queries for Gemini processing
    test_queries = [
        None,  # Test without query
        "What people are mentioned in these documents?",
        "List all organizations and their locations",
        "Extract key entities related to business or legal matters"
    ]
    
    # Check command line arguments
    if len(sys.argv) > 1:
        api_gateway_url = sys.argv[1]
    else:
        api_gateway_url = "http://localhost:8080"
    
    if len(sys.argv) > 2:
        # Document IDs from command line
        test_document_ids = sys.argv[2].split(',')
    
    if len(sys.argv) > 3:
        # Custom queries from command line
        test_queries = [None] + sys.argv[3].split('|')
    
    print(f"🎯 Target API Gateway: {api_gateway_url}")
    print(f"📄 Test Document IDs: {test_document_ids}")
    print(f"🔍 Test Queries: {[q if q else 'No query' for q in test_queries]}")
    
    # IMPORTANT: Check if documents exist first
    print("\n🔍 Checking if test documents exist...")
    document_exists = False
    for doc_id in test_document_ids:
        try:
            parts = doc_id.split('_')
            if len(parts) == 3:
                user_id, project_id, doc_id_part = parts
                check_url = f"{api_gateway_url}/api/v1/documents/{user_id}/{project_id}/{doc_id_part}/text"
                response = requests.get(check_url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Document {doc_id} exists and accessible")
                    document_exists = True
                else:
                    print(f"❌ Document {doc_id} not found: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking document {doc_id}: {str(e)}")
    
    if not document_exists:
        print("\n⚠️  No test documents found!")
        print("To test with real documents:")
        print("1. Upload a document first via the document service")
        print("2. Use the returned document ID in format: userId_projectId_docId")
        print("3. Run: python test_extraction_agent.py http://localhost:8080 'real_user_real_project_real_doc' 'query1|query2'")
        print("\n🧪 Proceeding with tests anyway (will show expected errors)...")
    
    # Run tests
    tester = ExtractionAgentTester(api_gateway_url)
    success = tester.run_comprehensive_test(test_document_ids, test_queries)
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        if not document_exists:
            print("ℹ️  This is expected since test documents don't exist")
        sys.exit(1)

if __name__ == "__main__":
    main()