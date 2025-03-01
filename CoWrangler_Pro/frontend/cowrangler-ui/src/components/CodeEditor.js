// For the code preview/editing

import React from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const CodeEditor = ({ code }) => {
  // Sample Python code if none is provided
  const sampleCode = `# Split the "title" column by the pattern ":"
df_split = df['title'].str.split(':', n=1, expand=True)
df = pd.concat([df, df_split.add_prefix('title')], axis=1)
df = df.drop(columns = ['title'])`;

  return (
    <div className="mb-2">
      <h5 className="mb-2">Generated Code</h5>
      <div className="border rounded p-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
        <SyntaxHighlighter language="python" style={docco}>
          {code || sampleCode}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

export default CodeEditor;