# Web Project Structure

This directory contains the web-related components of the project, separated into `backend` and `frontend`.

## `backend/`

This directory houses the backend services for the web application.

- `main.py`: The primary entry point for the backend application, likely containing API definitions and server setup.
- `__pycache__/`: Python's cache directory.

## `frontend/`

This directory contains the frontend application, which is a modern web interface. It appears to be a React project set up with Vite.

- `public/`: Contains static assets that are served directly.
  - `vite.svg`: Default Vite logo.
- `src/`: Source code for the frontend application.
  - `App.css`: Stylesheet for the main application component.
  - `App.tsx`: The main React application component.
  - `index.css`: Global styles.
  - `main.tsx`: The entry point for the React application.
  - `assets/`: Directory for various assets.
    - `react.svg`: React logo asset.
- `index.html`: The main HTML file for the frontend application.
- `package.json`: Defines project metadata and lists development and runtime dependencies.
- `package-lock.json`: Records the exact versions of dependencies used.
- `vite.config.ts`: Configuration file for Vite.
- `tsconfig.json`: TypeScript configuration for the project.
- `tsconfig.app.json`: TypeScript configuration specific to the application.
- `tsconfig.node.json`: TypeScript configuration specific to Node.js environments (e.g., Vite configuration).
- `eslint.config.js`: Configuration for ESLint, a static code analysis tool.
- `.gitignore`: Specifies intentionally untracked files to ignore by Git.
- `node_modules/`: Directory containing installed Node.js modules.
- `README.md`: Frontend-specific README.