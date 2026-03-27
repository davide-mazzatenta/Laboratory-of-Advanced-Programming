#!/usr/bin/env python3
"""
Unit Test for Orchestration Agent with Gemini
Tests the AI Legal Assistant coordination capabilities
"""

import requests
import json
import sys
import time
from typing import List, Optional

class OrchestrationAgentTester:
    def __init__(self, orchestration_agent_url: str = "http://localhost:8005"):
        self.orchestration_agent_url = orchestration_agent_url
        self.orchestration_endpoint = f"{orchestration_agent_url}/api/v1/agents/orchestrate"
        self.health_endpoint = f"{orchestration_agent_url}/health"

    def check_health(self) -> bool:
        """Check if orchestration agent is healthy"""
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

    def test_orchestration(self, document_ids: List[str], prompt: str, execution_id: Optional[str] = None) -> Optional[dict]:
        """Test the main orchestration endpoint"""
        print(f"\n🤖 Testing orchestration endpoint")
        print(f"📄 Document IDs: {document_ids}")
        print(f"📋 Prompt: {prompt}")
        
        payload = {
            "document_ids": document_ids,
            "prompt": prompt,
            "agent_id": "orchestration-agent"
        }
        
        if execution_id:
            payload["execution_id"] = execution_id

        try:
            print(f"⏳ Sending orchestration request...")
            response = requests.post(
                self.orchestration_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300  # Longer timeout for complex orchestration
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Orchestration successful!")
                print(f"Actions Taken: {len(result['actions_taken'])}")
                print(f"Message: {result['message']}")
                
                # Display actions taken
                if result['actions_taken']:
                    print(f"\n🔄 Agent Actions Executed:")
                    print("-" * 50)
                    for i, action in enumerate(result['actions_taken']):
                        action_info = action['action']
                        print(f"{i+1}. Turn {action['turn']}: {action_info['action_type'].upper()}")
                        print(f"   Query: {action_info['query']}")
                        if 'document_titles' in action_info:
                            print(f"   Documents: {action_info['document_titles']}")
                        if 'full_doc' in action_info:
                            print(f"   Full Doc: {action_info['full_doc']}")
                        result_preview = action['result'][:100] + "..." if len(action['result']) > 100 else action['result']
                        print(f"   Result: {result_preview}")
                        print()
                
                print(f"\n🤖 Final Legal Analysis:")
                print("-" * 50)
                print(result['final_response'])
                print("-" * 50)
                
                return result
            else:
                print(f"❌ Orchestration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None

    def test_service_dependencies(self) -> dict:
        """Test if dependent services are available"""
        print(f"\n🔍 Checking dependent services...")
        
        services = {
            "document-service": "http://localhost:8000/health",
            "extraction-agent": "http://localhost:8001/health", 
            "search-agent": "http://localhost:8002/health",
            "generation-agent": "http://localhost:8003/health"
        }
        
        status = {}
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service}: Available")
                    status[service] = "available"
                else:
                    print(f"⚠️ {service}: Unhealthy ({response.status_code})")
                    status[service] = f"unhealthy-{response.status_code}"
            except Exception as e:
                print(f"❌ {service}: Unavailable ({str(e)})")
                status[service] = "unavailable"
        
        return status

    def run_comprehensive_test(self, document_ids: List[str], test_scenarios: List[dict] = None):
        """Run comprehensive tests with different legal scenarios"""
        print("🚀 Starting Orchestration Agent Tests (Legal AI Assistant)")
        print("=" * 70)
        
        # 1. Health check
        print("\n1. Health Check:")
        if not self.check_health():
            print("❌ Health check failed. Stopping tests.")
            return False
        
        # 2. Check service dependencies
        print("\n2. Service Dependencies:")
        dependency_status = self.test_service_dependencies()
        available_services = sum(1 for status in dependency_status.values() if status == "available")
        
        if available_services < 2:
            print(f"⚠️ Only {available_services}/4 services available. Some features may not work.")
        
        # Wait for service readiness
        print("⏳ Waiting 3 seconds for service readiness...")
        time.sleep(3)
        
        if not test_scenarios:
            test_scenarios = [
                {
                    "name": "Contract Risk Analysis",
                    "prompt": "Analyze these contracts for potential legal risks, liability issues, and recommend mitigation strategies",
                    "expected_actions": ["search", "extract", "generate"]
                },
                {
                    "name": "Compliance Review", 
                    "prompt": "Review these documents for regulatory compliance issues and identify any violations or areas of concern",
                    "expected_actions": ["search", "extract"]
                },
                {
                    "name": "Due Diligence Summary",
                    "prompt": "Prepare a comprehensive due diligence summary highlighting key legal points, parties involved, and critical dates",
                    "expected_actions": ["extract", "generate"]
                },
                {
                    "name": "Legal Research Query",
                    "prompt": "What are the current legal precedents regarding data privacy in employment contracts? Reference relevant case law and regulations",
                    "expected_actions": ["search", "generate"]
                },
                {
                    "name": "Document Comparison",
                    "prompt": "Compare these legal documents and identify key differences, conflicting terms, and potential issues",
                    "expected_actions": ["extract", "generate"]
                }
            ]
        
        results = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n{'='*25} TEST {i+1}: {scenario['name']} {'='*25}")
            
            orchestration_result = self.test_orchestration(
                document_ids, 
                scenario["prompt"],
                f"test-orchestration-{i+1:03d}"
            )
            
            # Analyze results
            if orchestration_result:
                actions_taken = [action['action']['action_type'] for action in orchestration_result['actions_taken']]
                expected_actions = scenario.get('expected_actions', [])
                
                print(f"\n📊 Action Analysis:")
                print(f"   Expected: {expected_actions}")
                print(f"   Executed: {actions_taken}")
                
                # Check if at least some expected actions were taken
                actions_match = any(expected in actions_taken for expected in expected_actions)
                
                results.append({
                    'scenario': scenario['name'],
                    'prompt': scenario['prompt'],
                    'success': True,
                    'actions_taken': len(actions_taken),
                    'actions_match_expected': actions_match,
                    'final_response_length': len(orchestration_result['final_response']),
                    'result': orchestration_result
                })
            else:
                results.append({
                    'scenario': scenario['name'],
                    'prompt': scenario['prompt'], 
                    'success': False,
                    'actions_taken': 0,
                    'actions_match_expected': False,
                    'final_response_length': 0,
                    'result': None
                })
            
            # Brief pause between tests
            time.sleep(2)
        
        # Summary
        print(f"\n{'='*25} TEST SUMMARY {'='*25}")
        successful_tests = sum(1 for result in results if result['success'])
        
        print(f"\n📈 Overall Results:")
        print(f"   Tests Passed: {successful_tests}/{len(results)}")
        print(f"   Success Rate: {successful_tests/len(results)*100:.1f}%")
        
        print(f"\n📊 Detailed Results:")
        for i, result in enumerate(results):
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            print(f"{i+1}. {result['scenario']}: {status}")
            if result['success']:
                print(f"   Actions: {result['actions_taken']}")
                print(f"   Response Length: {result['final_response_length']} chars")
                print(f"   Expected Actions Match: {'Yes' if result['actions_match_expected'] else 'No'}")
        
        # Sample responses
        if successful_tests > 0:
            print(f"\n📝 Sample Legal Analysis (Test 1):")
            print("-" * 60)
            first_success = next((r for r in results if r['success']), None)
            if first_success and first_success['result']:
                response = first_success['result']['final_response']
                preview = response[:500] + "..." if len(response) > 500 else response
                print(preview)
            print("-" * 60)
        
        # Service dependency summary
        print(f"\n🔧 Service Dependencies:")
        for service, status in dependency_status.items():
            status_icon = "✅" if status == "available" else "❌"
            print(f"   {status_icon} {service}: {status}")
        
        return successful_tests == len(results)

def main():
    """Main test function"""
    
    # Example document IDs (replace with actual IDs from your system)
    test_document_ids = [
        "2e6263a5-4238-488d-bdfe-77839ad24a67_provaprog1_16b79616-cf98-4628-a1af-d5ad84a8f9fd"
    ]
    
    # Check command line arguments
    if len(sys.argv) > 1:
        orchestration_agent_url = sys.argv[1]
    else:
        orchestration_agent_url = "http://localhost:8005"

    print(f"🎯 Target Orchestration Agent: {orchestration_agent_url}")

    tester = OrchestrationAgentTester(orchestration_agent_url)
    
    if len(sys.argv) > 2:
        # Document IDs from command line
        document_ids_str = sys.argv[2]
        test_document_ids = document_ids_str.split(',')
    
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
                    "prompt": parts[1],
                    "expected_actions": parts[2].split(',') if len(parts) > 2 else []
                })
    
    print(f"📄 Test Document IDs: {test_document_ids}")
    
    # Check if documents exist
    print("\n🔍 Checking if test documents exist...")
    valid_documents = []
    for doc_id in test_document_ids:
        try:
            parts = doc_id.split('_')
            if len(parts) >= 3:
                user_id, project_id, doc_id_part = parts[0], '_'.join(parts[1:-1]), parts[-1]
                check_url = f"http://localhost:8000/api/v1/documents/{user_id}/{project_id}/{doc_id_part}/text"
                response = requests.get(check_url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Document {doc_id} exists and accessible")
                    valid_documents.append(doc_id)
                else:
                    print(f"❌ Document {doc_id} not found: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking document {doc_id}: {str(e)}")
    
    if not valid_documents:
        print("\n⚠️ No valid test documents found!")
        print("To test with real documents:")
        print("1. Upload documents via the document service")
        print("2. Use format: userId_projectId_docId")
        print("3. Run: python test.py http://localhost:8005 'doc1,doc2'")
        print("\n🧪 Proceeding with tests anyway (will show expected errors)...")
        valid_documents = test_document_ids  # Use original list anyway
    
    # Run tests
    success = tester.run_comprehensive_test(valid_documents, custom_scenarios)
    
    if success:
        print("🎉 All orchestration tests passed!")
        print("💼 Legal AI Assistant is ready for complex document analysis!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        if not valid_documents or len(valid_documents) != len(test_document_ids):
            print("ℹ️ Some failures may be due to missing test documents")
        sys.exit(1)

if __name__ == "__main__":
    main()