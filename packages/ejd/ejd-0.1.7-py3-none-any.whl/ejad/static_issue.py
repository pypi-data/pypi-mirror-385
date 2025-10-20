import os
import sys
from dotenv import load_dotenv
from .gemini_integration import analyze_and_fix_code, test_connection

load_dotenv()

def fix_static_issue(file_path, rule_path=None, apply=False):
    """Fix static issue in the given file using rule set.

    Args:
        file_path: path to the source file
        rule_path: optional path to the rule set file; if provided it will be used
                   and the user will not be prompted. JSON rule files are validated.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found -> {file_path}")
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
        
        # Store both files for LLM processing
        # TODO: Send to LLM for analysis and fixing
        process_with_llm(source_code, rule_set_content, file_path, rule_set_path, apply=apply)

    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)

def process_with_llm(source_code, rule_set_content, source_path, rule_set_path, apply=False):
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
                # Get absolute path for better VS Code clickable link support
                abs_source_path = os.path.abspath(source_path)
                file_name = os.path.basename(source_path)
                
                for i, issue in enumerate(result['issues_found'], 1):
                    line_num = issue.get('line', 'N/A')
                    # Format as hyperlink for VS Code clickable links
                    if str(line_num).isdigit():
                        # VS Code supports vscode://file/ URI scheme with line numbers
                        # Format: vscode://file/PATH:LINE:COLUMN
                        # We also keep the file:// format with #L syntax as fallback
                        file_uri = f"vscode://file/{abs_source_path.replace(os.sep, '/')}:{line_num}"
                        link_text = f"{file_name}:{line_num}"
                        # OSC 8 format: ESC]8;;URI ESC\\ TEXT ESC]8;; ESC\\
                        location = f"\033]8;;{file_uri}\033\\{link_text}\033]8;;\033\\"
                    else:
                        location = f"Line {line_num}"
                    print(f"   {i}. {location}")
                    print(f"      {issue.get('description', 'No description')}")
                    print(f"      Type: {issue.get('type', 'N/A')} | Rule: {issue.get('rule', 'N/A')}")
            
            # Ask user if they want to create a fixed file
            if result.get('fixed_code') and result['fixed_code'] != source_code:
                print(f"\nPreview of fixed code (first 200 characters):")
                preview = result['fixed_code'][:200] + "..." if len(result['fixed_code']) > 200 else result['fixed_code']
                print(f"   {preview}")
                
                # First question: Do you want to create a new fixed file?
                while True:
                    create_fixed_file = input("\nDo you want to create a new file with the fixed code? (y/n): ").strip().lower()
                    if create_fixed_file in ['y', 'n']:
                        break
                    print("Please enter 'y' for yes or 'n' for no.")
                
                fixed_file_path = None
                if create_fixed_file == 'y':
                    # User chose 'y' - create the fixed file
                    # Create fixed file path
                    base_name = os.path.splitext(source_path)[0]
                    extension = os.path.splitext(source_path)[1]
                    fixed_file_path = f"{base_name}-fixed{extension}"

                    # Write the fixed code to new file
                    with open(fixed_file_path, 'w', encoding='utf-8') as f:
                        f.write(result['fixed_code'])

                    print(f"\n[OK] Fixed version created: {fixed_file_path}")
                    print(f"[OK] Original file preserved: {source_path}")
                else:
                    print("\n[INFO] Fixed file will not be created.")

                # If --apply was passed, automatically overwrite the original with the fixed file
                def _apply_fixed_content(fixed_path, target_path):
                    """Atomically write the content of fixed_path into target_path.

                    This reads the fixed file's text content and writes it to a temporary
                    file in the same directory, then replaces the original file with
                    os.replace to ensure an atomic swap on the same filesystem.
                    Returns a tuple (fixed_hash, new_orig_hash).
                    """
                    import tempfile
                    import os
                    import hashlib

                    dir_name = os.path.dirname(os.path.abspath(target_path)) or '.'
                    # Read fixed content as text (utf-8)
                    with open(fixed_path, 'r', encoding='utf-8') as fh:
                        fixed_text = fh.read()

                    # Write fixed content to a temp file in same directory
                    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_fixed_')
                    try:
                        with os.fdopen(fd, 'w', encoding='utf-8') as tmpf:
                            tmpf.write(fixed_text)

                        abs_target = os.path.abspath(target_path)
                        abs_tmp = os.path.abspath(tmp_path)
                        os.replace(abs_tmp, abs_target)

                        if not os.path.exists(abs_target):
                            raise RuntimeError(f"Failed to replace original file at {abs_target}")


                        # Compute sha256 hashes for both files (binary read)
                        def _sha256(path):
                            h = hashlib.sha256()
                            with open(path, 'rb') as fh2:
                                for chunk in iter(lambda: fh2.read(8192), b''):
                                    h.update(chunk)
                            return h.hexdigest()

                        fixed_hash = _sha256(fixed_path)
                        new_orig_hash = _sha256(target_path)
                        return fixed_hash, new_orig_hash
                    finally:
                        # Ensure temp file removed if something went wrong and still exists
                        try:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                        except Exception:
                            pass

                # Second question: Do you want to apply fixes to the original file?
                while True:
                    apply_answer = input("\nDo you want to apply these fixes to the original file? (y/n): ").strip().lower()
                    if apply_answer in ['y', 'n']:
                        break
                    print("Please enter 'y' for yes or 'n' for no.")
                
                if apply_answer == 'y':
                    try:
                        # If no fixed file was created, create a temporary one
                        if not fixed_file_path:
                            import tempfile
                            fd, fixed_file_path = tempfile.mkstemp(suffix=os.path.splitext(source_path)[1], prefix='tmp_fixed_')
                            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                                f.write(result['fixed_code'])
                        
                        fixed_hash, orig_hash = _apply_fixed_content(fixed_file_path, source_path)
                        print(f"\n[OK] Original file updated: {source_path}")
                        
                        # Clean up temporary file if it was created
                        if create_fixed_file == 'n' and fixed_file_path and os.path.exists(fixed_file_path):
                            try:
                                os.remove(fixed_file_path)
                            except Exception:
                                pass
                        
                        if result.get('summary'):
                            print(f"\nSummary: {result['summary']}")
                    except Exception as e:
                        print(f"\n[ERROR] Error applying fixed file to original: {e}")
                else:
                    if create_fixed_file == 'y':
                        print(f"\n[OK] Original file left unchanged: {source_path}")
                        print(f"You can review the fixed file at: {fixed_file_path}")
                    else:
                        print(f"\n[OK] No changes made. Original file unchanged: {source_path}")
                    
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
