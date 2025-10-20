/**
 * Paste Content Cleaner for Blog Editor
 * Handles cleaning of Word/Google Docs pasted content
 */

document.addEventListener('DOMContentLoaded', function() {
    const editor = document.getElementById('blogContentEditor');
    
    if (editor) {
        editor.addEventListener('paste', function(event) {
            event.preventDefault();
            
            const clipboardData = event.clipboardData || window.clipboardData;
            const pastedData = clipboardData.getData('text/html') || clipboardData.getData('text/plain');
            
            if (pastedData) {
                const cleanedContent = cleanPastedContent(pastedData);
                document.execCommand('insertHTML', false, cleanedContent);
                
                // Save current selection
                const selection = window.getSelection();
                const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
                
                // Trigger content sync if available
                const contentField = document.getElementById('blogContent');
                if (contentField) {
                    contentField.value = editor.innerHTML;
                }
                
                // Update preview if available
                const previewContent = document.getElementById('previewContent');
                if (previewContent) {
                    previewContent.innerHTML = editor.innerHTML;
                }
            }
        });
    }
});

/**
 * Clean pasted content from Word/Google Docs
 */
function cleanPastedContent(html) {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Convert Word bold formatting to proper HTML
    const boldSpans = tempDiv.querySelectorAll('span');
    boldSpans.forEach(span => {
        const style = span.getAttribute('style') || '';
        if (style.includes('font-weight:bold') || style.includes('font-weight: bold') || style.includes('font-weight:700')) {
            const strong = document.createElement('strong');
            strong.innerHTML = span.innerHTML;
            span.replaceWith(strong);
        } else if (style.includes('font-style:italic') || style.includes('font-style: italic')) {
            const em = document.createElement('em');
            em.innerHTML = span.innerHTML;
            span.replaceWith(em);
        }
    });
    
    // Handle Word's <b> tags that might be nested in spans
    const bTags = tempDiv.querySelectorAll('b');
    bTags.forEach(b => {
        const strong = document.createElement('strong');
        strong.innerHTML = b.innerHTML;
        b.replaceWith(strong);
    });
    
    // Remove Google Docs specific elements
    const googleDocsSpans = tempDiv.querySelectorAll('span[id*="docs-internal-guid"]');
    googleDocsSpans.forEach(span => {
        span.replaceWith(...span.childNodes);
    });
    
    // Remove style blocks and comments
    const styleElements = tempDiv.querySelectorAll('style');
    styleElements.forEach(style => style.remove());
    
    // Clean all elements
    const allElements = tempDiv.querySelectorAll('*');
    allElements.forEach(element => {
        // Keep only essential formatting tags
        const allowedTags = ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h2', 'h3', 'ul', 'ol', 'li', 'hr'];
        
        if (allowedTags.includes(element.tagName.toLowerCase())) {
            // Remove attributes but keep the tag
            element.removeAttribute('style');
            element.removeAttribute('class');
            element.removeAttribute('id');
            element.removeAttribute('face');
            element.removeAttribute('size');
            element.removeAttribute('color');
        } else {
            // Replace non-allowed tags with their content
            if (element.textContent.trim()) {
                element.replaceWith(...element.childNodes);
            } else {
                element.remove();
            }
        }
    });
    
    return tempDiv.innerHTML;
}