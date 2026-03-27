#!/usr/bin/env python3
"""
Updated API Gateway Test with better debugging
"""

import os
import requests
from pathlib import Path
import uuid
import json
import time

# Configuration - VIA API GATEWAY (like frontend)
API_GATEWAY_URL = "http://localhost:8080"  # Via API Gateway
DOCUMENT_SERVICE_DIRECT_URL = "http://localhost:8000"  # For health comparison
PDF_DIR = "pdfs"
REAL_USER_ID = "54df1b72-6838-4061-8312-32ac7d3ce640"
TEST_PROJECTS = ["test_project", "my_documents", "research_papers"]

class GatewayDocumentServiceTester:
    def __init__(self):
        self.uploaded_docs = []
        self.test_results = {'passed': 0, 'failed': 0, 'errors': []}
        print("🌐 TESTING DOCUMENT SERVICE VIA API GATEWAY (port 8080)")
        print("   This tests exactly how the frontend calls the service")
        print("   Using existing PDFs from pdfs/ folder")
    
    def log_result(self, test_name, success, message=""):
        if success:
            print(f"✅ {test_name}")
            self.test_results['passed'] += 1
        else:
            print(f"❌ {test_name}: {message}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
    
    def create_frontend_headers(self):
        """Create headers that the frontend would typically send"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'React-Frontend/1.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
    
    def get_existing_pdfs(self):
        """Get list of existing PDF files"""
        pdf_dir = Path(PDF_DIR)
        if not pdf_dir.exists():
            print(f"❌ PDF directory '{PDF_DIR}' not found")
            return []
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in '{PDF_DIR}' directory")
            return []
        
        print(f"📁 Found {len(pdf_files)} PDF files:")
        for pdf in pdf_files[:5]:  # Show first 5
            print(f"   - {pdf.name}")
        if len(pdf_files) > 5:
            print(f"   ... and {len(pdf_files) - 5} more")
        
        return pdf_files
    
    def check_services_health(self):
        """Check if both gateway and document service are running"""
        print("🔍 Checking services health (gateway + service)...")
        
        # Check API Gateway
        try:
            response = requests.get(f"{API_GATEWAY_URL}/api/health", timeout=5)
            gateway_ok = response.status_code == 200
            self.log_result("API Gateway Health (/api/health)", gateway_ok)
            
            if gateway_ok:
                try:
                    health_data = response.json()
                    print(f"   Gateway status: {health_data.get('status', 'unknown')}")
                except:
                    print(f"   Gateway responded but no JSON data")
            return gateway_ok
            
        except requests.exceptions.ConnectionError:
            self.log_result("API Gateway Connection", False, "Connection refused - is the gateway running?")
            return False
        except Exception as e:
            self.log_result("API Gateway Health Check", False, str(e))
            return False
    
    def test_get_user_projects(self):
        """Test getting user projects via gateway - FIXED URL"""
        try:
            # FIXED: Use correct endpoint path
            url = f"{API_GATEWAY_URL}/api/v1/projects/{REAL_USER_ID}"
            print(f"🔍 Testing gateway route: {url}")
            
            response = requests.get(
                url,
                headers=self.create_frontend_headers(),
                timeout=10
            )
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                projects_data = response.json()
                projects = projects_data.get('projects', [])
                self.log_result("Get User Projects (Gateway)", True)
                print(f"   Found {len(projects)} projects: {[p.get('project_id') for p in projects]}")
                return projects
            else:
                self.log_result("Get User Projects (Gateway)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Get User Projects (Gateway)", False, str(e))
            return []
    
    def test_upload_document(self, pdf_path, project_id, title):
        """Test uploading a document via gateway"""
        try:
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                self.log_result(f"Upload {title}", False, "PDF file not found")
                return None
            
            print(f"🔍 Testing upload via gateway: {API_GATEWAY_URL}/api/v1/documents/upload")
            
            # Prepare multipart form data
            with open(pdf_file, 'rb') as f:
                files = {'file': (pdf_file.name, f, 'application/pdf')}
                data = {
                    'user_id': REAL_USER_ID,
                    'project_id': project_id,
                    'title': title
                }
                
                response = requests.post(
                    f"{API_GATEWAY_URL}/api/v1/documents/upload",
                    files=files,
                    data=data,
                    timeout=30  # PDF processing can take time
                )
            
            print(f"   Upload response status: {response.status_code}")
            print(f"   Upload response: {response.text}")
            
            if response.status_code in [200, 201]:
                doc_info = response.json()
                self.log_result(f"Upload '{title}'", True)
                
                # Store uploaded doc info for later tests
                uploaded_doc = {
                    'doc_id': doc_info.get('doc_id'),  # FIXED: Use doc_id instead of document_id
                    'user_id': REAL_USER_ID,
                    'project_id': project_id,
                    'title': title,
                    'filename': pdf_file.name
                }
                self.uploaded_docs.append(uploaded_doc)
                
                print(f"   Document ID: {doc_info.get('doc_id')}")
                return uploaded_doc
            else:
                self.log_result(f"Upload '{title}'", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"Upload '{title}'", False, str(e))
            return None
    
    def test_get_project_documents(self, project_id):
        """Test getting documents in a project via gateway"""
        try:
            # FIXED: Use correct endpoint path
            url = f"{API_GATEWAY_URL}/api/v1/documents/{REAL_USER_ID}/{project_id}"
            print(f"🔍 Testing project documents via gateway: {url}")
            
            response = requests.get(
                url,
                headers=self.create_frontend_headers(),
                timeout=10
            )
            
            print(f"   Project docs response status: {response.status_code}")
            
            if response.status_code == 200:
                docs_data = response.json()
                documents = docs_data.get('documents', [])
                self.log_result(f"Get Project Documents ({project_id})", True)
                print(f"   Found {len(documents)} documents in {project_id}")
                return documents
            else:
                self.log_result(f"Get Project Documents ({project_id})", False,
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result(f"Get Project Documents ({project_id})", False, str(e))
            return []
    
    def test_get_document_binary(self, doc):
        """Test getting document binary data via gateway"""
        try:
            # Try both endpoints - with and without /pdf suffix
            urls_to_try = [
                f"{API_GATEWAY_URL}/api/v1/documents/{doc['user_id']}/{doc['project_id']}/{doc['doc_id']}/pdf",
                f"{API_GATEWAY_URL}/api/v1/documents/{doc['user_id']}/{doc['project_id']}/{doc['doc_id']}"
            ]
            
            for i, url in enumerate(urls_to_try):
                print(f"🔍 Trying PDF endpoint {i+1}: {url}")
                
                response = requests.get(
                    url,
                    headers=self.create_frontend_headers(),
                    timeout=15
                )
                
                print(f"   PDF response status: {response.status_code}")
                
                if response.status_code == 200:
                    self.log_result(f"Get PDF Binary ({doc['title']})", True)
                    print(f"   PDF size: {len(response.content)} bytes")
                    return response.content
                elif i == 0:  # First URL failed, try second
                    continue
                else:  # Both failed
                    self.log_result(f"Get PDF Binary ({doc['title']})", False,
                                  f"Both endpoints failed. Last: HTTP {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            self.log_result(f"Get PDF Binary ({doc['title']})", False, str(e))
            return None
    
    def test_get_document_text(self, doc):
        """Test getting document text content via gateway"""
        try:
            url = f"{API_GATEWAY_URL}/api/v1/documents/{doc['user_id']}/{doc['project_id']}/{doc['doc_id']}/text"
            print(f"🔍 Testing text endpoint via gateway: {url}")
            
            response = requests.get(
                url,
                headers=self.create_frontend_headers(),
                timeout=15
            )
            
            print(f"   Text response status: {response.status_code}")
            
            if response.status_code == 200:
                text_data = response.json()
                self.log_result(f"Get Text Content ({doc['title']})", True)
                text_content = text_data.get('text_content', '')
                print(f"   Text length: {len(text_content)} characters")
                if text_content:
                    preview = text_content[:100].replace('\n', ' ')
                    print(f"   Preview: {preview}...")
                return text_data
            else:
                self.log_result(f"Get Text Content ({doc['title']})", False,
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"Get Text Content ({doc['title']})", False, str(e))
            return None
    
    def debug_gateway_routing(self):
        """Debug gateway routing by testing direct vs gateway"""
        print("\n🔧 DEBUG: Gateway Routing Analysis")
        print("=" * 50)
        
        # Test direct service first
        print("1️⃣ Testing DIRECT service endpoints:")
        try:
            direct_response = requests.get(f"{DOCUMENT_SERVICE_DIRECT_URL}/api/v1/projects/{REAL_USER_ID}")
            print(f"   Direct service /api/v1/projects/{REAL_USER_ID}: {direct_response.status_code}")
            
            if direct_response.status_code == 200:
                data = direct_response.json()
                print(f"   Direct service returned: {data}")
        except Exception as e:
            print(f"   Direct service error: {e}")
        
        # Test gateway routing
        print("\n2️⃣ Testing GATEWAY routing:")
        try:
            gateway_response = requests.get(f"{API_GATEWAY_URL}/api/v1/projects/{REAL_USER_ID}")
            print(f"   Gateway /api/v1/projects/{REAL_USER_ID}: {gateway_response.status_code}")
            
            if gateway_response.status_code != 200:
                print(f"   Gateway error response: {gateway_response.text}")
                print(f"   Gateway headers: {dict(gateway_response.headers)}")
        except Exception as e:
            print(f"   Gateway error: {e}")
    
    def simulate_frontend_workflow(self):
        """Simulate complete frontend workflow via gateway"""
        print("\n🎭 Simulating Complete Frontend Workflow (Via Gateway)")
        print("=" * 60)
        
        # Debug routing first
        self.debug_gateway_routing()
        
        # Get existing PDFs
        pdf_files = self.get_existing_pdfs()
        if not pdf_files:
            print("❌ No PDF files found in pdfs/ folder")
            return
        
        # Step 1: Frontend app loads - check user projects
        print("\n1️⃣ Frontend loads: Checking user projects...")
        initial_projects = self.test_get_user_projects()
        
        # Step 2: User uploads documents (simulate frontend upload workflow)
        print("\n2️⃣ User uploads documents...")
        project_index = 0
        for i, pdf_file in enumerate(pdf_files):
            if i >= 2:  # Limit uploads for testing
                break
                
            project_id = TEST_PROJECTS[project_index % len(TEST_PROJECTS)]
            title = pdf_file.stem  # filename without extension
            
            print(f"   Uploading {pdf_file.name} to {project_id}...")
            self.test_upload_document(str(pdf_file), project_id, title)
            project_index += 1
            time.sleep(1)  # Small delay between uploads
        
        if not self.uploaded_docs:
            print("❌ No documents uploaded successfully")
            return
        
        print(f"\n✅ Frontend uploaded {len(self.uploaded_docs)} documents")
        
        # Step 3: Frontend refreshes projects list
        print("\n3️⃣ Frontend refreshes projects list...")
        updated_projects = self.test_get_user_projects()
        
        # Step 4: User browses projects (simulate clicking on projects)
        print("\n4️⃣ User browses project contents...")
        for project in TEST_PROJECTS:
            if any(doc['project_id'] == project for doc in self.uploaded_docs):
                print(f"   📂 User clicks on project: {project}")
                self.test_get_project_documents(project)
        
        # Step 5: User views/downloads specific documents
        print("\n5️⃣ User views/downloads documents...")
        for doc in self.uploaded_docs[:2]:  # Test first 2 documents
            print(f"   👁️ User views: {doc['title']}")
            pdf_data = self.test_get_document_binary(doc)
            text_data = self.test_get_document_text(doc)
            
            if pdf_data:
                print(f"     📄 PDF ready for display/download")
            if text_data:
                print(f"     📝 Text content available for search/processing")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🌐 GATEWAY TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print(f"\n🚨 Errors:")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"\n📊 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 Excellent! Gateway is routing perfectly!")
            elif success_rate >= 70:
                print("👍 Good! Minor gateway issues to address.")
            else:
                print("⚠️ Several gateway issues need attention.")
        
        print(f"\n📄 Documents uploaded via gateway: {len(self.uploaded_docs)}")
        for doc in self.uploaded_docs:
            print(f"   - {doc['title']} (ID: {doc['doc_id']}) in {doc['project_id']}")

def main():
    """Main test execution for gateway"""
    print("🚀 API GATEWAY DOCUMENT SERVICE TEST SUITE")
    print("=" * 70)
    print("Testing document service through API Gateway on port 8080")
    print("This simulates EXACTLY how your React frontend calls the API")
    
    tester = GatewayDocumentServiceTester()
    
    # Check if gateway is running
    if not tester.check_services_health():
        print("\n❌ API Gateway is not running!")
        print("To start the services:")
        print("   1. Document Service:")
        print("      cd document-service")
        print("      python main.py")
        print("   2. API Gateway:")
        print("      cd api-gateway")
        print("      mvn spring-boot:run")
        print("\nTrying to run tests anyway (some may fail)...")
    else:
        print("\n✅ API Gateway is running!")
    
    # Run the test suite
    try:
        tester.simulate_frontend_workflow()
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        tester.log_result("Test Suite Execution", False, str(e))
    
    # Print results
    tester.print_summary()
    
    print(f"\n🔧 Next Steps:")
    print(f"   1. Restart your API Gateway after applying the fixes")
    print(f"   2. Restart your Document Service after applying the fixes")
    print(f"   3. Run the test again")

if __name__ == "__main__":
    main()