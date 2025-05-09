from lxml import etree
import json


def get_clean_seg_text(seg_el):
    text_parts = []
    for child in seg_el.iter():
        if child.tag == 'seg':
            if child.text:
                text_parts.append(child.text)
        elif child.tag not in {'ph', 'bpt', 'ept', 'it'}:
            if child.text:
                text_parts.append(child.text)
        if child.tail:
            text_parts.append(child.tail)
    return ''.join(text_parts).strip()


def parse_translation_units(xml_file):
    with open(xml_file, 'rb') as f:
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(f, parser)
        root = tree.getroot()

    translation_map = {}

    for tu in root.xpath(".//tu"):
        srclang = tu.get("srclang", "EN-US")
        tuvs = tu.xpath("tuv")

        source_text = None
        target_text = None
        target_lang = None

        for tuv in tuvs:
            lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
            seg_el = tuv.find("seg")
            seg = get_clean_seg_text(seg_el) if seg_el is not None else ""

            if lang == srclang:
                source_text = seg
            else:
                target_lang = lang
                target_text = seg

        if source_text and target_text and target_lang:
            key = f"{srclang}:{target_lang}"
            if key not in translation_map:
                translation_map[key] = {}
            translation_map[key][source_text] = target_text

    return translation_map


# Usage
result = parse_translation_units("sample.xml")
print(json.dumps(result, indent=2, ensure_ascii=False))
