
interface NotebookCell {
  cell_type: string;
  metadata: Record<string, object | string>;
  source: string | string[];
  execution_count?: number;
}

export interface NotebookData {
  cells: NotebookCell[];
  metadata: Record<string, object | string>;
  nbformat: number;
  nbformat_minor: number;
}

interface ScriptParsingResult {
  script: string;
  isFilePolyglot: boolean;
  error?: string;
}

export function extractCodeFromNotebook(notebookData: NotebookData) {
  const codeBlocks: string[] = [];

  for (const cell of notebookData?.cells || []) {
    // Only process code cells
    if (cell.cell_type !== 'code') {
      continue;
    }

    let source = cell.source;

    // Handle source as string or array
    if (Array.isArray(source)) {
      source = source.join('');
    }

    // Skip empty cells
    if (!source.trim()) {
      continue;
    }

    codeBlocks.push(source);
  }

  return {
    codeBlocks,
  };
}

export function processMagicCommands(codeBlocks: string[]) {
  const processedBlocks: string[] = [];
  let isFilePolyglot = false;

  for (const block of codeBlocks) {
    /**
     * TODO: @adamrohr parse the configure magic to prepopulate smart defaults
     * in the next Job configuration step
     *  */
    if (block.startsWith('%%configure')) {
      continue;
    } else if (block.startsWith('%%pyspark')) {
      // Remove the magic command from the first line
      const lines = block.split('\n');
      const processedBlock = lines.length > 1 ? lines.slice(1).join('\n') : '';
      processedBlocks.push(processedBlock);
    } else if (block.startsWith('%%') && !block.includes('project.spark')) {
      isFilePolyglot = true;
    } else {
      // Regular code cell, ensure it's not configuring a magic
      const lines = block.split('\n');
      const processedBlock = lines.filter(line => !line.startsWith('%')).join('\n');
      processedBlocks.push(processedBlock);
    }
  }

  return {
    processedBlocks,
    isFilePolyglot,
  };
}

// Converts a Jupyter notebook (.ipynb) to Python code string
export function convertNotebookToScript(notebookData: NotebookData | string): ScriptParsingResult {
  try {
    const parsedData: NotebookData =
      typeof notebookData === 'string' ? (JSON.parse(notebookData) as NotebookData) : notebookData;

    const { codeBlocks } = extractCodeFromNotebook(parsedData);
    const { processedBlocks, isFilePolyglot } = processMagicCommands(codeBlocks);

    // Combine all code blocks with separators
    const processedScript = processedBlocks.map(block => `\n${block}\n`).join('');
    return {
      script: processedScript,
      isFilePolyglot,
    };
  } catch (e: unknown) {
    const errorMessage = e instanceof Error ? e.message : String(e);
    return {
      script: '',
      isFilePolyglot: false,
      error: errorMessage,
    };
  }
}

export function isJupyterNotebook(filename: string): boolean {
  return filename.toLowerCase().endsWith('.ipynb');
}

export function readFileContent(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = event => {
      try {
        const content = event.target?.result as string;
        resolve(content);
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => {
      reject(new Error(`Error reading file: ${file.name}`));
    };

    reader.readAsText(file);
  });
}

export async function extractPythonScript(file: File): Promise<ScriptParsingResult> {
  const content = await readFileContent(file);

  if (isJupyterNotebook(file.name)) {
    return convertNotebookToScript(content);
  }

  return {
    script: content,
    isFilePolyglot: false,
  };
}
