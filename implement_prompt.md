# Reusable Project Implementation Prompt

Copy this prompt into an AI coding agent opened in the project repository:

```text
Implement this project from its Product Requirements Document.

1. Read all of `PRD.md`, `README.md`, `prompt.md`, and the existing source/configuration before editing. Treat `PRD.md` as the functional and visual specification; treat other repository files as project context. If the PRD conflicts with the current code, follow the PRD and update the documentation to match the result.
2. Inspect the repository state, branch, and configured Git remotes. Preserve existing user changes. Do not reset, force-push, or overwrite unrelated work.
3. Build the complete project described in the PRD. Keep the specified Python/Streamlit/pandas/Plotly stack, data source and schema, calculations, controls, visual system, and disclaimers. Do not silently omit features or replace them with mockups. Keep feature behavior and assumptions explicit in the UI.
4. Run the applicable checks and validation described by the PRD and repository workflow. Validate the local data snapshot and verify important calculations and app startup when the environment allows. Fix issues found. If a dependency, credential, service, or deployment setting blocks verification, state the concrete blocker and finish all independent work.
5. Update `README.md` and other project documentation when implementation or setup changes. Ensure deployment instructions match the actual runtime. Streamlit needs a Python host; do not claim that GitHub Pages runs it. Configure or verify Streamlit Community Cloud only when account access and required authorization are available.
6. Review the final diff for correctness, accidental files, secrets, and whitespace errors. Commit the completed work with a concise message, then push the current working branch to its configured remote (normally `origin`). Do not force-push. If pushing is blocked by missing access or credentials, leave the commit intact and report the exact action the user must take.
7. In the final response, summarize what was built, list checks and their outcomes, give the commit and push status, and clearly state any feature, runtime, or deployment limitation that remains. Never claim successful deployment without confirming the app is live and usable.

Work through the implementation end to end. Do not stop after proposing a plan or generating code snippets; modify the repository, validate the result, and push it when repository access permits.
```
