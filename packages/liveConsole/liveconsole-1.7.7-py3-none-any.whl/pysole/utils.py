import os
import sys
import re

settingsPath = os.path.join(os.path.dirname(__file__), "settings.json")
themesPath = os.path.join(os.path.dirname(__file__), "themes.json")

def stdPrint(text):
    """Print text to the terminal."""
    try:
        sys.__stdout__.write(f"{text}\n")
        sys.__stdout__.flush()
    except:
        pass

def normalizeWhitespace(lines):
    """
    Normalize leading whitespace across a list of code lines.
    Removes common leading indentation and trims excess on over-indented lines.
    """
    
    if type(lines) == str:
        lines = lines.split('\n')

    # Remove empty lines and preserve original line endings
    strippedLines = [line.rstrip('\n') for line in lines if line.strip()]
    if not strippedLines:
        return []

    # Find minimum indentation across non-empty lines
    indentLevels = [
        len(re.match(r'^[ \t]*', line).group())
        for line in strippedLines
    ]
    minIndent = min(indentLevels)

    
    normalized = [line[minIndent:] if len(line) >= minIndent else line for line in lines]   #< Normalize by removing minIndent from each line
    return(normalized)

def findUnindentedLine(lines):
    for i, line in enumerate(lines):
        if re.match(r'^\S', line):  # Line starts with non-whitespace
            return(i)
    return(None)