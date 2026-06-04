/**
 * String manipulation specifically aligned with the native C++ parser output.
 */

export const truncateSnippet = (text: string, maxLength: number = 140): string => {
  if (text.length <= maxLength) return text;
  // Prevent cutting off in the middle of a word
  const truncated = text.slice(0, maxLength);
  const lastSpace = truncated.lastIndexOf(' ');
  return `${truncated.slice(0, lastSpace > 0 ? lastSpace : maxLength)}...`;
};

/**
 * Highlights exact keyword matches extracted during the SIMD tokenization phase.
 * Note: Returns a string representation for React dangerouslySetInnerHTML or a specialized parser component.
 */
export const highlightTokens = (text: string, tokens: string[]): string => {
  if (!tokens || tokens.length === 0) return text;
  
  let processedText = text;
  tokens.forEach(token => {
    // Case-insensitive replacement wrapping in a Tailwind highlight class
    const regex = new RegExp(`(${token})`, 'gi');
    processedText = processedText.replace(regex, `<mark class="bg-blue-100 text-blue-900 px-1 rounded font-medium">$1</mark>`);
  });
  
  return processedText;
};
