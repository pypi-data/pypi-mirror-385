"""Automatic code style correction using Google Gemini AI.

This module provides functionality to automatically format Python code according to
a style guide using Google's Gemini AI models. It can:
- Read a style guide and target code file
- Send code to Gemini for formatting suggestions
- Parse AI responses with modified code and explanations
- Generate unified diffs showing changes
- Optionally apply changes to the original file

The script uses structured delimiters to parse AI responses and generate
comprehensive diffs with explanations.

Example:
    $ python auto_gemini_styleguide.py target_file.py --styleguide .gemini/styleguide.md
    $ python auto_gemini_styleguide.py target_file.py --no-modify  # Generate diff only

Co-author: Gemini Code Assist
"""

import argparse
import difflib  # For generating diffs
import logging
import os
import pathlib

import google.api_core.exceptions  # Added: For GoogleAPICallError
import google.generativeai as genai
import google.generativeai.types  # Added: For BlockedPromptException
from dotenv import load_dotenv

from coffee_maker.config.manager import APIKeyMissingError, ConfigManager

# --- Configuration ---
# Relative path to the style guide from the script's location or project root
DEFAULT_STYLEGUIDE_PATH = ".gemini/styleguide.md"
# Relative path to the .env file
DEFAULT_ENV_FILE_PATH = ".env"
# Environment variable name for the API key
API_KEY_ENV_VAR = "COFFEE_MAKER_GEMINI_API_KEY"  # As per your preference

# Delimiters for parsing LLM response
MODIFIED_CODE_DELIMITER_START = "---MODIFIED_CODE_START---"
MODIFIED_CODE_DELIMITER_END = "---MODIFIED_CODE_END---"
EXPLANATIONS_DELIMITER_START = "---EXPLANATIONS_START---"
EXPLANATIONS_DELIMITER_END = "---EXPLANATIONS_END---"


def load_api_key(env_file_path: str, let_load_dotenv_search: bool = True) -> str | None:
    """Loads the Google API key from .env file or environment variables using ConfigManager.

    ConfigManager automatically checks multiple environment variable names:
    - GEMINI_API_KEY (primary)
    - GOOGLE_API_KEY (alternative)
    - COFFEE_MAKER_GEMINI_API_KEY (project-specific)

    Args:
        env_file_path (str): The path to the .env file.
        let_load_dotenv_search (bool): If True, and key not found via `env_file_path`,
                                        `load_dotenv()` will search default locations.

    Returns:
        str | None: The API key if found, otherwise None.
    """
    # Load .env file if it exists (for other environment variables)
    if pathlib.Path(env_file_path).is_file():
        logging.info(f"Sourcing environment variables from '{env_file_path}'...")
        load_dotenv(dotenv_path=env_file_path, override=True)
    else:
        logging.info(f"Info: Environment file '{env_file_path}' not found. Checking system environment variables.")

    # Try to get API key using ConfigManager (checks multiple variable names)
    try:
        api_key = ConfigManager.get_gemini_api_key(required=True)
        logging.info("Gemini API key loaded successfully from environment")
        return api_key
    except APIKeyMissingError:
        # If not found, try load_dotenv() search
        if let_load_dotenv_search and load_dotenv():
            try:
                api_key = ConfigManager.get_gemini_api_key(required=True)
                logging.info("Gemini API key loaded successfully from .env file")
                return api_key
            except APIKeyMissingError:
                logging.error(
                    "API key not found. Tried GEMINI_API_KEY, GOOGLE_API_KEY, and COFFEE_MAKER_GEMINI_API_KEY. "
                    f"Please set one of these in '{env_file_path}' or your environment."
                )
                logging.info("You can get an API key from Google AI Studio (https://aistudio.google.com/app/apikey).")
                return None
        else:
            logging.error(
                "API key not found. Tried GEMINI_API_KEY, GOOGLE_API_KEY, and COFFEE_MAKER_GEMINI_API_KEY. "
                f"Please set one of these in '{env_file_path}' or your environment."
            )
            logging.info("You can get an API key from Google AI Studio (https://aistudio.google.com/app/apikey).")
            return None


def read_file_content(file_path: str) -> str | None:
    """Read and return the complete content of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File content as string, or None if file not found or read error occurs

    Example:
        >>> content = read_file_content("example.py")
        >>> if content:
        ...     print(f"Read {len(content)} characters")
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Error: File not found at '{file_path}'.")
        return None
    except Exception as e:
        logging.exception(f"Error reading file '{file_path}': {e}")
        return None


def write_file_content(file_path: str, content: str) -> bool:
    """Write content to a file, overwriting existing content.

    Args:
        file_path: Path to the file to write
        content: String content to write to the file

    Returns:
        True if write succeeded, False if an error occurred

    Example:
        >>> success = write_file_content("output.txt", "Hello, World!")
        >>> if success:
        ...     print("File written successfully")
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Successfully updated '{file_path}'.")
        return True
    except Exception as e:
        logging.exception(f"Error writing to file '{file_path}': {e}")
        return False


def construct_llm_prompt(style_guide_content: str, code_to_modify: str, file_name: str) -> str:
    """Construct the LLM prompt for code formatting with structured output.

    Creates a detailed prompt that instructs the LLM to format code according to
    a style guide and return results with specific delimiters for parsing.

    Args:
        style_guide_content: Complete text of the style guide in markdown format
        code_to_modify: Source code to be formatted
        file_name: Name of the file being formatted (for context)

    Returns:
        Complete prompt string ready to send to the LLM

    Example:
        >>> prompt = construct_llm_prompt(
        ...     "# Style Guide\\n- Use 4 spaces",
        ...     "def foo():\\n  pass",
        ...     "example.py"
        ... )
        >>> print(prompt[:50])  # First 50 chars of prompt
    """
    prompt = f"""You are an expert code formatting and styling assistant.
Your task is to take the provided code snippet and reformat/restyle it to adhere (with minimal changes : don't change the code logic) to the rules outlined in the "STYLE GUIDE" below.
The code is from the file named '{file_name}'.

Your response MUST be structured in two parts, using the exact delimiters provided:

Part 1: The Modified Code
Begin this part with the delimiter "{MODIFIED_CODE_DELIMITER_START}" on a new line.
Provide ONLY the fully modified code. Do not include any explanations, apologies, or introductory sentences within this code block.
End this part with the delimiter "{MODIFIED_CODE_DELIMITER_END}" on a new line.

Part 2: Explanations for Changes
Begin this part with the delimiter "{EXPLANATIONS_DELIMITER_START}" on a new line.
List the significant changes you made to the code and briefly explain why each change was made, referencing the "STYLE GUIDE" rules where applicable.
If no changes were made, state "No changes were necessary."
End this part with the delimiter "{EXPLANATIONS_DELIMITER_END}" on a new line.

Example of your response structure:
{MODIFIED_CODE_DELIMITER_START}
# ... your modified code here ...
{MODIFIED_CODE_DELIMITER_END}
{EXPLANATIONS_DELIMITER_START}
- Line X: Changed Y to Z because of style guide rule A.1 (e.g., line length).
- Line Y: Refactored function F for clarity as per style guide section B (e.g., readability).
{EXPLANATIONS_DELIMITER_END}

STYLE GUIDE:
---
{style_guide_content}
---

ORIGINAL CODE from '{file_name}':
---
{code_to_modify}
---

Now, provide your response following the structure above.
"""
    return prompt


def parse_llm_response(llm_full_response: str) -> tuple[str | None, str | None]:
    """Parses the LLM's response to extract modified code and explanations."""
    modified_code = None
    explanations = None
    logging.debug(f"PARSER: Received LLM response length: {len(llm_full_response)}")

    try:
        # Find the primary delimiters that separate the main sections
        idx_code_start_delimiter = llm_full_response.find(MODIFIED_CODE_DELIMITER_START)
        idx_explanation_start_delimiter = llm_full_response.find(EXPLANATIONS_DELIMITER_START)
        idx_explanation_end_delimiter = llm_full_response.find(EXPLANATIONS_DELIMITER_END)

        # --- Extract Explanations First ---
        # This is often more straightforward if the AI terminates it correctly.
        if (
            idx_explanation_start_delimiter != -1
            and idx_explanation_end_delimiter != -1
            and idx_explanation_start_delimiter < idx_explanation_end_delimiter
        ):
            start_of_explanation_payload = idx_explanation_start_delimiter + len(EXPLANATIONS_DELIMITER_START)
            explanations = llm_full_response[start_of_explanation_payload:idx_explanation_end_delimiter].strip()
        elif idx_explanation_start_delimiter != -1:  # Start found, but no end
            logging.warning(
                f"PARSER: Found '{EXPLANATIONS_DELIMITER_START}' but no matching '{EXPLANATIONS_DELIMITER_END}'. Explanation block might be unterminated."
            )
            explanations = llm_full_response[
                idx_explanation_start_delimiter + len(EXPLANATIONS_DELIMITER_START) :
            ].strip()  # Take to end
        else:
            logging.debug(  # Changed to debug, as this is expected for malformed
                f"PARSER: Could not find explanation block delimiters ('{EXPLANATIONS_DELIMITER_START}', '{EXPLANATIONS_DELIMITER_END}')."
            )

        # --- Extract Modified Code ---
        if idx_code_start_delimiter != -1:
            start_of_code_payload = idx_code_start_delimiter + len(MODIFIED_CODE_DELIMITER_START)
            end_of_ai_code_block_boundary = -1

            if idx_explanation_start_delimiter != -1 and idx_explanation_start_delimiter > start_of_code_payload:
                # Code ends right before explanations start
                end_of_ai_code_block_boundary = idx_explanation_start_delimiter
            else:
                # No explanation block after code start, or malformed.
                # Look for the AI's intended MODIFIED_CODE_DELIMITER_END after the code start.
                end_of_ai_code_block_boundary = llm_full_response.rfind(
                    MODIFIED_CODE_DELIMITER_END, start_of_code_payload
                )
                if end_of_ai_code_block_boundary == -1:  # MCE not found after MCS
                    # If no explanation start and no MCE after code start, assume code goes to end.
                    end_of_ai_code_block_boundary = len(llm_full_response)
                    logging.warning(
                        f"PARSER: No '{EXPLANATIONS_DELIMITER_START}' found after code, and no '{MODIFIED_CODE_DELIMITER_END}' found after code start. Assuming code extends to end of response."
                    )

            if start_of_code_payload < end_of_ai_code_block_boundary:
                # This segment is what the AI considers its code output, potentially ending with its own MODIFIED_CODE_DELIMITER_END
                ai_code_output_segment = llm_full_response[start_of_code_payload:end_of_ai_code_block_boundary]
                stripped_ai_code_segment = ai_code_output_segment.rstrip()

                # Now, remove the AI's *actual* MODIFIED_CODE_DELIMITER_END from the end of this segment
                if stripped_ai_code_segment.endswith(MODIFIED_CODE_DELIMITER_END):
                    modified_code = stripped_ai_code_segment[: -len(MODIFIED_CODE_DELIMITER_END)].strip()
                else:
                    logging.warning(
                        f"PARSER: AI's code output segment (len {len(stripped_ai_code_segment)}) did not end with '{MODIFIED_CODE_DELIMITER_END}'. "
                        f"Segment tail (last 50 chars): '{repr(stripped_ai_code_segment[-50:])}'. Using segment as is (after stripping)."
                    )
                    modified_code = stripped_ai_code_segment.strip()  # Use the segment as is, but stripped
            else:
                logging.warning(
                    f"PARSER: Code start payload index ({start_of_code_payload}) not before code end boundary ({end_of_ai_code_block_boundary}). Cannot extract code."
                )

        # --- Fallback for completely missing delimiters ---
        # If after all attempts, modified_code is still None and explanations is None,
        # and the original response wasn't empty, assume it's a completely malformed response
        # and treat the whole thing as code.
        if modified_code is None and explanations is None and llm_full_response.strip():
            all_delimiters_missing = all(
                delim not in llm_full_response
                for delim in [
                    MODIFIED_CODE_DELIMITER_START,
                    MODIFIED_CODE_DELIMITER_END,
                    EXPLANATIONS_DELIMITER_START,
                    EXPLANATIONS_DELIMITER_END,
                ]
            )
            if all_delimiters_missing:
                logging.warning("PARSER: No delimiters found anywhere. Treating entire response as modified code.")
                modified_code = llm_full_response.strip()
            else:
                # This case means some delimiters were found, but the structure didn't fit any parsing logic.
                # modified_code and explanations remain None.
                logging.warning("PARSER: Some delimiters found, but structure is unexpected. Cannot reliably parse.")

    except Exception as e:
        logging.exception(f"PARSER: Error during LLM response parsing: {e}")
        # Ensure None is returned on exception
        return None, None

    logging.debug(f"PARSER: Final modified_code (first 100): {repr(modified_code[:100]) if modified_code else 'None'}")
    logging.debug(f"PARSER: Final explanations (first 100): {repr(explanations[:100]) if explanations else 'None'}")
    return modified_code, explanations


def get_ai_suggestion(api_key: str, model_name: str, prompt: str) -> tuple[str | None, str | None]:
    """Calls the Gemini API and gets the modified code and explanations."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        logging.info(f"Sending request to Gemini model '{model_name}'...")

        generation_config = genai.types.GenerationConfig(candidate_count=1, temperature=0.1)

        response = model.generate_content(prompt, generation_config=generation_config)

        if not response.candidates or not response.candidates[0].content.parts:
            logging.error("Error: Model did not return any content.")
            if response.prompt_feedback:
                logging.info(f"Prompt Feedback: {response.prompt_feedback}")
            return None, None

        full_llm_output = response.text

        # --- DEBUGGING: Print raw LLM response ---
        logging.debug("\n" + "=" * 20 + " RAW LLM RESPONSE " + "=" * 20)
        logging.debug(f"Raw LLM Output Length: {len(full_llm_output)}")
        # logging.debug(full_llm_output) # Uncomment to see the full raw output if needed
        # For very detailed inspection of potential hidden characters:
        # logging.debug("Representation of RAW LLM response (first 500 chars):")
        # logging.debug(repr(full_llm_output[:500]))
        # logging.debug("Representation of RAW LLM response (last 500 chars):")
        # logging.debug(repr(full_llm_output[-500:]))
        logging.debug("=" * (40 + len(" RAW LLM RESPONSE ")) + "\n")
        # --- END DEBUGGING ---

        return parse_llm_response(full_llm_output)

    except google.generativeai.types.BlockedPromptException as bpe:
        logging.error(f"Gemini API Error: Prompt was blocked. {bpe}")
        # Potentially log bpe.response.prompt_feedback if available and relevant
        return None, None
    except google.api_core.exceptions.GoogleAPICallError as api_error:
        logging.error(f"Google API Call Error: {api_error}")
        # api_error often has structured details like api_error.code() or api_error.message
        return None, None
    except Exception as e:
        logging.exception(f"Unexpected error calling Gemini API: {e}")
        # Note: The specific Google API exceptions inherit from Exception, so this will catch them too,
        # but the more specific handlers above allow for different logging/handling if needed.
        # If you remove the specific handlers, this one will catch them.
        if hasattr(e, "response") and e.response:
            logging.error(f"API Response Status: {e.response.status_code}")
            logging.error(f"API Response Body: {e.response.text}")
        return None, None


def generate_and_write_diff(
    original_content: str, modified_content: str, target_file_path: str, explanations: str | None
) -> bool:
    """
    Generates a diff and writes it to a .diff.<filename> file if actual code changes exist.
    Explanations are included in the diff file if changes were made, or logged if no code changes.
    """
    original_filename = os.path.basename(target_file_path)
    diff_filename = f".diff.{original_filename}"
    diff_file_path = os.path.join(os.path.dirname(target_file_path), diff_filename)

    # Primary condition: Only create a diff file if code content has actually changed.
    # Use strip() to ignore leading/trailing whitespace differences
    if original_content.strip() == modified_content.strip():
        logging.info("Code content is identical to the original after stripping whitespace.")
        if explanations:
            # Log explanations, but do not create the diff file for the code.
            logging.info(f"AI provided explanations for no code change:\n{explanations}")
        else:
            logging.info("No explanations provided for identical code.")
        logging.info(f"Diff file '{diff_file_path}' will NOT be created as there are no actual code changes.")
        return True  # Operation considered successful, but no diff file generated for code.

    # If we reach here, original_content.strip() != modified_content.strip(), so there are changes.
    logging.info("Code content has changed. Generating diff file.")

    original_lines = original_content.splitlines(keepends=True)
    modified_lines = modified_content.splitlines(keepends=True)

    # Create a unified diff
    diff_generator = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"a/{original_filename}",
        tofile=f"b/{original_filename}",
        lineterm="",  # Avoids extra newlines if source lines already have them
    )

    diff_content_list = list(diff_generator)

    # Although we checked strip(), difflib might still produce an empty list if changes are only whitespace/newlines
    # or if there's some other subtle difference it doesn't represent in the diff format.
    # We should still write the file if we reached this point based on the strip() check,
    # but maybe add a note if the diff_content_list is empty unexpectedly.

    try:
        with open(diff_file_path, "w", encoding="utf-8") as f:
            f.write(f"# Diff for {original_filename} (AI Suggested Changes)\n")
            f.write("# Generated by auto_gemini_styleguide.py\n")
            f.write("-" * 30 + " GIT-STYLE UNIFIED DIFF " + "-" * 30 + "\n")

            if not diff_content_list:
                logging.warning(
                    "Difflib generated an empty diff list, but content comparison (strip) indicated a difference. This is unusual."
                )
                f.write("--- Difflib reported no changes, but content comparison (strip) differed. ---\n")
            else:
                for line in diff_content_list:
                    f.write(line)

            if explanations:
                f.write("\n\n" + "-" * 30 + " AI EXPLANATIONS FOR CHANGES " + "-" * 30 + "\n")
                f.write(explanations + "\n")
            else:
                f.write("\n\n" + "-" * 30 + " AI EXPLANATIONS FOR CHANGES " + "-" * 30 + "\n")
                f.write("No specific explanations were provided by the AI for these changes.\n")

        logging.info(f"Successfully wrote diff and explanations to '{diff_file_path}'.")
        return True
    except Exception as e:
        logging.exception(f"Error writing to diff file '{diff_file_path}': {e}")
        return False


def main():
    """Main function to autocorrect a file using Google AI and generate a diff."""
    # Configure logging at the beginning of main or at module level
    # Set level to DEBUG to see all parser logs and raw LLM response
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Autocorrects a file using Google AI according to a style guide and generates a diff with explanations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("target_file_path", help="The path to the Python file to autocorrect.")
    parser.add_argument(
        "--styleguide",
        default=DEFAULT_STYLEGUIDE_PATH,
        help=f"Path to the style guide markdown file (default: {DEFAULT_STYLEGUIDE_PATH}).",
    )
    parser.add_argument(
        "--envfile",
        default=DEFAULT_ENV_FILE_PATH,
        help=f"Path to the .env file for API key (default: {DEFAULT_ENV_FILE_PATH}).",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash-lite",
        help="The Gemini model to use (e.g., 'gemini-2.0-flash-lite', 'gemini-1.5-flash-latest', 'gemini-pro').",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create a backup of the original file (as .bak) before overwriting."
    )
    parser.add_argument(
        "--no-modify", action="store_true", help="Do not modify the original file. Only generate the .diff file."
    )
    # Added --debug argument to control logging level from CLI
    parser.add_argument("--debug", action="store_true", help="Enable debug logging for more verbose output.")

    args = parser.parse_args()

    # Set logging level based on --debug argument
    # This overrides the basicConfig level if --debug is not used
    # If --debug is used, basicConfig already set it to DEBUG
    if not args.debug:
        logging.getLogger().setLevel(logging.INFO)

    logging.info("--- AI Code Style Corrector & Differ ---")

    api_key = load_api_key(args.envfile)
    if not api_key:
        return 1

    logging.info(f"Reading style guide from: {args.styleguide}")
    style_guide_content = read_file_content(args.styleguide)
    if style_guide_content is None:
        return 1

    logging.info(f"Reading target file: {args.target_file_path}")
    original_code_content = read_file_content(args.target_file_path)
    if original_code_content is None:
        return 1

    if args.backup:
        backup_file_path = f"{args.target_file_path}.bak"
        logging.info(f"Creating backup: {backup_file_path}")
        if not write_file_content(backup_file_path, original_code_content):
            logging.warning("Warning: Failed to create backup. Proceeding cautiously.")

    prompt = construct_llm_prompt(style_guide_content, original_code_content, pathlib.Path(args.target_file_path).name)

    modified_code, explanations = get_ai_suggestion(api_key, args.model, prompt)

    if modified_code is not None:
        logging.info("--- AI Suggestion Received ---")

        # Decide if we should process changes (generate diff, potentially modify file)
        # Process if code changed OR if explanations were provided (even if code didn't change)
        should_process_changes = modified_code.strip() != original_code_content.strip() or bool(explanations)

        if should_process_changes:
            # generate_and_write_diff will now internally decide if a diff FILE is created
            # based on whether the code content actually changed.
            generate_and_write_diff(original_code_content, modified_code, args.target_file_path, explanations)

            if args.no_modify:
                logging.info(f"Original file '{args.target_file_path}' was NOT modified due to --no-modify flag.")
            elif modified_code.strip() == original_code_content.strip():
                # This case is hit if AI returned identical code but provided explanations.
                # generate_and_write_diff logged the explanations and skipped diff file creation.
                logging.info("AI returned identical code content. No changes made to the original file based on code.")
            else:
                # Code content actually changed, proceed with writing the modified file
                logging.info(f"Attempting to write AI modified code back to '{args.target_file_path}'...")
                logging.info("IMPORTANT: Please review the changes carefully after the script finishes.")
                if write_file_content(args.target_file_path, modified_code):
                    logging.info("Original file successfully updated with AI suggestions.")
                else:
                    logging.error("Failed to write modified code to the original file.")
                    return 1
        else:
            # modified_code is not None, but code is identical AND no explanations were provided.
            # This is the case where AI returned the exact same code and nothing else.
            logging.info("AI returned identical code content and no explanations. No changes made, no diff generated.")

        logging.info("Process completed.")
    else:
        # This means get_ai_suggestion returned (None, explanations) or (None, None)
        logging.error(
            "Failed to get a valid modified code block from the AI. No changes made to the file. No diff generated."
        )
        if explanations:  # If explanations were returned but code was None
            logging.info("AI provided explanations, but no valid code block was parsed:")
            logging.info("-" * 20 + " EXPLANATIONS " + "-" * 20)
            logging.info(explanations)  # Log the explanations
            logging.info("-" * (40 + len(" EXPLANATIONS ")) + "\n")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    exit_code = main()
    sys.exit(exit_code)
