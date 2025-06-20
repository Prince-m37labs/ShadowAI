// Regex patterns to detect code blocks without markdown formatting
export const codePatterns = [
  /(?:(?:public|private|static|void|class|interface|enum|function|const|let|var)\s+[\w\s]+\s*\{[\s\S]*?\})/, // C-style, JS, Java
  /(?:def\s+[\w_]+\s*\(.*?\):\s*\n(?:.|\n)*?(?=\n\w|\Z))/, // Python
  /(?:func\s+[\w_]+\s*\(.*?\)\s*\{[\s\S]*?\})/, // Go, Swift
  /(?:SELECT\s+[\s\S]+?\s+FROM\s+[\w_]+|INSERT\s+INTO\s+[\w_]+|UPDATE\s+[\w_]+|DELETE\s+FROM\s+[\w_]+)/i, // SQL
]; 