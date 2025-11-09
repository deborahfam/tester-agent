"""
app.py
~~~~~~

Web application built with Streamlit to automate the generation of solutions
and tests for programming exercises from a PDF statement and a code template.
The interface guides the user through file upload, viewing the extracted
statement, generating candidate solutions and test cases, and finally allows
downloading a package ready to run with `pytest`.

To use the OpenRouter API, you need to specify the key in the environment
variable `OPENROUTER_API_KEY` or provide a key manually in the interface.
In the absence of a valid key, the system can function in demonstration
(mock) mode where simulated responses are generated.

Usage:

```
streamlit run app.py
```
"""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import streamlit as st

from core.extractor import extract_and_parse
from core.generator import LLMClient, generate_solutions, generate_test_cases
from core.validator import validate_solutions
from core.test_builder import create_test_suite_for_solutions
from core.utils import slugify, make_zipfile


st.set_page_config(page_title="Auto Tester", page_icon="🧪")
st.title("🧪 Automatic Solution and Test Generator")

st.markdown(
    "Upload an exercise statement in PDF format and a Python code template "
    "with the function signature to implement.  The system will attempt to "
    "extract the text, generate candidate implementations using a language "
    "model and create a test suite."
)

# File upload
pdf_file = st.file_uploader("Select a statement (PDF)", type=["pdf"])
template_file = st.file_uploader("Select a code template (.py)", type=["py"])

# Generation parameters
col1, col2 = st.columns(2)
with col1:
    num_solutions = st.number_input("Number of solutions to generate", min_value=1, max_value=3, value=2)
with col2:
    max_tests = st.number_input("Maximum test cases", min_value=1, max_value=20, value=10)

api_key = st.text_input(
    "API Key (OpenRouter)", value=os.environ.get("OPENROUTER_API_KEY", ""), type="password"
)

mock_mode = False
if not api_key:
    st.info(
        "⚠️ No API key provided. Demo mode will be used with simulated responses."
    )
    mock_mode = True

if st.button("Generate"):  # Only execute when user requests it
    if not pdf_file or not template_file:
        st.error("You must select a PDF and a code template before continuing.")
    else:
        # Save files temporarily
        with st.spinner("Extracting and analyzing the statement…"):
            pdf_bytes = pdf_file.read()
            pdf_path = Path(tempfile.gettempdir()) / pdf_file.name
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            problem_data = extract_and_parse(str(pdf_path))
        st.subheader("Extracted Statement")
        for key, value in problem_data.items():
            if value:
                st.markdown(f"**{key.capitalize()}**:\n{value}")

        template_code = template_file.read().decode("utf-8")
        st.subheader("Code Template")
        st.code(template_code, language="python")

        with st.spinner("Generating solutions…"):
            client = LLMClient(api_key=api_key, mock=mock_mode)
            solutions = generate_solutions(problem_data, template_code, n=int(num_solutions), client=client)
        st.subheader("Generated Solutions")
        for idx, sol in enumerate(solutions):
            st.markdown(f"### Solution {idx+1}")
            st.code(sol, language="python")

        # Generate test cases from the first solution to save tokens
        with st.spinner("Generating test cases…"):
            test_cases = generate_test_cases(problem_data, solutions[0], max_tests=int(max_tests), client=client)
        st.subheader("Proposed Test Cases")
        if test_cases:
            for tc in test_cases:
                st.json(tc)
        else:
            st.warning("Could not generate test cases automatically.")

        # Validate solutions against the obtained cases
        if test_cases:
            with st.spinner("Validating solutions…"):
                results = validate_solutions(solutions, test_cases)
            st.subheader("Validation Results")
            for sol_key, res in results.items():
                if sol_key == "differential":
                    continue
                st.markdown(f"#### {sol_key}")
                st.write(f"Passed: {res['passes']} | Failed: {res['fails']}")
                with st.expander("Details"):
                    for detail in res["details"]:
                        st.write(detail)
            if "differential" in results:
                st.subheader("Consistency Between Solutions")
                for diff in results["differential"]:
                    st.write(diff)

        # Build test files and generate zip
        if test_cases:
            with st.spinner("Building test package…"):
                work_dir = Path(tempfile.gettempdir())
                solution_paths = []
                for idx, sol in enumerate(solutions):
                    sol_name = f"solution_{idx+1}.py"
                    sol_path = work_dir / sol_name
                    with open(sol_path, "w", encoding="utf-8") as f:
                        f.write(sol)
                    solution_paths.append(str(sol_path))
                tests_dir = work_dir / "tests"
                test_files = create_test_suite_for_solutions(test_cases, solution_paths, str(tests_dir))
                zip_name = slugify(pdf_file.name) + "_suite.zip"
                zip_path = work_dir / zip_name
                # Prepare list of files to compress
                files_to_zip = []
                for sol_path in solution_paths:
                    files_to_zip.append((Path(sol_path).name, sol_path))
                for test_path in test_files:
                    arcname = "tests/" + Path(test_path).name
                    files_to_zip.append((arcname, test_path))
                make_zipfile(files_to_zip, str(zip_path))
            # Offer download
            st.subheader("Download Test Suite")
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Download ZIP",
                    data=f.read(),
                    file_name=zip_name,
                    mime="application/zip",
                )