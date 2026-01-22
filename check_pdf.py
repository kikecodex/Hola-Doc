from langchain_community.document_loaders import PyPDFLoader

pdf_path = "knowledge/7631107_opinion_d008_2026_oece_dtn(1).pdf"
try:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages.")
    found = False
    for i, page in enumerate(pages):
        if "Junta" in page.page_content:
            print(f"FOUND 'Junta' on page {i+1}")
            print(page.page_content[:500]) # Print context
            found = True
    if not found:
        print("Keyword 'Junta' NOT FOUND in PDF.")
except Exception as e:
    print(f"Error loading PDF: {e}")
