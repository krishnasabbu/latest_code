from pdf2docx import Converter
import aspose.words as aw
import tempfile
import os
from bs4 import BeautifulSoup

pdf_path = r"C:\\Users\\Sabbu\\Desktop\\KMeans_Clustering_Report_KBest1.pdf"
output_docx = r"C:\\Users\\Sabbu\\Desktop\\KMeans_Clustering_Report_KBest.docx"

cv = Converter(pdf_path)
cv.convert(output_docx, start=0, end=None)  # Convert all pages
cv.close()

doc = aw.Document(output_docx)
page_count = doc.page_count
# Create a temporary directory for HTML files
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Temporary folder: {temp_dir}")

    # Save each page as individual HTML in the temp folder
    options = aw.saving.HtmlSaveOptions()
    options.pretty_format = True
    options.export_images_as_base64 = True
    options.css_style_sheet_type = aw.saving.CssStyleSheetType.INLINE
    options.export_text_input_form_field_as_text = True
    options.export_page_margins = True

    html_paths = []
    for i in range(page_count):
        page_doc = doc.extract_pages(i, 1)
        file_path = os.path.join(temp_dir, f"page_{i + 1}.html")
        print(f"file path === {file_path}")
        page_doc.save(file_path, options)
        html_paths.append(file_path)

    # Combine all HTMLs into one
    combined_body = ""
    for file_path in sorted(html_paths):
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            body = str(soup)
            if body:
                combined_body += f"\n<!-- Page: {os.path.basename(file_path)} -->\n" + str(body)

    # Final combined HTML output
    combined_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Combined Document</title>
        <style>
            body {{ margin: 2em; }}
            .page-break {{ page-break-after: always; }}
        </style>
    </head>
    <body>
    {combined_body}
    </body>
    </html>
    """

    # Save final combined HTML to same temp folder (or elsewhere)
    final_path = "combined.html"
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(combined_body)

    print(f"\n✅ Combined HTML created at: {final_path}")
    # If needed, move it to a permanent location:
    # shutil.copy(final_path, "output/combined.html")


