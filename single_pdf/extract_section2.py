""" import xml.etree.ElementTree as ET
import json

def extract_sections_from_xml(file_path, output_json_path):
    # Load XML from a file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace, if the XML uses namespaces
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Secciones a ignorar
    ignored_sections = ["introduction",
        "related works", "fig", "acknowledgements"]
    # Secciones deseadas (opcional para mejora)
    desired_sections = ["abstract", "experimental",
        "results and discussion", "conclusions"]

    # Function for extracting content under a specific tag, handles namespaces
    def extract_content_by_tag(tag_name):
        content = []
        path = f".//{{{ns['tei']}}}{tag_name}" if ns else f".//{tag_name}"
        for elem in root.findall(path):
            text = ''.join(elem.itertext())
            if text:
                content.append(text.strip())
        return " ".join(content)

    # Función para determinar si una sección debe ser ignorada o considerada deseada
    def check_section(section_title):
        section_title_lower = section_title.lower()
        if any(ignored in section_title_lower for ignored in ignored_sections):
            return None  # Ignorar sección
        for desired in desired_sections:
            if desired in section_title_lower:
                return desired.title()  # Devuelve el nombre de la sección deseada formateada
        return section_title.title()  # Por defecto, devolver el título formateado

    # Function to extract all relevant sections
    def extract_sections():
        sections = {}
        current_section_title = None

        for elem in root.iter():
            if elem.tag.endswith("head"):
                section_title = elem.text.strip() if elem.text else ""
                current_section_title = check_section(section_title)

            elif elem.tag.endswith("p") and current_section_title:
                text = ''.join(elem.itertext()).strip()
                if text:
                    if current_section_title not in sections:
                        sections[current_section_title] = []
                    sections[current_section_title].append(text)

        # Concatenate texts within the same sections
        for section, texts in sections.items():
            sections[section] = " ".join(texts)
        return sections

    # Extraer secciones y procesar datos JSON
    sections = extract_sections()
    sections["Abstract"] = extract_content_by_tag(
        "abstract")  # Agrega el contenido del abstracto

    # Formatear secciones para salida JSON
    json_sections = [{"title": key, "content": value}
        for key, value in sections.items()]
    json_data = json.dumps(json_sections, indent=2)

    # Escribir JSON en un archivo
    with open(output_json_path, 'w') as json_file:
        json_file.write(json_data)

    return f"JSON guardado correctamente en {output_json_path}" """

import xml.etree.ElementTree as ET
import json


def extract_sections_from_xml(file_path, output_json_path):
    # Load XML from a file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace, if the XML uses namespaces
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Function for extracting content under a specific tag, handles namespaces
    def extract_content_by_tag(tag_name):
        content = []
        # Adjust the label name for the namespace if necessary.
        path = f".//{{{ns['tei']}}}{tag_name}" if ns else f".//{tag_name}"
        for elem in root.findall(path):
            text = ''.join(elem.itertext())
            if text:
                content.append(text.strip())
        return " ".join(content)

    # Function to extract content according to keywords
    def extract_content_by_keywords(start_keywords, end_section):
        content = []
        capture = False
        for elem in root.iter():
            if elem.tag.endswith("head"):
                if elem.text and any(keyword.lower() in elem.text.lower() for keyword in start_keywords):
                    capture = True
                elif elem.text and end_section.lower() in elem.text.lower():
                    break
            if capture and elem.tag.endswith("p"):
                text = ''.join(elem.itertext())
                if text:
                    content.append(text.strip())
        return " ".join(content)

    # Function to extract content by specific ID
    def extract_by_xml_id(xml_id):
        for elem in root.findall(".//*[@xml:id='" + xml_id + "']"):
            return " ".join(elem.itertext())

    # Extraction of sections
    """ abstract_content = extract_content_by_keywords(
        ["Introduction"], "Experimental") """
    abstract_content = extract_content_by_tag("abstract")
    experimental_content = extract_content_by_keywords(
        ["Experimental", "Experimental studies", "Experiments", "Methods"], "Results and discussion")
    results_discussion_content = extract_content_by_keywords(
        ["Results and discussion", "Result and discussion", "Results"], "Conclusion")
    supporting_information_content = extract_content_by_keywords(
        ["Supporting Information", "Supporting"], "Conclusion")
    conclusions_content = extract_content_by_keywords(
        ["Conclusion", "Conclusions"], "Conclusion")
    # specific_id_content = extract_by_xml_id("_ZT2rFX7")

    sections = [
        {"title": "Abstract", "content": abstract_content},
        {"title": "Experimental", "content": experimental_content},
        {"title": "Results and discussion", "content": results_discussion_content},
        {"title": "Conclusions", "content": conclusions_content},
    ]

    if supporting_information_content:
        sections.append({"title": "Supporting Information",
                        "content": supporting_information_content})

    json_data = json.dumps(sections, indent=2)

    with open(output_json_path, 'w') as json_file:
        json_file.write(json_data)

    return f"JSON guardado correctamente en {output_json_path}"


# Example usage
xml_file_path = '../xml_results/papers1/paper_16238777645e67b6116072c5.89519248.xml'
output_json_path = '../json_results/papers1/paper_.json'
resultado = extract_sections_from_xml(xml_file_path, output_json_path)
print(resultado)
