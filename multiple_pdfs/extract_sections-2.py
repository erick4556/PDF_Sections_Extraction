import xml.etree.ElementTree as ET
import json
import glob
import re
import unicodedata
import os
import logging

# Configurar el registro (logging)
log_file_path = 'process_errors.log'
logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def clean_text(text):
    # Normalización Unicode para eliminar caracteres especiales
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Eliminar caracteres no imprimibles
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Eliminar todos los caracteres no ASCII
    
    # Eliminar caracteres no deseados usando expresiones regulares
    text = re.sub(r'[\u00b0\n\t\r]', ' ', text)  # Eliminar caracteres específicos
    text = re.sub(r'[^A-Za-z0-9\s,.?!;:()\-\'\"/]', '', text)  # Mantener solo caracteres alfanuméricos y puntuación básica, incluyendo "/"
    
    # Reemplazar múltiples espacios por uno solo
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_sections_from_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    title = ''
    title_element = root.find(".//tei:title", ns)
    if title_element is not None:
        title = ''.join(title_element.itertext()).strip()

    def extract_content_by_tag(tag_name):
        content = []
        path = f".//{{{ns['tei']}}}{tag_name}" if ns else f".//{tag_name}"
        for elem in root.findall(path):
            text = ''.join(elem.itertext())
            if text:
                content.append(clean_text(text.strip()))
        return " ".join(content)

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
                text = ''.join(elem.itertext()).strip()
                if text:
                    content.append(clean_text(text))
        return " ".join(content)
    
    def extract_doi():
        doi_element = root.find(".//tei:idno[@type='DOI']", ns)
        if doi_element is not None:
            return clean_text(doi_element.text.strip())
        return None

    doi = extract_doi()
    abstract_content = extract_content_by_tag("abstract")
    experimental_content = extract_content_by_keywords(
        ["Experimental", "Experimental studies", "Experiments", "Experimental methods", "Methods"], "Results and discussion")
    results_discussion_content = extract_content_by_keywords(
        ["Results and discussion", "Result and discussion", "Results"], "Conclusion")
    supporting_information_content = extract_content_by_keywords(
        ["Supporting Information", "Supporting"], "Conclusion")
    conclusions_content = extract_content_by_keywords(
        ["Conclusion", "Conclusions"], "Conclusion")

    sections = [
        {"title": "Doi", "content": doi if doi else "Doi not found"},
        {"title": "Article_Title", "content": title},
        {"title": "Abstract", "content": abstract_content},
        {"title": "Experimental", "content": experimental_content},
        {"title": "Results_and_Discussion", "content": results_discussion_content},
        {"title": "Conclusions", "content": conclusions_content},
    ]

    if supporting_information_content:
        sections.append({"title": "Supporting_Information", "content": supporting_information_content})

    return sections

def process_files_in_folder(xml_folder_path, complete_output_folder, incomplete_output_folder):
    os.makedirs(complete_output_folder, exist_ok=True)
    os.makedirs(incomplete_output_folder, exist_ok=True)
    xml_files = glob.glob(os.path.join(xml_folder_path, '*.xml'))

    for index, xml_file_path in enumerate(xml_files, start=1):
        try:
            sections = extract_sections_from_xml(xml_file_path)
            json_file_name = f'paper_{index}.json'

            all_sections_have_content = all(section['content'] for section in sections)
            output_json_path = os.path.join(
                complete_output_folder if all_sections_have_content else incomplete_output_folder,
                json_file_name
            )
            
            with open(output_json_path, 'w') as json_file:
                json.dump(sections, json_file, indent=2)

            print(f"JSON guardado correctamente en {output_json_path}")
        except Exception as e:
            error_message = f"Error procesando el archivo {xml_file_path}, Error: {str(e)}"
            print(error_message)
            logging.error(error_message)

# Uso
xml_folder_path = '../xml_results/'
complete_output_folder = '../json_results/complete/'
incomplete_output_folder = '../json_results/incomplete/'
process_files_in_folder(xml_folder_path, complete_output_folder, incomplete_output_folder)

if os.path.exists(log_file_path):
    print(f"El archivo de log se ha creado correctamente: {log_file_path}")
else:
    print("No se ha creado el archivo de log.")
