"""
Tag Manager
Handle inline formatting tags (bold, italic, underline)

This module converts formatting runs into XML-like tags for editing,
validates tag integrity, and reconstructs formatting on export.

Example:
    "This is **bold** text" → "This is <b>bold</b> text"
"""

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class FormattingRun:
    """Represents a formatting run in text"""
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    start_pos: int = 0
    end_pos: int = 0
    
    def has_formatting(self) -> bool:
        """Check if this run has any formatting"""
        return self.bold or self.italic or self.underline
    
    def get_tag_name(self) -> str:
        """Get the tag name for this formatting"""
        if self.bold and self.italic:
            return "bi"
        elif self.bold:
            return "b"
        elif self.italic:
            return "i"
        elif self.underline:
            return "u"
        return None


class TagManager:
    """Manage inline formatting tags"""
    
    # Tag patterns
    TAG_PATTERN = re.compile(r'<(/?)([biu]|bi)>')
    
    def __init__(self):
        self.tag_colors = {
            'b': '#CC0000',    # Red for bold
            'i': '#0066CC',    # Blue for italic
            'u': '#009900',    # Green for underline
            'bi': '#CC00CC'    # Purple for bold+italic
        }
    
    def extract_runs(self, paragraph) -> List[FormattingRun]:
        """
        Extract formatting runs from a python-docx paragraph
        
        Args:
            paragraph: python-docx paragraph object
            
        Returns:
            List of FormattingRun objects with position information
        """
        runs = []
        current_pos = 0
        
        for run in paragraph.runs:
            text = run.text
            if not text:
                continue
            
            run_info = FormattingRun(
                text=text,
                bold=run.bold or False,
                italic=run.italic or False,
                underline=run.underline or False,
                start_pos=current_pos,
                end_pos=current_pos + len(text)
            )
            runs.append(run_info)
            current_pos += len(text)
        
        return runs
    
    def runs_to_tagged_text(self, runs: List[FormattingRun]) -> str:
        """
        Convert formatting runs to tagged text
        
        Example:
            [Run("Hello ", bold=False), Run("world", bold=True), Run("!", bold=False)]
            → "Hello <b>world</b>!"
        
        Args:
            runs: List of FormattingRun objects
            
        Returns:
            Text with inline tags
        """
        if not runs:
            return ""
        
        result = []
        current_formatting = {'bold': False, 'italic': False, 'underline': False}
        
        for run in runs:
            # Determine what formatting changed
            formatting_changed = (
                run.bold != current_formatting['bold'] or
                run.italic != current_formatting['italic'] or
                run.underline != current_formatting['underline']
            )
            
            if formatting_changed:
                # Close previous tags
                if current_formatting['bold'] and current_formatting['italic']:
                    result.append('</bi>')
                elif current_formatting['bold']:
                    result.append('</b>')
                elif current_formatting['italic']:
                    result.append('</i>')
                elif current_formatting['underline']:
                    result.append('</u>')
                
                # Open new tags
                if run.bold and run.italic:
                    result.append('<bi>')
                elif run.bold:
                    result.append('<b>')
                elif run.italic:
                    result.append('<i>')
                elif run.underline:
                    result.append('<u>')
                
                # Update current state
                current_formatting['bold'] = run.bold
                current_formatting['italic'] = run.italic
                current_formatting['underline'] = run.underline
            
            result.append(run.text)
        
        # Close any remaining tags
        if current_formatting['bold'] and current_formatting['italic']:
            result.append('</bi>')
        elif current_formatting['bold']:
            result.append('</b>')
        elif current_formatting['italic']:
            result.append('</i>')
        elif current_formatting['underline']:
            result.append('</u>')
        
        return ''.join(result)
    
    def tagged_text_to_runs(self, text: str) -> List[Dict[str, Any]]:
        """
        Convert tagged text back to run specifications
        
        Example:
            "Hello <b>world</b>!" →
            [{'text': 'Hello ', 'bold': False},
             {'text': 'world', 'bold': True},
             {'text': '!', 'bold': False}]
        
        Args:
            text: Text with inline tags
            
        Returns:
            List of run specifications (dicts with text and formatting)
        """
        runs = []
        current_formatting = {'bold': False, 'italic': False, 'underline': False}
        current_text = []
        
        pos = 0
        while pos < len(text):
            # Check for tag
            match = self.TAG_PATTERN.match(text, pos)
            if match:
                # Save current text as a run
                if current_text:
                    runs.append({
                        'text': ''.join(current_text),
                        'bold': current_formatting['bold'],
                        'italic': current_formatting['italic'],
                        'underline': current_formatting['underline']
                    })
                    current_text = []
                
                # Process tag
                is_closing = match.group(1) == '/'
                tag_name = match.group(2)
                
                if tag_name == 'bi':
                    current_formatting['bold'] = not is_closing
                    current_formatting['italic'] = not is_closing
                elif tag_name == 'b':
                    current_formatting['bold'] = not is_closing
                elif tag_name == 'i':
                    current_formatting['italic'] = not is_closing
                elif tag_name == 'u':
                    current_formatting['underline'] = not is_closing
                
                pos = match.end()
            else:
                # Regular character
                current_text.append(text[pos])
                pos += 1
        
        # Save final text
        if current_text:
            runs.append({
                'text': ''.join(current_text),
                'bold': current_formatting['bold'],
                'italic': current_formatting['italic'],
                'underline': current_formatting['underline']
            })
        
        return runs
    
    def validate_tags(self, text: str) -> Tuple[bool, str]:
        """
        Validate that all tags are properly paired and nested
        
        Args:
            text: Text with inline tags
            
        Returns:
            (is_valid, error_message)
        """
        stack = []
        pos = 0
        
        while pos < len(text):
            match = self.TAG_PATTERN.match(text, pos)
            if match:
                is_closing = match.group(1) == '/'
                tag_name = match.group(2)
                
                if is_closing:
                    if not stack:
                        return False, f"Closing tag </{tag_name}> without opening tag"
                    if stack[-1] != tag_name:
                        return False, f"Mismatched tags: expected </{stack[-1]}>, found </{tag_name}>"
                    stack.pop()
                else:
                    stack.append(tag_name)
                
                pos = match.end()
            else:
                pos += 1
        
        if stack:
            return False, f"Unclosed tags: {', '.join(stack)}"
        
        return True, ""
    
    def count_tags(self, text: str) -> Dict[str, int]:
        """
        Count tags in text
        
        Returns:
            Dictionary with tag counts (e.g., {'b': 2, 'i': 1})
        """
        counts = {}
        pos = 0
        
        while pos < len(text):
            match = self.TAG_PATTERN.match(text, pos)
            if match:
                is_closing = match.group(1) == '/'
                if not is_closing:  # Only count opening tags
                    tag_name = match.group(2)
                    counts[tag_name] = counts.get(tag_name, 0) + 1
                pos = match.end()
            else:
                pos += 1
        
        return counts
    
    def strip_tags(self, text: str) -> str:
        """Remove all tags from text"""
        return self.TAG_PATTERN.sub('', text)
    
    def get_tag_color(self, tag_name: str) -> str:
        """Get color for tag name"""
        return self.tag_colors.get(tag_name, '#000000')
    
    def format_for_display(self, text: str) -> str:
        """
        Format tagged text for display (simplified version)
        This could be enhanced with colored markers in a rich text widget
        
        For now, just show tags as-is
        """
        return text
