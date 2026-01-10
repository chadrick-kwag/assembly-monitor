# Web Project Structure

This directory contains the web-related components of the project, separated into `backend` and `frontend`.

## `backend/`

This directory houses the backend services for the web application.

- `main.py`: The primary entry point for the backend application, likely containing API definitions and server setup.
- `__pycache__/`: Python's cache directory.

### Backend API Endpoints

The `main.py` file exposes the following API endpoints:

- **`GET /`**
  - **Description:** Returns a welcome message.
  - **Response:** `{"message": "Welcome to the Legislation Scraper API"}`

- **`GET /posts/`**
  - **Description:** Retrieves a paginated list of all posts from the database.
  - **Query Parameters:**
    - `fetchsize` (int, optional, default: 100): The number of posts to retrieve.
    - `startfrom` (int, optional, default: 0): The starting index for pagination.
  - **Response:** A JSON object containing the total count of posts and a list of post objects.

- **`GET /posts/{post_id}`**
  - **Description:** Retrieves a single post by its unique ID.
  - **Path Parameter:**
    - `post_id` (int, required): The ID of the post to retrieve.
  - **Response:** A JSON object representing the post.

- **`GET /posts/legislation/{legislation_number}`**
  - **Description:** Retrieves a single post by its legislation number.
  - **Path Parameter:**
    - `legislation_number` (str, required): The legislation number of the post to retrieve.
  - **Response:** A JSON object representing the post.

- **`GET /download/pdf/{post_id}`**
  - **Description:** Downloads the PDF file associated with a specific post.
  - **Path Parameter:**
    - `post_id` (int, required): The ID of the post whose PDF should be downloaded.
  - **Response:** A PDF file.

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