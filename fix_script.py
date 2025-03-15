import sys

with open("routes/resume.py", "r") as f:
    lines = f.readlines()

# Fix line 1974
lines[1973] = '        data = f"event: complete\\ndata: {json.dumps({\'message\': \'Test complete\'})}\\n\\n"\n'

# Add logging to api_save_customized_resume
target_line = 2149  # Line before original_content = ...
new_lines = [
    "        # Get original content if not provided\n",
    "        original_content = original_resume.original_content\n",
    "        if not original_content:\n",
    "            logger.warning(f\"Original content is empty for resume ID {resume_id}, this will cause comparison issues\")\n",
    "            \n",
    "        # Log the content lengths for debugging\n",
    "        logger.debug(f\"Original content length: {len(original_content) if original_content else 0}\")\n",
    "        logger.debug(f\"Customized content length: {len(customized_content) if customized_content else 0}\")\n",
]

# Replace line 2150 with our new lines
lines = lines[:target_line] + new_lines + lines[target_line+1:]

with open("routes/resume.py", "w") as f:
    f.writelines(lines)

print("File updated successfully") 