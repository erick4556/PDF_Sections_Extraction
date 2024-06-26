import xml.etree.ElementTree as ET
import json
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Suponiendo que el modelo y tokenizer están adecuadamente configurados y entrenados
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

def classify_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    label_id = torch.argmax(outputs.logits, dim=-1).item()
    # Mapeo de etiquetas del modelo a las categorías de secciones requeridas
    section_mapping = {0: "Abstract", 1: "Experimental", 2: "Results and discussion"}
    return section_mapping[label_id]

def extract_sections_from_xml(file_path, output_json_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    sections = {}
    current_section = None
    content = []

    for elem in root.iter():
        if elem.tag.endswith("p"):
            text = ''.join(elem.itertext()).strip()
            if text:
                section_label = classify_text(text)
                if section_label != current_section:
                    if current_section is not None and content:
                        if current_section in sections:
                            sections[current_section] += " " + " ".join(content)
                        else:
                            sections[current_section] = " ".join(content)
                    current_section = section_label
                    content = [text]
                else:
                    content.append(text)

    # Guardar la última sección encontrada
    if current_section is not None and content:
        if current_section in sections:
            sections[current_section] += " " + " ".join(content)
        else:
            sections[current_section] = " ".join(content)

    # Preparar la salida JSON
    json_sections = [{"title": key, "content": value} for key, value in sections.items() if key in ["Abstract", "Experimental", "Results and discussion"]]
    json_data = json.dumps(json_sections, indent=2)

    with open(output_json_path, 'w') as json_file:
        json_file.write(json_data)

    return f"JSON guardado correctamente en {output_json_path}"

# Ejecutar la función
xml_file_path = '../xml_results/paper_30.xml'
output_json_path = '../json_results/paper30_extraction.json'
resultado = extract_sections_from_xml(xml_file_path, output_json_path)
print(resultado)
