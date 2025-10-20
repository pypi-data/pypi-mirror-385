from pathlib import Path
from docpipe import PyMuPDFSerializer

serializer = PyMuPDFSerializer()
file_path = Path("tests/data/pdf/1.pdf")

print(f"Testing with: {file_path}")
print("\n1. Testing default header_row=None:")

for chunk in serializer.iterate_chunks(file_path):
    if chunk.type == "image":
        print(chunk.type)