# Potential Libraries for generating OpenAPI Specification Document

## Context
Investigation of Python Libraries which can be used to generate OpenAPI Specification Document automatically. 
Below are a list of libraries which are up for consideration, each supporting OpenAPI 3.0 and Amazon "x-" key values.

## apispec
https://github.com/marshmallow-code/apispec
-   **Maintenance Status:**  Actively maintained with regular updates. The project has over  **1,700 commits**  and continues to receive releases into 2025
-   **Latest Release:**  **v6.8.2**  (released May 12, 2025)

-   **Implementation:** Register routes and schema components with apispec (or via framework-specific plugins) rather than using Python type annotations.

-   **OpenAPI Support:**  Supports  **OpenAPI 2.0 (Swagger)**  and  **OpenAPI 3.x**  specifications - you can specify the target OpenAPI version when generating the spec.

## Flask-OpenAPI3
https://github.com/luolingchun/flask-openapi3
-   **Maintenance Status:**  Actively maintained; latest release in mid-2025. Development is ongoing with multiple releases this year.

-   **Latest Release:**  **v4.2.0**  (released June 21, 2025)

-   **License:**  MIT License

-   **Implementation:**  Provided as a Flask extension that uses  **Pydantic**  models and Flask route decorators to generate documentation. You define request/response models as Pydantic classes, and use decorators (e.g.  `@app.get`,  `@app.post`) on Flask view functions – the library then  **automatically validates data and generates the OpenAPI documentation**  from these definitions.

-   **OpenAPI Support:**  Focuses on  **OpenAPI 3**


## Spectree
https://github.com/0b01001001/spectree
-   **Maintenance Status:**  Very active – multiple updates and fixes are released frequently.

-   **Latest Release:**  **v1.4.11**  (released June 26, 2025)

-   **License:**  Apache 2.0 License (not MIT)

-   **Implementation:**  Uses  type annotations and decorators. Attach a  `@api.validate`  decorator to routes and define request/response data models with  **Pydantic**.

-   **OpenAPI Support:**  Generates  **OpenAPI 3**  documentation.


## APIFlask
https://github.com/apiflask/apiflask
-   **Maintenance Status:**  Actively maintained; saw steady releases through 2024 and a recent 2025 release.

-   **Latest Release:**  **v2.4.0**  (released March 25, 2025)

-   **License:**  MIT License.

-   **Implementation:**  It provides convenient decorators like  `@app.input()`  and  `@app.output()`  (as well as route decorators  `@app.get()`,  `@app.post()`, etc.) to declare input and output  **Schema**  classes for each endpoint.

-   **OpenAPI Support:**  Supports  **OpenAPI 3**.