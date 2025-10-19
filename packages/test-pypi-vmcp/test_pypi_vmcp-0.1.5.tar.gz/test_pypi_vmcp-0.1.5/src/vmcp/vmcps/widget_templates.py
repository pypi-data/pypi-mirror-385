"""
Widget template system for creating production-grade React widgets
following OpenAI Apps SDK patterns.
"""

def get_default_index_jsx(widget_name: str) -> str:
    """Generate default index.jsx with OpenAI Apps SDK hooks"""
    root_id = widget_name.lower().replace(' ', '-').replace('_', '-')

    return f'''import React, {{ useState, useEffect }} from 'react';
import './index.css';

export default function {widget_name.replace('-', '').replace('_', '').title()}() {{
  const [toolData, setToolData] = useState(null);
  const [displayMode, setDisplayMode] = useState('full');

  useEffect(() => {{
    // Listen for tool invocation data from OpenAI
    if (window.openai?.toolInvocationData) {{
      setToolData(window.openai.toolInvocationData);
    }}

    // Listen for display mode changes
    if (window.openai?.displayMode) {{
      setDisplayMode(window.openai.displayMode);
    }}

    // Set up event listeners for dynamic updates
    const handleToolData = (event) => {{
      if (event.detail) {{
        setToolData(event.detail);
      }}
    }};

    const handleDisplayMode = (event) => {{
      if (event.detail) {{
        setDisplayMode(event.detail);
      }}
    }};

    window.addEventListener('openai:tooldata', handleToolData);
    window.addEventListener('openai:displaymode', handleDisplayMode);

    return () => {{
      window.removeEventListener('openai:tooldata', handleToolData);
      window.removeEventListener('openai:displaymode', handleDisplayMode);
    }};
  }}, []);

  // Expose widget state to OpenAI
  useEffect(() => {{
    if (window.openai?.setWidgetState) {{
      window.openai.setWidgetState({{
        ready: true,
        data: toolData
      }});
    }}
  }}, [toolData]);

  return (
    <div className="widget-container" data-display-mode={{displayMode}}>
      <div className="widget-header">
        <h1>{widget_name}</h1>
      </div>
      <div className="widget-content">
        {{toolData ? (
          <div className="tool-data">
            <h2>Tool Invocation Data:</h2>
            <pre>{{JSON.stringify(toolData, null, 2)}}</pre>
          </div>
        ) : (
          <div className="placeholder">
            <p>Waiting for tool invocation...</p>
          </div>
        )}}
      </div>
    </div>
  );
}}
'''


def get_default_index_css(widget_name: str) -> str:
    """Generate default index.css with modern styling"""
    return '''* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --background: #ffffff;
  --surface: #f8fafc;
  --border: #e2e8f0;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --radius: 8px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--background);
  color: var(--text-primary);
}

.widget-container {
  width: 100%;
  min-height: 100vh;
  padding: 24px;
  background: var(--background);
}

.widget-container[data-display-mode="compact"] {
  min-height: auto;
  padding: 16px;
}

.widget-container[data-display-mode="minimal"] {
  min-height: auto;
  padding: 12px;
}

.widget-header {
  margin-bottom: 24px;
}

.widget-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.widget-container[data-display-mode="compact"] .widget-header h1 {
  font-size: 20px;
}

.widget-container[data-display-mode="minimal"] .widget-header h1 {
  font-size: 18px;
}

.widget-content {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.widget-container[data-display-mode="compact"] .widget-content {
  padding: 16px;
}

.widget-container[data-display-mode="minimal"] .widget-content {
  padding: 12px;
}

.placeholder {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-secondary);
}

.placeholder p {
  font-size: 16px;
}

.tool-data {
  width: 100%;
}

.tool-data h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.tool-data pre {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  overflow-x: auto;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
}

/* Responsive design */
@media (max-width: 640px) {
  .widget-container {
    padding: 16px;
  }

  .widget-header h1 {
    font-size: 20px;
  }

  .widget-content {
    padding: 16px;
  }
}
'''


def get_default_package_json(widget_name: str) -> str:
    """Generate default package.json following OpenAI Apps SDK structure"""
    return f'''{{
  "name": "{widget_name}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "build": "vite build"
  }},
  "dependencies": {{
    "react": "^19.1.1",
    "react-dom": "^19.1.1"
  }},
  "devDependencies": {{
    "vite": "^7.1.1",
    "@vitejs/plugin-react": "^4.5.2",
    "typescript": "^5.9.2"
  }}
}}
'''


def get_vite_config(widget_name: str) -> str:
    """Generate vite.config.mts for widget build"""
    return f'''import {{ defineConfig }} from 'vite';
import react from '@vitejs/plugin-react';
import {{ resolve }} from 'path';

export default defineConfig({{
  plugins: [react()],
  esbuild: {{
    jsx: 'automatic',
    jsxImportSource: 'react',
    target: 'es2022',
  }},
  build: {{
    target: 'es2022',
    outDir: 'dist',
    emptyOutDir: true,
    minify: 'esbuild',
    cssCodeSplit: false,
    rollupOptions: {{
      input: resolve(__dirname, '_entry.js'),
      output: {{
        format: 'es',
        entryFileNames: '{widget_name}.js',
        inlineDynamicImports: true,
        assetFileNames: (info) =>
          (info.name || '').endsWith('.css')
            ? '{widget_name}.css'
            : '[name]-[hash][extname]',
      }},
      preserveEntrySignatures: 'allow-extension',
      treeshake: true,
    }},
  }},
}});
'''


def get_widget_html_template(widget_name: str, css_url: str, js_url: str) -> str:
    """Generate HTML that references separate CSS and JS files"""
    root_id = widget_name.lower().replace(' ', '-').replace('_', '-')

    return f'''<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="{css_url}">
</head>
<body>
  <div id="{root_id}-root"></div>
  <script type="module" src="{js_url}"></script>
</body>
</html>'''


def get_entry_wrapper(widget_name: str, entry_point: str) -> str:
    """Generate _entry.js that mounts the React component"""
    root_id = widget_name.lower().replace(' ', '-').replace('_', '-')

    return f'''import React from 'react';
import ReactDOM from 'react-dom/client';
import Widget from './{entry_point}';

const rootElement = document.getElementById('{root_id}-root');

if (rootElement) {{
  const root = ReactDOM.createRoot(rootElement);
  root.render(React.createElement(Widget));
}}
'''
