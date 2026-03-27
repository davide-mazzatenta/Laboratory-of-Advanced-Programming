#!/usr/bin/env python3
"""
Unit Test for Generation Agent with Gemini
Simulates orchestrator request through API Gateway
"""

import requests
import json
import sys
import time
from typing import List, Optional

class GenerationAgentTester:
    def __init__(self, generation_agent_url: str = "http://localhost:8003"):
        self.generation_agent_url = generation_agent_url
        self.generation_endpoint = f"{generation_agent_url}/api/v1/agents/generate"
        self.process_endpoint = f"{generation_agent_url}/api/v1/agents/process"
        self.health_endpoint = f"{generation_agent_url}/health"

    def check_health(self) -> bool:
        """Check if generation agent is healthy"""
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health Check: {health_data}")
                return health_data.get("service_ready", False)
            else:
                print(f"❌ Health check failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False

    def test_generation_endpoint(self, document_id: str, query: str, full_doc: bool = False, execution_id: Optional[str] = None) -> Optional[dict]:
        """Test the main generation endpoint"""
        print(f"\n🧪 Testing generation endpoint")
        print(f"📄 Document ID: {document_id}")
        print(f"📋 Query: {query}")
        print(f"🔄 Full Doc: {full_doc}")
        
        payload = {
            "document_id": document_id,
            "query": query,
            "full_doc": full_doc,
            "agent_id": "generation-agent"
        }
        
        if execution_id:
            payload["execution_id"] = execution_id

        try:
            response = requests.post(
                self.generation_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # Longer timeout for generation
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Generation successful!")
                print(f"Source Mode: {result['source_mode']}")
                print(f"Chunks Used: {result['chunks_used']}")
                print(f"Message: {result['message']}")
                print(f"\n🤖 Generated Content:\n{'-'*50}")
                print(result['generated_content'])
                print(f"{'-'*50}")
                
                return result
            else:
                print(f"❌ Generation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None

    def test_orchestrator_compatibility(self, document_ids: List[str], prompt: str, full_doc: bool = False, execution_id: Optional[str] = None) -> Optional[dict]:
        """Test the orchestrator compatibility endpoint"""
        print(f"\n🤖 Testing orchestrator compatibility endpoint")
        print(f"📄 Document IDs: {document_ids}")
        print(f"📋 Prompt: {prompt}")
        print(f"🔄 Full Doc: {full_doc}")
        
        payload = {
            "agentId": "generation-agent",
            "prompt": prompt,
            "documentIds": document_ids,
            "fullDoc": full_doc
        }
        
        if execution_id:
            payload["executionId"] = execution_id

        try:
            response = requests.post(
                self.process_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Orchestrator endpoint successful!")
                print(f"\n🤖 Agent Response:\n{'-'*50}")
                print(result['response'])
                print(f"{'-'*50}")
                
                # Print full result details if available
                if 'fullResult' in result:
                    full_result = result['fullResult']
                    print(f"Source Mode: {full_result['source_mode']}")
                    print(f"Chunks Used: {full_result['chunks_used']}")
                    print(f"Message: {full_result['message']}")
                
                return result
            else:
                print(f"❌ Orchestrator endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None

    def run_comprehensive_test(self, document_id: str, test_scenarios: List[dict] = None):
        """Run comprehensive tests with different scenarios"""
        print("🚀 Starting Generation Agent Tests (with Gemini)")
        print("=" * 60)
        
        # 1. Health check
        print("\n1. Health Check:")
        if not self.check_health():
            print("❌ Health check failed. Stopping tests.")
            return False
        
        # Wait for service readiness
        print("⏳ Waiting 2 seconds for service readiness...")
        time.sleep(2)
        
        if not test_scenarios:
            test_scenarios = [
                {
                    "name": "Query-based Generation",
                    "query": "Summarize the main points of this document",
                    "full_doc": False
                },
                {
                    "name": "Question Answering",
                    "query": "What are the key people and organizations mentioned?",
                    "full_doc": False
                },
                {
                    "name": "Full Document Analysis",
                    "query": "Provide a comprehensive analysis of this document including main themes, important details, and conclusions",
                    "full_doc": True
                },
                {
                    "name": "Specific Information Extraction",
                    "query": "Extract any dates, numbers, and important facts from this document",
                    "full_doc": False
                }
            ]
        
        results = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n{'='*20} TEST {i+1}: {scenario['name']} {'='*20}")
            
            # Test main generation endpoint
            print(f"\n2.{i+1}. Main Generation Endpoint:")
            generation_result = self.test_generation_endpoint(
                document_id, 
                scenario["query"], 
                scenario["full_doc"],
                f"test-generation-{i+1:03d}"
            )
            
            # Test orchestrator compatibility
            print(f"\n3.{i+1}. Orchestrator Compatibility Endpoint:")
            orchestrator_result = self.test_orchestrator_compatibility(
                [document_id], 
                scenario["query"], 
                scenario["full_doc"],
                f"test-orchestrator-{i+1:03d}"
            )
            
            results.append({
                'scenario': scenario['name'],
                'query': scenario['query'],
                'full_doc': scenario['full_doc'],
                'generation': generation_result,
                'orchestrator': orchestrator_result
            })
            
            # Brief pause between tests
            time.sleep(1)
        
        # Summary
        print(f"\n{'='*20} SUMMARY {'='*20}")
        successful_tests = 0
        for i, result in enumerate(results):
            generation_ok = result['generation'] is not None
            orchestrator_ok = result['orchestrator'] is not None
            
            print(f"Test {i+1} ({result['scenario']}): ", end="")
            if generation_ok and orchestrator_ok:
                print("✅ PASSED")
                successful_tests += 1
            else:
                print("❌ FAILED")
        
        print(f"\n🏁 Tests completed! {successful_tests}/{len(results)} passed")
        
        if successful_tests > 0:
            print("\n📊 Sample Generation Results:")
            for i, result in enumerate(results):
                if result['generation']:
                    print(f"\nTest {i+1} ({result['scenario']}):")
                    content = result['generation']['generated_content']
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(f"  🤖 Generated: {preview}")
        
        return successful_tests == len(results)

def main():
    """Main test function"""
    
    # Example document ID (replace with actual ID from your system)
    test_document_id = "2e6263a5-4238-488d-bdfe-77839ad24a67_provaprog1_16b79616-cf98-4628-a1af-d5ad84a8f9fd"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        generation_agent_url = sys.argv[1]
    else:
        generation_agent_url = "http://localhost:8003"

    print(f"🎯 Target Generation Agent: {generation_agent_url}")

    tester = GenerationAgentTester(generation_agent_url)
    
    if len(sys.argv) > 2:
        # Document ID from command line
        test_document_id = sys.argv[2]
    
    custom_scenarios = None
    if len(sys.argv) > 3:
        # Custom test scenarios from command line
        scenarios_str = sys.argv[3]
        custom_scenarios = []
        for scenario_str in scenarios_str.split('|'):
            parts = scenario_str.split(':')
            if len(parts) >= 2:
                custom_scenarios.append({
                    "name": parts[0],
                    "query": parts[1],
                    "full_doc": parts[2].lower() == 'true' if len(parts) > 2 else False
                })
    
    print(f"📄 Test Document ID: {test_document_id}")
    
    # Check if document exists first
    print("\n🔍 Checking if test document exists...")
    document_exists = False
    try:
        parts = test_document_id.split('_')
        if len(parts) == 3:
            user_id, project_id, doc_id_part = parts
            check_url = f"http://localhost:8000/api/v1/documents/{user_id}/{project_id}/{doc_id_part}/text"
            response = requests.get(check_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Document {test_document_id} exists and accessible")
                document_exists = True
            else:
                print(f"❌ Document {test_document_id} not found: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking document {test_document_id}: {str(e)}")
    
    if not document_exists:
        print("\n⚠️  Test document not found!")
        print("To test with real documents:")
        print("1. Upload a document first via the document service")
        print("2. Use the returned document ID in format: userId_projectId_docId")
        print("3. Run: python test_generation_agent.py http://localhost:8080 'real_user_real_project_real_doc'")
        print("\n🧪 Proceeding with tests anyway (will show expected errors)...")
    
    # Run tests
    success = tester.run_comprehensive_test(test_document_id, custom_scenarios)
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        if not document_exists:
            print("ℹ️  This is expected since test document doesn't exist")
        sys.exit(1)

if __name__ == "__main__":
    main()