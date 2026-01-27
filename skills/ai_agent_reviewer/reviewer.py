import os
import sys
import argparse
from pathlib import Path

# Add project root to path to import model
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

try:
    from model import get_model
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    print("Error: Could not import 'model' or 'langchain'. Make sure you are in the project environment.")
    sys.exit(1)

def load_skill_content():
    skill_path = Path(__file__).parent / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"SKILL.md not found at {skill_path}")
    with open(skill_path, "r", encoding="utf-8") as f:
        return f.read()

def review_content(target_path, review_type):
    # Load the target content
    target_file = Path(target_path)
    if not target_file.exists():
        return f"Error: File {target_path} not found."
    
    with open(target_file, "r", encoding="utf-8") as f:
        target_content = f.read()

    # Load the review framework
    framework = load_skill_content()

    # detailed instructions based on type
    if review_type == "architecture":
        focus_area = "1. AGENT ARCHITECTURE REVIEW"
    elif review_type == "prompt":
        focus_area = "2. PROMPT ENGINEERING AUDIT"
    else:
        focus_area = "the entire framework"

    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert AI Agent Reviewer & Optimizer.
        Your goal is to audit the provided content against the specific criteria defined in the "AI Agent Reviewer & Optimizer" framework.

        FRAMEWORK GUIDELINES:
        {framework}

        ---
        
        TASK:
        Perform a {review_type} review for the following content.
        Focus specifically on sections relevant to: {focus_area}.
        
        Use the checklists and metrics provided in the framework.
        Provide a structured report with:
        1. Executive Summary
        2. Detailed Analysis (referencing specific lines/sections)
        3. Scores (if applicable based on the framework)
        4. Red Flags identified
        5. Actionable Recommendations

        CONTENT TO REVIEW:
        {content}
        """
    )

    model = get_model(temperature=0.1)
    chain = prompt_template | model | StrOutputParser()

    print(f"Analyzing {target_file.name} for {review_type}...")
    result = chain.invoke({
        "framework": framework,
        "review_type": review_type,
        "focus_area": focus_area,
        "content": target_content
    })

    return result

def main():
    parser = argparse.ArgumentParser(description="AI Agent Reviewer & Optimizer Tool")
    parser.add_argument("file", help="Path to the file to review (code or prompt)")
    parser.add_argument("--type", choices=["architecture", "prompt", "general"], default="general", help="Type of review to perform")
    
    args = parser.parse_args()
    
    report = review_content(args.file, args.type)
    
    print("\n" + "="*40)
    print(f"REVIEW REPORT FOR: {args.file}")
    print("="*40 + "\n")
    print(report)

    # Save report
    output_filename = f"review_{Path(args.file).stem}_{args.type}.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {output_filename}")

if __name__ == "__main__":
    main()
