# Contributing to Streamlit Plugins  

We appreciate your interest in contributing to **Streamlit Plugins**! Whether you're fixing bugs, adding features, improving documentation, or helping with frontend components, your help is invaluable.  

Please take a moment to review the following guidelines to ensure a smooth contribution process.  

---

## Table of Contents  
1. [Code of Conduct](#code-of-conduct)  
2. [How Can I Contribute?](#how-can-i-contribute)  
   - [Reporting Issues](#reporting-issues)  
   - [Feature Requests](#feature-requests)  
   - [Contributing Code](#contributing-code)  
3. [Development Workflow](#development-workflow)  
   - [Backend (Python)](#backend-python)  
   - [Frontend (React + TypeScript)](#frontend-react--typescript)  
4. [Code Style Guidelines](#code-style-guidelines)  
5. [Contact](#contact)  

---

## Code of Conduct  
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat everyone with respect and kindness.  

---

## How Can I Contribute?  

### Reporting Issues  
If you find a bug or an issue, please [open an issue](https://github.com/quiradev/streamlit-plugins/issues). Be sure to include:  
- A clear and descriptive title.  
- Steps to reproduce the issue.  
- Relevant screenshots or GIFs, if applicable.  
- Details about your environment (Streamlit version, Python version, etc.).  

### Feature Requests  
We love hearing your ideas for improving Streamlit Plugins! If you have a feature request, [open a feature request issue](https://github.com/quiradev/streamlit-plugins/issues) and describe:  
- The feature you'd like to see.  
- Why this feature would be useful.  
- Any potential implementation ideas.  

### Contributing Code  
If you'd like to contribute code, you can work on either:  
- **Backend (Python):** Core Streamlit plugins and server-side logic.  
- **Frontend (React + TypeScript):** Custom Streamlit components with modern web technologies.  

---

## Development Workflow  

### Setting Up the Project  
1. Clone the repository:  
   ```bash
   git clone https://github.com/quiradev/streamlit-plugins.git
   cd streamlit-plugins
   ```  
2. Create and activate a virtual environment for Python development:  
   ```bash
   python -m venv venv  
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```  
3. Install Python dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
4. Install frontend dependencies (if working on components):  
   ```bash
   cd frontend  
   npm install
   ```  

---

### Backend (Python)  
- The backend is written in Python and extends Streamlit functionality.  
- Core plugins and functionality live in the `streamlit_plugins` directory.  

#### Running Tests  
Ensure your Python code works as expected by running the test suite:  
```bash
pytest
```  

---

### Frontend (React + TypeScript)  
Custom components are developed using React and TypeScript. These components interact with Streamlit via the Streamlit Component API.  

#### Workflow for Frontend Development  
1. Navigate to the `frontend` directory:  
   ```bash
   cd frontend
   ```  
2. Start the development server:  
   ```bash
   npm start
   ```  
   This will start a local server at `http://localhost:3000` where you can preview your components.  
3. Build the frontend components:  
   ```bash
   npm run build
   ```  

#### Testing Frontend Changes  
Frontend tests can be written using Jest or other JavaScript testing frameworks. Run tests with:  
```bash
npm test
```  

#### Packaging a Component  
Once your custom component is ready, package it by running:  
```bash
npm run build  
```  
Place the built files in the appropriate Python directory to make it accessible as a Streamlit plugin.  

---

## Code Style Guidelines  

### Python  
- Follow [PEP 8](https://peps.python.org/pep-0008/).  
- Use meaningful variable and function names.  
- Add comments where the code might not be self-explanatory.  

### React + TypeScript  
- Use [Prettier](https://prettier.io/) for formatting.  
- Use functional components and React hooks.  
- Keep components small and focused.  
- Follow best practices for TypeScript type safety.  

Run linters before committing:  
```bash
flake8  # For Python  
npm run lint  # For TypeScript  
```  

---

## Contact  
If you have any questions or need help, feel free to reach out by opening an issue or contacting the maintainers.  

---

Thank you for helping make Streamlit Plugins awesome! 🎉