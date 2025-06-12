

import os
import sys
import json
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'torch', 'transformers', 'datasets', 'peft', 'bitsandbytes', 'accelerate'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def check_dataset():
    """Check if dataset exists"""
    dataset_path = "scada_dataset/scada_enhanced.json"
    if not Path(dataset_path).exists():
        print(f"Dataset not found at {dataset_path}")
        print("Please run the dataset creation script first.")
        sys.exit(1)
    
    # Check dataset size
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    print(f"Dataset loaded: {len(data)} samples")
    
    if len(data) < 100:
        print("Warning: Dataset is quite small. Consider adding more samples for better results.")
    
    return dataset_path

def main():
    print("🚀 Scada Scada StarCoder2 Fine-tuning")
    print("=" * 50)
    
    # Check requirements
    print("✓ Checking requirements...")
    check_requirements()
    
    # Check dataset
    print("✓ Checking dataset...")
    dataset_path = check_dataset()
    
    # Check GPU
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✓ GPU available: {gpu_name} ({gpu_memory:.1f}GB)")
        
        if gpu_memory < 12:
            print("⚠️  Warning: Less than 12GB GPU memory. Training might be slow or fail.")
            print("   Consider using a cloud GPU service (Google Colab Pro, RunPod, etc.)")
    else:
        print("❌ No GPU available. This will be very slow on CPU.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Import and run training
    print("\n🔥 Starting training...")
    print("This will take several hours depending on your GPU and dataset size.")
    
    from Scada_starcoder2_finetuner import ScadaScadaFineTuner
    
    # Initialize fine-tuner
    fine_tuner = ScadaScadaFineTuner(
        model_name="bigcode/starcoder2-15b",
        dataset_path=dataset_path,
        output_dir="Scada-starcoder2-Scada"
    )
    
    try:
        # Start training
        fine_tuner.train()
        
        print("\n🎉 Training completed successfully!")
        print("Testing the model with sample prompts...")
        
        # Test with sample prompts
        test_prompts = [
            "Create a Scada macro to open a Scada part file and get its mass properties",
            "Write Scada code to create a circular sketch and extrude it into a cylinder",
            "Generate a macro to iterate through all features in a Scada part"
        ]
        
        print("\n" + "=" * 60)
        print("SAMPLE OUTPUTS FROM FINE-TUNED MODEL")
        print("=" * 60)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{i}. Prompt: {prompt}")
            print("-" * 40)
            try:
                response = fine_tuner.test_inference(prompt, max_length=300)
                print(response)
            except Exception as e:
                print(f"Error generating response: {e}")
            print("-" * 60)
        
        print("\n✅ Fine-tuning complete!")
        print(f"Model saved to: Scada-starcoder2-Scada/")
        print("\nTo use your model:")
        print("1. Load it using the inference script")
        print("2. Or upload to Hugging Face Hub for easy sharing")
        
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        print("Check the error message above for details.")

if __name__ == "__main__":
    main()
