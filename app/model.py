import torch
from transformers import AutoModelForObjectDetection, TableTransformerForObjectDetection
from PIL import Image
from torchvision import transforms
import numpy as np
import easyocr
from tqdm.auto import tqdm
import re

class MaxResize(object):
    def __init__(self, max_size=800):
        self.max_size = max_size

    def __call__(self, image):
        width, height = image.size
        current_max_size = max(width, height)
        scale = self.max_size / current_max_size
        resized_image = image.resize((int(round(scale*width)), int(round(scale*height))))
        return resized_image

class TableExtractor:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initializes the workshop. This is where we load all the heavy models,
        and it runs only once.
        """
        print("Initializing Table Extractor and loading models...")
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load models and processor
        self.detection_model = AutoModelForObjectDetection.from_pretrained("microsoft/table-transformer-detection", revision="no_timm")
        self.structure_model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-structure-recognition-v1.1-all")
        self.ocr_reader = easyocr.Reader(['en'])
        
        # Move models to the specified device
        self.detection_model.to(self.device)
        self.structure_model.to(self.device)
        
        # Prepare transforms
        self.detection_transform = self._get_detection_transform()
        self.structure_transform = self._get_structure_transform()

        # Prepare labels
        self.id2label = self.detection_model.config.id2label
        self.id2label[len(self.id2label)] = "no object"
        
        self.structure_id2label = self.structure_model.config.id2label
        self.structure_id2label[len(self.structure_id2label)] = "no object"
        print("Initialization complete.")

    # Helper methods are now part of the class
    def _get_detection_transform(self):
        return transforms.Compose([
            MaxResize(800),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _get_structure_transform(self):
        return transforms.Compose([
            MaxResize(1000),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _box_cxcywh_to_xyxy(self, x):
        x_c, y_c, w, h = x.unbind(-1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
        return torch.stack(b, dim=1)

    def _rescale_bboxes(self, out_bbox, size):
        img_w, img_h = size
        b = self._box_cxcywh_to_xyxy(out_bbox)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b

    def _outputs_to_objects(self, outputs, img_size, id2label_map):
        m = outputs.logits.softmax(-1).max(-1)
        pred_labels = list(m.indices.detach().cpu().numpy())[0]
        pred_scores = list(m.values.detach().cpu().numpy())[0]
        pred_bboxes = outputs['pred_boxes'].detach().cpu()[0]
        pred_bboxes = [elem.tolist() for elem in self._rescale_bboxes(pred_bboxes, img_size)]

        objects = []
        for label, score, bbox in zip(pred_labels, pred_scores, pred_bboxes):
            class_label = id2label_map[int(label)]
            if not class_label == 'no object':
                objects.append({'label': class_label, 'score': float(score),
                                'bbox': [float(elem) for elem in bbox]})
        return objects

    def _get_cell_coordinates_by_row(self, table_data):
        rows = [entry for entry in table_data if entry['label'] == 'table row']
        columns = [entry for entry in table_data if entry['label'] == 'table column']
        rows.sort(key=lambda x: x['bbox'][1])
        columns.sort(key=lambda x: x['bbox'][0])
        
        cell_coordinates = []
        for row in rows:
            row_cells = []
            for column in columns:
                cell_bbox = [column['bbox'][0], row['bbox'][1], column['bbox'][2], row['bbox'][3]]
                row_cells.append({'column': column['bbox'], 'cell': cell_bbox})
            row_cells.sort(key=lambda x: x['column'][0])
            cell_coordinates.append({'row': row['bbox'], 'cells': row_cells, 'cell_count': len(row_cells)})
        cell_coordinates.sort(key=lambda x: x['row'][1])
        return cell_coordinates

    def _apply_ocr(self, cell_coordinates, cropped_table) -> tuple[dict, list]:
        """
        Applies OCR to each cell and returns the extracted data and a list of
        all OCR confidence scores.
        """
        data = {}
        ocr_confidence_scores = []
        max_num_columns = 0

        for idx, row in enumerate(tqdm(cell_coordinates)):
            row_text = []
            for cell in row["cells"]:
                cell_image = np.array(cropped_table.crop(cell["cell"]))
                result = self.ocr_reader.readtext(cell_image)
                
                if result:
                    text = " ".join([res[1] for res in result])
                    confidence_scores = [res[2] for res in result]
                    row_text.append(text)
                    ocr_confidence_scores.extend(confidence_scores)
                else:
                    row_text.append("")

            if len(row_text) > max_num_columns:
                max_num_columns = len(row_text)
            data[idx] = row_text
        
        for row, row_data in data.items():
            data[row] = row_data + [""] * (max_num_columns - len(row_data))
            
        # This is the crucial line. Ensure it only returns two items.
        return data, ocr_confidence_scores

    # This is the main method you will call from your API
    def extract_table(self, image: Image.Image) -> dict:
        """
        This method now extracts raw data, calculates the overall confidence,
        and returns them together in a single dictionary.
        """
        all_confidence_scores = []

        # 1. Detect tables
        pixel_values = self.detection_transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.detection_model(pixel_values)
        
        tables = self._outputs_to_objects(outputs, image.size, self.id2label)
        if not tables:
            return {"data": {}, "confidence": 0.0, "error": "No tables detected."}
        all_confidence_scores.extend([obj['score'] for obj in tables])

        # 2. Crop table and recognize structure
        table_bbox = tables[0]['bbox']
        cropped_table = image.crop(table_bbox)
        pixel_values = self.structure_transform(cropped_table).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.structure_model(pixel_values)
        cells = self._outputs_to_objects(outputs, cropped_table.size, self.structure_id2label)
        all_confidence_scores.extend([obj['score'] for obj in cells])

        # 3. Apply OCR and get scores
        cell_coordinates = self._get_cell_coordinates_by_row(cells)
        data, ocr_scores = self._apply_ocr(cell_coordinates, cropped_table)
        all_confidence_scores.extend(ocr_scores)
        
        # 4. Calculate Overall Confidence
        overall_confidence = (sum(all_confidence_scores) / len(all_confidence_scores)) if all_confidence_scores else 0.0
        
        # --- THIS IS THE CHANGE ---
        # 5. Structure the final output as a single dictionary
        final_output = {
            "data": {str(k): v for k, v in data.items()}, # The extracted table data
            "confidence": round(overall_confidence, 4)   # The calculated score
        }
        
        # 6. Return the single dictionary
        return final_output

    def clean_and_normalize_report(self, raw_data: dict) -> dict:
        """
        Cleans, filters, and normalizes a lab report from a JSON object.

        It strictly enforces a rule: a row is only kept if it contains
        a text parameter, a numeric result, and a reference range.
        All other rows are eliminated.
        """
            # --- Step 1: Define the Rules (Regex) ---
        result_regex = re.compile(r'^(\d+\.?\d*)\s*.*$')
        # A string that CONTAINS a number-hyphen-number pattern
        range_regex = re.compile(r'\d+\.?\d*(\s*-\s*|\s+)\d+\.?\d*')

        # --- Step 2: Filter for Valid Rows Only ---
        valid_rows = []
        for key, row_list in raw_data['data'].items():
            # A valid row must not be empty and have at least a parameter
            if not row_list or not row_list[0].strip():
                continue

            # Check if the row contains one of each required component
            has_result = any(result_regex.fullmatch(cell.strip()) for cell in row_list)
            has_range = any(range_regex.search(cell.strip()) for cell in row_list)
            
            # The first item is assumed to be the parameter.
            # If all three components are found, keep the row.
            if has_result and has_range:
                valid_rows.append(row_list)

        # --- Step 3: Process the Filtered Rows ---
        final_report = {}
        for i, row in enumerate(valid_rows):
            parameter = row[0].strip()
            result_str = ""
            range_str = ""

            for cell in row[1:]:
                cell = cell.strip()
                if range_regex.search(cell):
                    range_str = cell
                elif result_regex.search(cell):
                    result_str = cell
            
            status = "Undetermined"
            
            try:
                result_num_match = re.search(r'\d+\.?\d*', result_str)
                result_val = float(result_num_match.group(0))

                range_numbers = re.findall(r'\d+\.?\d*', range_str)
                
                if len(range_numbers) == 2:
                    lower_bound = float(range_numbers[0])
                    upper_bound = float(range_numbers[1])
                    
                    if lower_bound <= result_val <= upper_bound:
                        status = "Normal"
                    elif result_val > upper_bound:
                        status = "High"
                    else:
                        status = "Low"
            except (ValueError, IndexError, AttributeError):
                status = "Undetermined"
                
            final_report[str(i)] = {
                "parameter": parameter,
                "results": result_str,
                "range": range_str,
                "status": status
            }
        return final_report
    

    def process_image(self, image: Image.Image, confidence_threshold: float = 0.5) -> dict:
        """
        This is the new main entry point. It orchestrates the entire pipeline.
        """
        # Step 1: Extract the raw data and the confidence score.
        raw_data = self.extract_table(image)
        confidence = raw_data.get("confidence", 0.0)
        if float(confidence) < float(confidence_threshold):
            return {
                "error": "Picture not clear enough to extract details.",
                "confidence": round(confidence, 4)
            }

        # Step 3: If confidence is high enough, clean and normalize the data.
        normalized_data = self.clean_and_normalize_report(raw_data)
        
        # Step 4: Return the final, structured output.
        final_output = {
            "data": normalized_data,
            "normalization confidence": round(confidence, 4)
        }
        
        return final_output



# # This block allows you to test the code directly
# if __name__ == '__main__':

#     extractor = TableExtractor()

#     image_path = "/home/giri/plum/assets/report2.png"  # Replace with a valid image path
#     extracted_data = extractor.extract_table(image_path)
    
#     # Print the results
#     for row, row_data in extracted_data.items():
#         print(row_data)






