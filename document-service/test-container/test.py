#!/usr/bin/env python3
"""
Direct Document Service Test (test.py)
Tests the document-service directly on port 8000
This bypasses the API Gateway to test the service in isolation
Uses existing PDFs in the pdfs/ folder
"""

import os
import requests
from pathlib import Path
import uuid
import json
import time

# Configuration - DIRECT SERVICE
DOCUMENT_SERVICE_URL = "http://localhost:8000"  # Direct to document service
PDF_DIR = "pdfs"
REAL_USER_ID = "54df1b72-6838-4061-8312-32ac7d3ce640"
TEST_PROJECTS = ["test_project", "my_documents", "research_papers"]

class DirectDocumentServiceTester:
    def __init__(self):
        self.uploaded_docs = []
        self.test_results = {'passed': 0, 'failed': 0, 'errors': []}
        print("🎯 TESTING DOCUMENT SERVICE DIRECTLY (port 8000)")
        print("   This tests the FastAPI service without the gateway")
        print("   Using existing PDFs from pdfs/ folder")
    
    def log_result(self, test_name, success, message=""):
        if success:
            print(f"✅ {test_name}")
            self.test_results['passed'] += 1
        else:
            print(f"❌ {test_name}: {message}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
    
    def check_service_health(self):
        """Check if document service is running directly"""
        print("🔍 Checking document service health (direct)...")
        
        try:
            # Test root endpoint
            response = requests.get(f"{DOCUMENT_SERVICE_URL}/", timeout=5)
            root_ok = response.status_code == 200
            self.log_result("Root Endpoint (/)", root_ok)
            
            # Test health endpoint
            response = requests.get(f"{DOCUMENT_SERVICE_URL}/health", timeout=5)
            health_ok = response.status_code == 200
            self.log_result("Health Endpoint (/health)", health_ok)
            
            if health_ok:
                health_data = response.json()
                print(f"   Service: {health_data.get('service', 'unknown')}")
                print(f"   Status: {health_data.get('status', 'unknown')}")
            
            return root_ok and health_ok
            
        except requests.exceptions.ConnectionError:
            self.log_result("Document Service Connection", False, "Connection refused - is the service running?")
            return False
        except Exception as e:
            self.log_result("Document Service Health", False, str(e))
            return False
    
    def get_existing_pdfs(self):
        """Get list of existing PDF files"""
        pdf_files = []
        if Path(PDF_DIR).exists():
            pdf_files = list(Path(PDF_DIR).glob("*.pdf"))
        
        print(f"📁 Found {len(pdf_files)} existing PDF files:")
        for pdf_file in pdf_files:
            size_kb = pdf_file.stat().st_size / 1024
            print(f"   - {pdf_file.name} ({size_kb:.1f} KB)")
        
        return pdf_files
    
    def test_upload_document(self, pdf_path, project_id, title, doc_id=None):
        """Test document upload directly to FastAPI service"""
        print(f"📤 Testing direct upload: {title}")
        
        if not os.path.exists(pdf_path):
            self.log_result(f"Upload {title}", False, f"PDF not found: {pdf_path}")
            return None
        
        if not doc_id:
            doc_id = str(uuid.uuid4())
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': pdf_file}
                data = {
                    'user_id': REAL_USER_ID,
                    'project_id': project_id,
                    'doc_id': doc_id,
                    'title': title
                }
                
                # Direct FastAPI endpoint
                response = requests.post(f"{DOCUMENT_SERVICE_URL}/api/v1/documents/upload", 
                                       files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    document_id = result['document_id']
                    self.log_result(f"Upload {title}", True)
                    
                    # Store for later tests
                    self.uploaded_docs.append({
                        'document_id': document_id,
                        'user_id': REAL_USER_ID,
                        'project_id': project_id,
                        'doc_id': doc_id,
                        'title': title
                    })
                    return document_id
                else:
                    self.log_result(f"Upload {title}", False, f"HTTP {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            self.log_result(f"Upload {title}", False, str(e))
            return None
    
    def test_get_user_projects(self):
        """Test getting user projects directly"""
        print(f"📋 Testing get user projects (direct): {REAL_USER_ID}")
        
        try:
            response = requests.get(f"{DOCUMENT_SERVICE_URL}/api/v1/projects/{REAL_USER_ID}")
            
            if response.status_code == 200:
                result = response.json()
                projects = result.get('projects', [])
                self.log_result("Get User Projects (Direct)", True)
                print(f"   Found {len(projects)} projects:")
                for project in projects:
                    print(f"   - {project['project_id']}: {project['document_count']} documents")
                return projects
            else:
                self.log_result("Get User Projects (Direct)", False, f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_result("Get User Projects (Direct)", False, str(e))
            return []
    
    def test_get_project_documents(self, project_id):
        """Test listing documents in a project directly"""
        print(f"📄 Testing get project documents (direct): {project_id}")
        
        try:
            response = requests.get(f"{DOCUMENT_SERVICE_URL}/api/v1/documents/{REAL_USER_ID}/{project_id}")
            
            if response.status_code == 200:
                result = response.json()
                documents = result.get('documents', [])
                self.log_result(f"Get Project Documents Direct ({project_id})", True)
                print(f"   Found {len(documents)} documents:")
                for doc in documents:
                    content_preview = doc['content'][:50] + "..." if len(doc['content']) > 50 else doc['content']
                    print(f"   - {doc['title']} ({doc['doc_id']})")
                    print(f"     Content preview: {content_preview}")
                return documents
            else:
                self.log_result(f"Get Project Documents Direct ({project_id})", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_result(f"Get Project Documents Direct ({project_id})", False, str(e))
            return []
    
    def test_get_document_binary(self, doc):
        """Test getting document PDF binary directly"""
        print(f"📥 Testing get PDF binary (direct): {doc['title']}")
        
        try:
            response = requests.get(
                f"{DOCUMENT_SERVICE_URL}/api/v1/documents/{doc['user_id']}/{doc['project_id']}/{doc['doc_id']}"
            )
            
            if response.status_code == 200:
                pdf_size = len(response.content)
                self.log_result(f"Get PDF Binary Direct ({doc['title']})", True)
                print(f"   PDF size: {pdf_size} bytes")
                
                # Verify it's actually a PDF
                if response.content[:4] == b'%PDF':
                    print(f"   ✓ Valid PDF header detected")
                    return response.content
                else:
                    self.log_result(f"PDF Validation Direct ({doc['title']})", False, "Invalid PDF format")
                    return None
            else:
                self.log_result(f"Get PDF Binary Direct ({doc['title']})", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result(f"Get PDF Binary Direct ({doc['title']})", False, str(e))
            return None
    
    def test_get_document_text(self, doc):
        """Test getting document text content directly"""
        print(f"📄 Testing get text content (direct): {doc['title']}")
        
        try:
            response = requests.get(
                f"{DOCUMENT_SERVICE_URL}/api/v1/documents/{doc['user_id']}/{doc['project_id']}/{doc['doc_id']}/text"
            )
            
            if response.status_code == 200:
                result = response.json()
                text_content = result.get('text_content', '')
                self.log_result(f"Get Text Content Direct ({doc['title']})", True)
                
                # Show preview
                text_preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
                print(f"   Text preview: {text_preview}")
                print(f"   Text length: {len(text_content)} characters")
                return text_content
            else:
                self.log_result(f"Get Text Content Direct ({doc['title']})", False,
                              f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result(f"Get Text Content Direct ({doc['title']})", False, str(e))
            return None
    
    def test_error_cases(self):
        """Test error handling directly"""
        print("\n🚨 Testing Error Cases (Direct)")
        print("=" * 40)
        
        # Test non-existent document
        try:
            response = requests.get(f"{DOCUMENT_SERVICE_URL}/api/v1/documents/{REAL_USER_ID}/fake_project/fake_doc")
            success = response.status_code == 404
            self.log_result("Non-existent Document Direct (404)", success, 
                          f"Expected 404, got {response.status_code}" if not success else "")
        except Exception as e:
            self.log_result("Non-existent Document Error Test Direct", False, str(e))
        
        # Test non-existent user projects
        try:
            fake_user = str(uuid.uuid4())
            response = requests.get(f"{DOCUMENT_SERVICE_URL}/api/v1/projects/{fake_user}")
            success = response.status_code == 200  # Should return empty list
            if success:
                result = response.json()
                success = len(result.get('projects', [])) == 0
            self.log_result("Non-existent User Projects Direct", success,
                          "Should return empty projects list" if not success else "")
        except Exception as e:
            self.log_result("Non-existent User Projects Test Direct", False, str(e))
    
    def run_comprehensive_tests(self):
        """Run all direct service tests"""
        print("\n🧪 COMPREHENSIVE DIRECT SERVICE TESTS")
        print("=" * 50)
        
        # Get existing PDFs
        pdf_files = self.get_existing_pdfs()
        if not pdf_files:
            print("❌ No PDF files found in pdfs/ folder")
            return
        
        # Upload existing PDFs to different projects
        project_index = 0
        for i, pdf_file in enumerate(pdf_files):
            project_id = TEST_PROJECTS[project_index % len(TEST_PROJECTS)]
            title = pdf_file.stem  # filename without extension
            
            self.test_upload_document(str(pdf_file), project_id, title)
            project_index += 1
        
        if not self.uploaded_docs:
            print("❌ No documents uploaded successfully")
            return
        
        print(f"\n✅ Successfully uploaded {len(self.uploaded_docs)} documents")
        
        # Test all endpoints
        print(f"\n📋 Testing project listing...")
        projects = self.test_get_user_projects()
        
        print(f"\n📂 Testing document listing per project...")
        for project in TEST_PROJECTS:
            if any(doc['project_id'] == project for doc in self.uploaded_docs):
                self.test_get_project_documents(project)
        
        print(f"\n📄 Testing document retrieval...")
        for doc in self.uploaded_docs[:2]:  # Test first 2 documents
            self.test_get_document_binary(doc)
            self.test_get_document_text(doc)
        
        # Test error cases
        self.test_error_cases()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 DIRECT SERVICE TEST SUMMARY")
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
                print("🎉 Excellent! Document service is working perfectly!")
            elif success_rate >= 70:
                print("👍 Good! Minor issues to address.")
            else:
                print("⚠️ Several issues need attention.")
        
        print(f"\n📄 Documents uploaded: {len(self.uploaded_docs)}")
        for doc in self.uploaded_docs:
            print(f"   - {doc['title']} in {doc['project_id']}")

def main():
    """Main test execution for direct service"""
    print("🚀 DIRECT DOCUMENT SERVICE TEST SUITE")
    print("=" * 70)
    print("Testing FastAPI service directly on port 8000")
    print("This bypasses the API Gateway completely")
    
    tester = DirectDocumentServiceTester()
    
    # Check if service is running
    if not tester.check_service_health():
        print("\n❌ Document service is not running!")
        print("To start the service:")
        print("   cd document-service")
        print("   python main.py")
        return
    
    print("\n✅ Document service is running!")
    
    # Run the test suite
    try:
        tester.run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        tester.log_result("Test Suite Execution", False, str(e))
    
    # Print results
    tester.print_summary()
    
    print(f"\n🧹 Note: Test documents remain in your database")
    print(f"   - User: {REAL_USER_ID}")
    print(f"   - Projects: {', '.join(TEST_PROJECTS)}")

if __name__ == "__main__":
    main()