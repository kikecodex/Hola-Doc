from langchain_community.document_loaders import PyPDFLoader
import os

def find_article_100_raw():
    path = "knowledge/6444155-ref-reglamento-de-la-ley-de-contrataciones-del-estado-con-modificaciones-posteriores-hasta-08-ene-2026-2-v2.pdf"
    
    if not os.path.exists(path):
        print("❌ PDF not found.")
        return

    print(f"📖 Reading {path}...")
    loader = PyPDFLoader(path)
    pages = loader.load()
    
    print(f"📄 Total Pages: {len(pages)}")
    
    found = False
    for i, page in enumerate(pages):
        content = page.page_content
        # Search for variants of Article 100
        if "100" in content and ("Art" in content or "ART" in content):
            # Print context around "100"
            idx = content.find("100")
            start = max(0, idx - 50)
            end = min(len(content), idx + 200)
            snippet = content[start:end].replace("\n", " ")
            
            # Check if it looks like the header of the article
            if "rtículo 100" in content or "RTÍCULO 100" in content:
                print(f"\n✅ FOUND POTENTIAL MATCH on Page {i+1}:")
                print(f"...{snippet}...")
                found = True
    
    if not found:
        print("\n❌ 'Artículo 100' header not found in text.")

if __name__ == "__main__":
    find_article_100_raw()
