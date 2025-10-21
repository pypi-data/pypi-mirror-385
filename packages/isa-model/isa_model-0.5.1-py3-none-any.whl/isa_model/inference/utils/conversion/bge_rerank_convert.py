import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path

def convert_bge_to_onnx(save_dir: str):
    """Convert BGE reranker to ONNX format"""
    try:
        # Create save directory if it doesn't exist
        save_dir = Path(save_dir).resolve()  # Get absolute path
        save_dir.mkdir(parents=True, exist_ok=True)
        
        model_name = "BAAI/bge-reranker-v2-m3"
        save_path = str(save_dir / "model.onnx")  # Convert to string for absolute path
        
        print(f"Loading model {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.eval()
        
        # Save tokenizer for later use
        print("Saving tokenizer...")
        tokenizer.save_pretrained(save_dir)
        
        # Create dummy input
        print("Creating dummy input...")
        dummy_input = tokenizer(
            [["what is panda?", "The giant panda is a bear species."]], 
            padding=True, 
            truncation=True, 
            return_tensors='pt',
            max_length=512
        )
        
        # Export to ONNX with external data storage
        print(f"Exporting to ONNX: {save_path}")
        torch.onnx.export(
            model,
            (dummy_input['input_ids'], dummy_input['attention_mask']),
            save_path,  # Using string absolute path
            input_names=['input_ids', 'attention_mask'],
            output_names=['logits'],
            dynamic_axes={
                'input_ids': {0: 'batch', 1: 'sequence'},
                'attention_mask': {0: 'batch', 1: 'sequence'},
                'logits': {0: 'batch'}
            },
            opset_version=16,
            export_params=True,  # Export the trained parameter weights
            do_constant_folding=True,  # Optimize constant-folding
            verbose=True,
            use_external_data_format=True  # Enable external data storage
        )
        print("Conversion completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    # Get the absolute path to the model directory
    current_dir = Path(__file__).parent.parent
    model_dir = current_dir / "model_converted" / "bge-reranker-v2-m3"
    
    success = convert_bge_to_onnx(str(model_dir))
    if success:
        print(f"Model saved to: {model_dir}")
        print("Files created:")
        for file in model_dir.glob('*'):
            print(f"- {file.name}")
    else:
        print("Conversion failed!")