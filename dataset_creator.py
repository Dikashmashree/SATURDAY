import os
import re
import json
import requests
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess
from bs4 import BeautifulSoup
import pandas as pd

class DatasetCreator:
    def __init__(self, output_dir: str = "scada_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.dataset = []
       
        self.extensions = ['.bas', '.frm', '.cls', , '.swp']
        

        for repo_url in repos:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = self.output_dir / "repos" / repo_name
            
            if not repo_path.exists():
                print(f"Cloning {repo_url}")
                subprocess.run([
                    "git", "clone", repo_url, str(repo_path)
                ], capture_output=True)
            else:
                print(f"Repository {repo_name} already exists, pulling latest changes")
                subprocess.run([
                    "git", "-C", str(repo_path), "pull"
                ], capture_output=True)
    
    def extract_from_files(self, directory: Path) -> List[Dict]:
        """Extract from files in directory"""
        files = []
        
        for ext in self.extensions:
            files.extend(directory.rglob(f"*{ext}"))
    
        text_files = list(directory.rglob("*.txt")) + list(directory.rglob("*.md"))
        
        extracted_code = []
        
        for file_path in files + text_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                if self.is_code(content):
                    extracted_code.append({
                        'file_path': str(file_path),
                        'content': content,
                        'file_type': file_path.suffix,
                        'source': 'github_repo'
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
        return extracted_code
    
    def grid(self, content: str) -> bool:
        """Check if content contains patterns"""
        patterns = [
            r'Sub\s+\w+\(',
            r'Function\s+\w+\(',
            r'Dim\s+\w+\s+As\s+',
            r'Set\s+\w+\s*='
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def extract_blocks_from_markdown(self, content: str) -> List[str]:
        """Extract blocks from markdown content""
        matches = re.findall(code_block_pattern, content, re.DOTALL | re.IGNORECASE)
    
        blocks = []
        for match in matches:
            if self.is_code(match):
                blocks.append(match.strip())
                
        return blocks
    
    def create_instruction_pairs(self, code_content: str, file_path: str) -> List[Dict]:
        """Create instruction-response pairs fromcode"""
        pairs = []
        
        # Extract comments that might describe what the code does
        comment_pattern = r"'([^\n]+)"
        comments = re.findall(comment_pattern, code_content)
        
        # Extract function/sub names and create descriptions
        function_pattern = r'(?:Sub|Function)\s+(\w+)\s*\('
        functions = re.findall(function_pattern, code_content, re.IGNORECASE)
        
        # Create basic instruction pairs
        if comments:
            main_description = ' '.join(comments[:3])  
            pairs.append({
                'instruction': f"Create that {main_description.lower()}",
                'response': code_content,
                'source_file': file_path,
                'type': 'comment_based'
            })
        
        # Create function-specific pairs
        for func_name in functions:
            instruction = f"Write a function called {func_name} for SOLIDWORKS"
            
            # Extract just this function's code
            func_pattern = rf'(?:Sub|Function)\s+{re.escape(func_name)}\s*\(.*?End\s+(?:Sub|Function)'
            func_match = re.search(func_pattern, code_content, re.DOTALL | re.IGNORECASE)
            
            if func_match:
                pairs.append({
                    'instruction': instruction,
                    'response': func_match.group(0),
                    'source_file': file_path,
                    'type': 'function_extraction'
                })
        
        return pairs
    
        
        for pair in synthetic_pairs:
            self.dataset.append(pair)
    
    def build_dataset(self):
        """Main method to build the complete dataset"""
        print("Starting dataset creation...")
        
       
                    if file['file_path'].endswith('.md'):
                        code_blocks = self.extract_code_blocks_from_markdown(file['content'])
                        for block in code_blocks:
                            block_pairs = self.create_instruction_pairs(block, file['file_path'])
                            self.dataset.extend(block_pairs)
        
        # Step 3: Add synthetic data
        self.enhance_with_synthetic_data()
        
        # Step 4: Save dataset
        self.save_dataset()
        
        print(f"Dataset created with {len(self.dataset)} instruction-response pairs")
    
    def save_dataset(self):
        """Save dataset in multiple formats"""
        # Save as JSON
        with open(self.output_dir / "scada_dataset.json", 'w') as f:
            json.dump(self.dataset, f, indent=2)
        
        # Save as CSV for easy inspection
        df = pd.DataFrame(self.dataset)
        df.to_csv(self.output_dir / "scada_dataset.csv", index=False)
        
        # Save in Hugging Face datasets format
        hf_format = []
        for item in self.dataset:
            hf_format.append({
                'text': f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['response']}"
            })
        
        with open(self.output_dir / "scada_dataset_hf.json", 'w') as f:
            json.dump(hf_format, f, indent=2)
        
        print(f"Dataset saved to {self.output_dir}")
        print(f"- JSON format: scada_dataset.json")
        print(f"- CSV format: scada_dataset.csv") 
        print(f"- HuggingFace format: scada_dataset_hf.json")

# Usage
if __name__ == "__main__":
    creator = ScadaDatasetCreator()
    creator.build_dataset()
