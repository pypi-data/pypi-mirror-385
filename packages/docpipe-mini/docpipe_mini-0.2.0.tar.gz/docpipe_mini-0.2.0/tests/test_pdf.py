from docpipe import PdfiumSerializer

serializer = PdfiumSerializer()
file_path = "tests\\data\\pdf\\1.pdf"

print(f"Testing with: {file_path}")
print("\n1. Testing default header_row=None:")

for chunk in serializer.iterate_chunks(file_path):
    print(chunk.type)