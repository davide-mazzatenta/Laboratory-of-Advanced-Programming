import requests

GATEWAY_URL = "http://localhost:8080"

USER_ID = "54df1b72-6838-4061-8312-32ac7d3ce640"
PROJECT_ID = "test_project"
DOC_ID = "doc123"   # 👈 doc_id scelto manualmente
TITLE = "Test Document"
PDF_PATH = "Prima_rata.pdf"   # <-- cambia con un PDF esistente

def health_check():
    r = requests.get(f"{GATEWAY_URL}/api/health")
    print("Health:", r.json())

def upload_document():
    files = {"file": open(PDF_PATH, "rb")}
    data = {
        "user_id": USER_ID,
        "project_id": PROJECT_ID,
        "title": TITLE,
        "doc_id": DOC_ID   # 👈 forzato doc_id
    }
    r = requests.post(f"{GATEWAY_URL}/api/v1/documents/upload", files=files, data=data)
    resp = r.json()
    print("Upload:", resp)
    return DOC_ID   # ritorna quello che abbiamo passato

def list_documents():
    r = requests.get(f"{GATEWAY_URL}/api/v1/documents/{USER_ID}/{PROJECT_ID}")
    resp = r.json()
    print("List documents:", resp)
    return resp

def query_document(doc_id, query="Qual è l’argomento principale?"):
    payload = {
        "user_id": USER_ID,
        "project_id": PROJECT_ID,
        "doc_id": doc_id,
        "query": query,
        "limit": 2000
    }
    r = requests.post(f"{GATEWAY_URL}/api/v1/documents/query", json=payload)
    resp = r.json()
    print("Query response:", resp)
    return resp

if __name__ == "__main__":
    health_check()
    doc_id = upload_document()
    list_documents()
    query_document(doc_id)