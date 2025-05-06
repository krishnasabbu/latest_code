import xml.etree.ElementTree as ET
import json


def parse_translation_units(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    translation_map = {}

    for tu in root.findall(".//tu"):
        srclang = tu.attrib.get("srclang", "EN-US")
        tuvs = tu.findall("tuv")

        source_text = None
        target_text = None
        target_lang = None

        for tuv in tuvs:
            lang = tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
            seg = tuv.find("seg").text.strip() if tuv.find("seg") is not None else ""

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


# Example usage:
xml_path = "sample.xml"
result = parse_translation_units(xml_path)
print(json.dumps(result, indent=2, ensure_ascii=False))
