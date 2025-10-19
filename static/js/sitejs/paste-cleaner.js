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
    
    // Remove Google Docs specific elements
    const googleDocsSpans = tempDiv.querySelectorAll('span[id*="docs-internal-guid"]');
    googleDocsSpans.forEach(span => {
        span.replaceWith(...span.childNodes);
    });
    
    // Remove style blocks and comments
    const styleElements = tempDiv.querySelectorAll('style');
    styleElements.forEach(style => style.remove());
    
    // Remove HTML comments
    const walker = document.createTreeWalker(tempDiv, NodeFilter.SHOW_COMMENT);
    const comments = [];
    let comment;
    while (comment = walker.nextNode()) {
        comments.push(comment);
    }
    comments.forEach(comment => comment.remove());
    
    // Remove empty paragraphs and excessive line breaks
    const emptyElements = tempDiv.querySelectorAll('p:empty, div:empty, span:empty, br + br');
    emptyElements.forEach(el => el.remove());
    
    // Clean up multiple consecutive line breaks
    let htmlContent = tempDiv.innerHTML;
    htmlContent = htmlContent.replace(/(<br\s*\/?\s*>\s*){3,}/gi, '<br><br>');
    htmlContent = htmlContent.replace(/(<p[^>]*>\s*<\/p>\s*){2,}/gi, '');
    htmlContent = htmlContent.replace(/^\s*(<br\s*\/?\s*>\s*)+/gi, '');
    tempDiv.innerHTML = htmlContent;
    
    // Clean all elements
    const allElements = tempDiv.querySelectorAll('*');
    allElements.forEach(element => {
        // Remove all style attributes and classes
        element.removeAttribute('style');
        element.removeAttribute('class');
        element.removeAttribute('id');
        element.removeAttribute('face');
        element.removeAttribute('size');
        element.removeAttribute('color');
        
        // Keep only essential formatting tags (including bold)
        const allowedTags = ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h2', 'h3', 'ul', 'ol', 'li', 'hr'];
        
        if (!allowedTags.includes(element.tagName.toLowerCase())) {
            if (element.textContent.trim()) {
                const p = document.createElement('p');
                p.textContent = element.textContent;
                element.replaceWith(p);
            } else {
                element.remove();
            }
        }
    });
    
    return tempDiv.innerHTML;
}