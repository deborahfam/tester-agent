# Auto Tester

This folder contains a reference implementation of an automatic **programming exercise generator and validator** based on language models and a web interface using **Streamlit**.  The project structure follows the proposal described by the user and includes independent modules to extract information from a PDF, invoke a large language model (LLM), analyze input and output schemas, generate test cases, validate different solutions and package everything in a project that can be run with PyTest. 

> Note:** Many of the components that interact with external services (such as the OpenRouter API) or deeply analyze the statement of an exercise are implemented as a *template*.  Comments and extension points have been added for the developer to complete according to actual needs.  This basis serves as a guide and starting point for a more complete development.

### Estructure

```
auto_tester/
├── app.py # Streamlit application
├── core/
│ ├── extractor.py # Extraction and statement normalization
│ ├── generator.py # LLM client and solution/test generation
│ ├── validator. py # Safe execution and differential validation
│ ├── test_builder.py # Test file construction pytest
│ ├── sandbox.py # Safe execution sandbox
│ └─── utils. py # Auxiliary functions
├── prompts/
│ ├── generate_solution.txt # Prompt template for solutions
│ ├── generate_tests.txt # Prompt template for test cases
│ └─── extract_schema. txt # Schema extraction prompt template
├─── examples/
│ ├── template.py # Sample code template
│ └── sample_problem.pdf# sample PDF (you can substitute with real PDF)
└── requirements.txt # Project dependencies
```

Each module includes documentation in the form of docstrings to facilitate understanding and further expansion.