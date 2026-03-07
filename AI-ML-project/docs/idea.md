**Solar Energy Generation Proxy Predictor**

* **The Task:** Predict localized shortwave solar radiation (a proxy for solar panel efficiency) using standard cloud cover and atmospheric data.
* **Data Collection Strategy:** While you cannot measure the actual power output without hardware, you can use the Open-Meteo API to pull hourly historical and real-time weather data for regions with known solar farms over the last year, instantly gathering thousands of records.
* **Attributes:** Cloud cover percentage, temperature, UV index, wind speed, and humidity.
* **ML Model:** A regression model mapping atmospheric conditions to the target variable of shortwave radiation.

---

### Maintainability and Architecture Framework

To ensure the projects are defensible, perfectly maintainable, and adhere to your requirement of separating foreign code, implement the following structured approach for whichever assignment you choose.

* **Architecture:** Divide the project into three distinct layers. The Data Layer handles API polling and raw storage (saving JSON responses as CSVs). The Processing Layer cleans, scales, and transforms the data. The Application Layer contains the ML model and the user interface. All external dependencies (e.g., API wrapper libraries, scikit-learn modules) must be isolated in a `vendor` or `lib` directory, leaving only your authored logic in the main `src` directory.
* **Tests:** Implement unit tests for your data cleaning functions to ensure null values or unexpected API responses are handled correctly. Implement integration tests to verify the pipeline correctly moves data from the raw CSV state to the transformed training state.
* **Lint Tests:** Enforce PEP 8 (if using Python) using a linter like Flake8 or Pylint. This ensures all authored code is highly readable and standard-compliant.
* **Changelog:** Maintain a `CHANGELOG.md` file following the "Keep a Changelog" standard. Document every added feature, changed process, or fixed bug chronologically to prove the iterative development of your model.
* **README:** Provide a comprehensive `README.md`. It must include a project description, the real-world application, prerequisites, strict instructions on how to launch the software without an IDE from a school terminal, and a basic usage guide.
* **Config:** Centralize all variables in a `config.json` or `.env` file. This must include API endpoints, file paths for the raw and processed data, and model hyperparameters. Hardcoding these values in the scripts will make the project difficult to maintain.
* **Semantic Versioning:** Tag your project states using Major.Minor.Patch versioning (e.g., 1.0.0). Increment the minor version when adding new API attributes and the patch version for bug fixes in the data cleaner.
* **Docs:** Generate documentation for your functions and classes using docstrings. Provide a separate markdown file explicitly detailing the origin of the data, the exact API endpoints used, and the methodology for data cleaning and scaling.
* **Workflows:** Use a simple local Git hook or a GitHub Actions workflow to automatically run your linting and testing scripts every time you commit code. This guarantees the codebase remains functional before the final defense.