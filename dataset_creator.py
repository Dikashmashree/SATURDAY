import os
import re
import json
import requests
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess
from bs4 import BeautifulSoup
import pandas as pd

class SolidWorksVBADatasetCreator:
    def __init__(self, output_dir: str = "solidworks_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.dataset = []
        
        # VBA file extensions to look for
        self.vba_extensions = ['.bas', '.frm', '.cls', '.vba', '.swp']
        
    def clone_repositories(self):
        """Clone key GitHub repositories containing SOLIDWORKS VBA code"""
        repos = [
            "https://github.com/xarial/codestack.git",
            "https://github.com/BlueByteSystemsInc/SOLIDWORKSVBAMacros.git",
            "https://github.com/YuanRayChang/Solidworks_Macro_Tutorial.git",
            "https://github.com/codestackdev/solidworks-api-examples.git"
        ]
        
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
    
    def extract_vba_code_from_files(self, directory: Path) -> List[Dict]:
        """Extract VBA code from files in directory"""
        vba_files = []
        
        for ext in self.vba_extensions:
            vba_files.extend(directory.rglob(f"*{ext}"))
        
        # Also look for .txt and .md files that might contain VBA code
        text_files = list(directory.rglob("*.txt")) + list(directory.rglob("*.md"))
        
        extracted_code = []
        
        for file_path in vba_files + text_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Check if content contains VBA code patterns
                if self.is_vba_code(content):
                    extracted_code.append({
                        'file_path': str(file_path),
                        'content': content,
                        'file_type': file_path.suffix,
                        'source': 'github_repo'
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
        return extracted_code
    
    def is_vba_code(self, content: str) -> bool:
        """Check if content contains VBA code patterns"""
        vba_patterns = [
            r'Sub\s+\w+\(',
            r'Function\s+\w+\(',
            r'Dim\s+\w+\s+As\s+',
            r'Set\s+\w+\s*=',
            r'swApp\.',
            r'SldWorks\.',
            r'ModelDoc2',
            r'FeatureManager',
            r'SelectionMgr'
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in vba_patterns)
    
    def extract_code_blocks_from_markdown(self, content: str) -> List[str]:
        """Extract VBA code blocks from markdown content"""
        # Pattern for code blocks with vba, vb, or no language specified
        code_block_pattern = r'```(?:vba|vb|basic)?\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, content, re.DOTALL | re.IGNORECASE)
        
        # Filter matches that look like VBA code
        vba_blocks = []
        for match in matches:
            if self.is_vba_code(match):
                vba_blocks.append(match.strip())
                
        return vba_blocks
    
    def create_instruction_pairs(self, code_content: str, file_path: str) -> List[Dict]:
        """Create instruction-response pairs from VBA code"""
        pairs = []
        
        # Extract comments that might describe what the code does
        comment_pattern = r"'([^\n]+)"
        comments = re.findall(comment_pattern, code_content)
        
        # Extract function/sub names and create descriptions
        function_pattern = r'(?:Sub|Function)\s+(\w+)\s*\('
        functions = re.findall(function_pattern, code_content, re.IGNORECASE)
        
        # Create basic instruction pairs
        if comments:
            main_description = ' '.join(comments[:3])  # Use first 3 comments as description
            pairs.append({
                'instruction': f"Create a VBA macro that {main_description.lower()}",
                'response': code_content,
                'source_file': file_path,
                'type': 'comment_based'
            })
        
        # Create function-specific pairs
        for func_name in functions:
            instruction = f"Write a VBA function called {func_name} for SOLIDWORKS"
            
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
    
    def enhance_with_synthetic_data(self):
        """Create synthetic instruction-response pairs for common SOLIDWORKS operations"""
        synthetic_pairs = [
            {
                'instruction': "Create a VBA macro to open a SOLIDWORKS file",
                'response': '''Sub OpenFile()
    Dim swApp As SldWorks.SldWorks
    Dim swModel As SldWorks.ModelDoc2
    Dim fileName As String
    
    Set swApp = Application.SldWorks
    fileName = "C:\\temp\\part1.sldprt"
    
    Set swModel = swApp.OpenDoc6(fileName, swDocumentTypes_e.swDocPART, _
                                swOpenDocOptions_e.swOpenDocOptions_Silent, "", 0, 0)
    
    If swModel Is Nothing Then
        MsgBox "Failed to open file"
    End If
End Sub''',
                'source_file': 'synthetic',
                'type': 'synthetic'
            },
            {
                'instruction': "Write VBA code to create a sketch circle in SOLIDWORKS",
                'response': '''Sub CreateSketchCircle()
    Dim swApp As SldWorks.SldWorks
    Dim swModel As SldWorks.ModelDoc2
    Dim swSketchMgr As SldWorks.SketchManager
    
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    Set swSketchMgr = swModel.SketchManager
    
    ' Insert sketch
    swModel.InsertSketch2 True
    
    ' Create circle at origin with radius 0.05
    swSketchMgr.CreateCircleByRadius 0, 0, 0, 0.05
    
    ' Exit sketch
    swModel.InsertSketch2 True
End Sub''',
                'source_file': 'synthetic',
                'type': 'synthetic'
            }
        ]
        
        for pair in synthetic_pairs:
            self.dataset.append(pair)
    
    def build_dataset(self):
        """Main method to build the complete dataset"""
        print("Starting dataset creation...")
        
        # Step 1: Clone repositories
        self.clone_repositories()
        
        # Step 2: Extract VBA code from repositories
        repos_dir = self.output_dir / "repos"
        for repo_dir in repos_dir.iterdir():
            if repo_dir.is_dir():
                print(f"Processing repository: {repo_dir.name}")
                vba_files = self.extract_vba_code_from_files(repo_dir)
                
                for vba_file in vba_files:
                    # Create instruction pairs from the code
                    pairs = self.create_instruction_pairs(
                        vba_file['content'], 
                        vba_file['file_path']
                    )
                    self.dataset.extend(pairs)
                    
                    # Also extract code blocks from markdown files
                    if vba_file['file_path'].endswith('.md'):
                        code_blocks = self.extract_code_blocks_from_markdown(vba_file['content'])
                        for block in code_blocks:
                            block_pairs = self.create_instruction_pairs(block, vba_file['file_path'])
                            self.dataset.extend(block_pairs)
        
        # Step 3: Add synthetic data
        self.enhance_with_synthetic_data()
        
        # Step 4: Save dataset
        self.save_dataset()
        
        print(f"Dataset created with {len(self.dataset)} instruction-response pairs")
    
    def save_dataset(self):
        """Save dataset in multiple formats"""
        # Save as JSON
        with open(self.output_dir / "solidworks_vba_dataset.json", 'w') as f:
            json.dump(self.dataset, f, indent=2)
        
        # Save as CSV for easy inspection
        df = pd.DataFrame(self.dataset)
        df.to_csv(self.output_dir / "solidworks_vba_dataset.csv", index=False)
        
        # Save in Hugging Face datasets format
        hf_format = []
        for item in self.dataset:
            hf_format.append({
                'text': f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['response']}"
            })
        
        with open(self.output_dir / "solidworks_vba_dataset_hf.json", 'w') as f:
            json.dump(hf_format, f, indent=2)
        
        print(f"Dataset saved to {self.output_dir}")
        print(f"- JSON format: solidworks_vba_dataset.json")
        print(f"- CSV format: solidworks_vba_dataset.csv") 
        print(f"- HuggingFace format: solidworks_vba_dataset_hf.json")

# Usage
if __name__ == "__main__":
    creator = SolidWorksVBADatasetCreator()
    creator.build_dataset()