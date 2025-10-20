import os
import sys
import shutil
from dotenv import load_dotenv
from .gemini_integration import analyze_and_fix_code, test_connection

load_dotenv()

def fix_static_issue(file_path, rule_path=None):
    """Fix static issue in the given file using rule set.

    Args:
        file_path: path to the source file
        rule_path: optional path to the rule set file; if provided it will be used
                   and the user will not be prompted. JSON rule files are validated.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found or not a file -> {file_path}")
        sys.exit(1)

    print(f"Processing file: {file_path}")
    # Helper to resolve paths and validate allowed extensions
    def _resolve_and_check_path(p):
        # Expand user (~) and make absolute relative to cwd
        p2 = os.path.expanduser(p)
        if not os.path.isabs(p2):
            p2 = os.path.abspath(os.path.join(os.getcwd(), p2))
        return p2

    allowed_exts = ('.txt', '.json')

    if rule_path:
        rule_set_path = _resolve_and_check_path(rule_path)
        if not os.path.isfile(rule_set_path):
            print(f"Error: Provided rule set file not found or not a file -> {rule_set_path}")
            sys.exit(1)
        _, ext = os.path.splitext(rule_set_path)
        if ext.lower() not in allowed_exts:
            print(f"Error: Unsupported rule file extension '{ext}'. Supported: {allowed_exts}")
            sys.exit(1)
    else:
        # Prompt user for rule set path (accept .txt or .json)
        while True:
            user_input = input("Please enter the path to the rule set file (.txt or .json): ").strip()
            if not user_input:
                print("Rule set path cannot be empty. Please try again.")
                continue

            rule_set_path = _resolve_and_check_path(user_input)

            if not os.path.isfile(rule_set_path):
                print(f"Error: Rule set file not found or not a file -> {rule_set_path}")
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Operation cancelled.")
                    sys.exit(1)
                continue

            _, ext = os.path.splitext(rule_set_path)
            if ext.lower() not in allowed_exts:
                print(f"Error: Unsupported rule file extension '{ext}'. Please provide a .txt or .json file.")
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Operation cancelled.")
                    sys.exit(1)
                continue

            break
    
    # Read both files into variables for LLM processing
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # If JSON, validate it first
        if rule_set_path.lower().endswith('.json'):
            import json

            try:
                with open(rule_set_path, 'r', encoding='utf-8') as f:
                    rule_text = f.read()
                # Validate JSON
                json.loads(rule_text)
                rule_set_content = rule_text
            except Exception as e:
                print(f" Error: Invalid JSON in rule set file -> {e}")
                sys.exit(1)
        else:
            with open(rule_set_path, 'r', encoding='utf-8') as f:
                rule_set_content = f.read()
            
        print(f"Successfully loaded:")
        print(f"   Source file: {file_path}")
        print(f"   Rule set: {rule_set_path}")
        
        process_with_llm(source_code, rule_set_content, file_path, rule_set_path)

    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)

def process_with_llm(source_code, rule_set_content, source_path, rule_set_path):
    """Process the source code and rule set with Gemini Flash 2.5."""
    print(f"Preparing to send data to Gemini Flash 2.5...")
    print(f"   Source code length: {len(source_code)} characters")
    print(f"   Rule set length: {len(rule_set_content)} characters")
    
    try:
        # Test connection first
        print("Testing connection to Gemini...")
        if not test_connection():
            print("Failed to connect to Gemini. Please check your API key.")
            return None
        
        print("Connected to Gemini successfully!")
        
        # Analyze and fix the code
        result = analyze_and_fix_code(source_code, rule_set_content, source_path)
        
        if result["status"] == "success":
            print("Analysis completed successfully!")
            print(f"Issues found: {len(result.get('issues_found', []))}")
            
            # Display report file location
            if result.get('report_path'):
                print(f"Detailed markdown report saved to: {result['report_path']}")
            
            # Display issues found
            if result.get('issues_found'):
                print("\nIssues identified:")
                # Create absolute path for clickable links
                abs_source_path = os.path.abspath(source_path)
                for i, issue in enumerate(result['issues_found'], 1):
                    line_num = issue.get('line', 'N/A')
                    description = issue.get('description', 'No description')
                    issue_type = issue.get('type', 'N/A')
                    rule = issue.get('rule', 'N/A')
                    
                    # Format as clickable link: file:line:column
                    if line_num != 'N/A':
                        clickable_link = f"{abs_source_path}:{line_num}:1"
                        print(f"   {i}. {clickable_link}")
                        print(f"      {description}")
                        print(f"      Type: {issue_type} | Rule: {rule}")
                    else:
                        print(f"   {i}. Line {line_num}: {description}")
                        print(f"      Type: {issue_type} | Rule: {rule}")
            
            # Create a -fixed file and then offer user a choice to apply fixes to the original file
            if result.get('fixed_code') and result['fixed_code'] != source_code:
                # Create fixed file path
                base_name = os.path.splitext(source_path)[0]
                extension = os.path.splitext(source_path)[1]
                fixed_file_path = f"{base_name}-fixed{extension}"

                # Write the fixed code to new file
                with open(fixed_file_path, 'w', encoding='utf-8') as f:
                    f.write(result['fixed_code'])

                print(f"\n✓ Fixed version created: {fixed_file_path}")
                print(f"✓ Original file preserved: {source_path}")
                print(f"\nTo apply fixes, run: ejd -si apply \"{source_path}\"")
                
                if result.get('summary'):
                    print(f"\nSummary: {result['summary']}")
            else:
                print("No fixes needed - your code looks good!")
            
            # Display suggestions
            if result.get('suggestions'):
                print("\nAdditional suggestions:")
                for i, suggestion in enumerate(result['suggestions'], 1):
                    print(f"   {i}. {suggestion}")
                    
        elif result["status"] == "partial_success":
            print("Partial success - received response but parsing had issues")
            if result.get('markdown_response'):
                print("Full markdown response from Gemini:")
                print("─" * 50)
                print(result.get('markdown_response', 'No response available'))
                print("─" * 50)
            
            # Try to show any parsed data
            if result.get('report_path'):
                print(f"Raw response saved to: {result['report_path']}")
            print("Please review the markdown content above for analysis results.")
            
        else:
            print(f"Analysis failed: {result.get('message', 'Unknown error')}")
            
        return result
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set your GOOGLE_API_KEY environment variable or create a .env file")
        return None
    except Exception as e:
        print(f"Unexpected error during Gemini processing: {e}")
        return None

def get_file_contents(file_path, rule_set_path):
    """Helper function to get both file contents for external use."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        with open(rule_set_path, 'r', encoding='utf-8') as f:
            rule_set_content = f.read()
            
        return {
            'source_code': source_code,
            'rule_set_content': rule_set_content,
            'source_path': file_path,
            'rule_set_path': rule_set_path
        }
    except Exception as e:
        raise Exception(f"Error reading files: {e}")

def apply_fixed_file(original_path):
    """Apply the -fixed version to the original file.
    
    Args:
        original_path: Path to the original file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Construct the -fixed file path
    base, ext = os.path.splitext(original_path)
    fixed_path = f"{base}-fixed{ext}"
    
    # Check if original file exists
    if not os.path.isfile(original_path):
        print(f"Error: Original file not found -> {original_path}")
        return False
    
    # Check if fixed file exists
    if not os.path.isfile(fixed_path):
        print(f"Error: Fixed file not found -> {fixed_path}")
        print(f"Expected to find: {fixed_path}")
        print("Run 'ejd -si fix <path>' first to create the fixed version.")
        return False
    
    try:
        print(f"Applying fixes from: {fixed_path}")
        print(f"To original file: {original_path}")
        
        # Overwrite original with fixed version
        shutil.copy2(fixed_path, original_path)
        print(f"✓ Successfully applied fixes to {original_path}")
        
        # Delete the fixed file
        os.remove(fixed_path)
        print(f"✓ Removed temporary file {fixed_path}")
        
        return True
        
    except Exception as e:
        print(f"Error applying fixes: {e}")
        return False
