from pdf2docx import Converter
import mammoth
import aspose.words as aw
from bs4 import BeautifulSoup

pdf_path = r"C:\\Users\\Sabbu\\Desktop\\KMeans_Clustering_Report_KBest1.pdf"
output_docx = r"C:\\Users\\Sabbu\\Desktop\\KMeans_Clustering_Report_KBest.docx"

cv = Converter(pdf_path)
cv.convert(output_docx, start=0, end=None)  # Convert all pages
cv.close()

doc = aw.Document(output_docx)

# Save HTML with page break markers
options = aw.saving.HtmlSaveOptions()
options.export_images_as_base64 = True  # or False if you want images in folders
doc.save("output.html", options)

# Load raw HTML
with open("output.html", "r", encoding="utf-8") as f:
    raw_html = f.read()

# Parse and prettify
soup = BeautifulSoup(raw_html, "html.parser")

# Remove all <div> tags with 'aw-headerfooter-type' in their style attribute
for div in soup.find_all("div"):
    style_attr = div.get("style", "")
    if "aw-headerfooter-type" in style_attr:
        div.decompose()

# Find all <p> tags and check their text content
for p in soup.find_all("p"):
    if "Created with an evaluation copy of Aspose.Words" in p.get_text():
        p.decompose()

# Convert the whole body content to string for splitting
body_html = str(soup.body)

# Define the exact split tag (self-closing <br/> with style)
split_tag = '<br style="page-break-before:always; clear:both; mso-break-type:section-break"/>'

# Split the HTML based on the page-break <br>
pages = body_html.split(split_tag)

# Count pages
print(f"Total pages found: {len(pages)}")

pretty_html = soup.prettify()

# Save the beautified version
with open("output_pretty.html", "w", encoding="utf-8") as f:
    f.write(pretty_html)

print("HTML has been beautified and saved as output_pretty.html.")


