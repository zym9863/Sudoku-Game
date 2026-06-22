The test must cover more than 90% of the API interfaces.
Run `bash run_tests.sh` to install dependencies and launch all tests, all of which must pass.

1. Startup command: The project must be able to be started with one keystroke, and only with one keystroke, using the command "docker compose up".
2. Runtime dependencies: Runtime dependencies must be declared through Docker Compose
3. Service exposure: Explicitly expose ports in docker-compose.yml.  
4. README specification: It must include a Markdown format document that clearly states:
  - How to Run
  - Service address (Services List)
  - Verification method

3.1 Hard threshold (One-Vote Veto)
Core principle: The code must be able to run, and it must run according to the requirements of the problem.
3.1.1 Absolute feasibility
One-click start: The deliverable must strictly support Docker compose up for startup. If any errors are reported during the startup process (such as missing dependencies, port conflicts, or configuration errors), it is directly disqualified.
Environment isolation: It is strictly prohibited to have situations where "it runs locally on my machine". The code must not rely on absolute paths on your local machine, specific global environment variables, or system libraries not declared in the Dockerfile.
Consistency in documentation: The startup steps outlined in the README must be authentic and effective, ensuring that verifiers can run them without having to guess or modify the source code.
3.1.2 Strict relevance to the topic
The core objective remains the same: development must strictly adhere to the business goals described in the Prompt. For instance, if the Prompt requires "implementing a customer service system that supports multiple rounds of dialogue", merely implementing a "single question-and-answer" system would be considered off-topic.
Unauthorized simplification is prohibited: It is strictly forbidden to reduce development difficulty by significantly reducing functionality or replacing core requirements (such as simplifying "real-time WebSocket communication" to "HTTP polling").

3.2 Delivery Completeness
Core principle: Deliver a prototype of the product, not just code snippets
3.2.1 Possess engineering structure (0-1 completeness)
Project format: The deliverable must be a complete engineering project, featuring a clear directory structure (such as src, config, public, tests, etc.) and a hierarchical code structure.
Rejection note: Submitting single-file code (such as a main.py or index.html file with thousands of lines) or providing only code snippets of core functions is strictly prohibited. The submission must include complete configuration files (package.json, pom.xml, requirements.txt, etc.).
3.2.2 Real logic implementation (rejecting Mock deception)
Logical truth: Unless the Prompt explicitly requires the use of Mock data (or involves an external expensive API that cannot be called), the core business logic must be implemented authentically.
Hard coding is strictly prohibited: for example, the login interface cannot directly return "Login Success", and must include verification logic; the query interface cannot directly return a fixed JSON list, and must include data query or processing logic.

3.3 Engineering and architecture quality
Core principle: The code must be maintainable, adhere to industry-wide standards, and meet best practices.
3.3.1 The architecture is reasonably layered
Separation of duties: The code structure should reflect "high cohesion and low coupling".
Backend: It is recommended to adopt a standard layered architecture, and it is strictly prohibited to mix database operations, business logic, and API definitions within the same function.
Front-end: Components should be reasonably split to avoid the appearance of "God components" consisting of thousands of lines.
File organization: Directory naming should be semantic, making it clear at a glance (such as /utils, /components, /api).
3.3.2 Code cleanliness (no junk files)
- Remove redundancies: Before submitting, all dependent directories, cache files, and build artifacts must be cleaned up (see Step 3 for the structure specification of artifact attachments).
- Configuration desensitization: Ensure that the configuration file does not contain your personal access key (AK)/secret key (SK), intranet IP, or sensitive information.
- Code quality: Remove large sections of commented-out dead code, as well as print/console.log statements used for debugging.
- API interface tidiness: If there are API interfaces in the project, when receiving the API interface responses, it is necessary to beautify the content of the API interface to prevent returning some JSON with unclear structure.
3.3.3 Maintainability and Extensibility
Reject one-time codes: Logical design should consider extensibility and avoid a large number of magic numbers or deeply nested if-else statements.
3.3.4 Test standards
The project must provide a complete and executable test verification plan and relevant test materials as a necessary component of system acceptance. The testing objective is to verify the correctness, stability, and robustness of the system's core functions, key business logic, and exception handling mechanisms.
Test verification must encompass both unit testing and API interface function testing. Both types of testing are essential for acceptance and must not be omitted. The testing requirements and examples are as follows:
3.3.4.1 Unit testing requirements and examples
Unit tests should cover the main functional modules, core logic processing flows, and key boundary scenarios of the system, with a focus on verifying the correctness of internal logic implementation.
Example description:
- For the core business calculation logic, corresponding unit test cases need to be provided to verify whether the processing results under normal input, boundary input, and illegal input conditions meet expectations;
- Unit test cases should be separately written for key state transition logic (such as task creation, execution, failure, retry, and other processes) to verify the correctness of behavior under various states;
- For exception handling logic, it is necessary to construct abnormal scenarios (such as null values, out-of-range parameters, etc.) to verify that the system can correctly return error messages and maintain stable operation.
3.3.4.2 API Interface Function Testing Requirements and Examples
API interface function testing should cover the main interfaces provided by the system to the outside world, verifying the functional integrity and stability of the interfaces under different input conditions.
Example description:
- For core business interfaces, it is necessary to provide interface invocation tests to verify that the interfaces can return correct response results under normal request parameters;
- For abnormal scenarios such as missing parameters, incorrect parameter formats, and insufficient permissions, corresponding interface test cases should be provided to verify that the error codes and error messages returned by the interface comply with the interface design specifications;
- For interfaces involving data changes, the correctness of system status or data results before and after the interface call should be verified.
3.3.4.3 Test execution method and result output requirements
The project root directory must contain the following test directory structure, which is a mandatory inspection item during acceptance:
- unit_tests/: used to store unit test scripts and related test resources;
- API_tests/: Used to store API interface function test scripts and related test resources.
All tests must be uniformly organized and executed through Shell scripting. The test scripts should support one-click execution and possess the ability to run repeatedly.
Example description:
- A unified test execution script (such as run_tests.sh) can be provided in the project root directory. After executing the script, all test cases under the unit_tests/ and API_tests/ directories can be automatically invoked;
- During the test execution process, clear and readable test result information should be outputted on the terminal or in the log file, including the execution status (successful/failed) of each test case, the reason for failure, and the necessary error logs;
- After the test execution is completed, summary information of test results (such as the total number of test cases, the number of passed cases, and the number of failed cases) should be outputted to facilitate the acceptance personnel to quickly judge the test coverage and execution status.
3.3.4.4 Acceptance judgment requirements
The test cases need to cover the vast majority of functional points and main business logic paths. During acceptance, the acceptor can confirm whether the test is fully executed and the results meet expectations by executing the test script and checking the test output results.
The absence of unit testing or API interface testing, significant deficiencies in test coverage, inability to execute test scripts, or unclear test result output are all considered as non-compliance with acceptance requirements.

3.4 Engineering details and professionalism
Core principle: Hold yourself to the standard of production-level code.
3.4.1 Robust error handling
Elegant degradation: When an interface reports an error, it should return a standard HTTP status code and a clear JSON error message (such as `{"code": 400, "msg": "Invalid email format"}`), and it is strictly prohibited to directly throw out the original Stack Trace (stack information) or cause the service to crash and become unresponsive.
Front-end fault tolerance: When an interface request fails, the UI should display a corresponding Toast prompt or a default page, rather than a blank screen or no response.

3.4.2 Standardized log recording
Effective logs: Key business processes (such as login, payment, and data changes) must have log outputs.
Log quality: Logs should contain necessary context to facilitate problem investigation. Reject meaningless logs (such as print("here"), console.log("111)).

3.4.3 Safety and parameter verification
Input defense: Perform validity verification (nullity checking, format checking, length limitation) on all parameters (Body, Query, Path) passed in from the front end.
Basic security: Avoid obvious security vulnerabilities (such as directly concatenating SQL strings, storing passwords in plaintext on the front end, etc.).

3.5 Depth of requirement understanding
Core principles: complete, correct, and well-done.
3.5.1 Identify implicit constraints
   Business closed loop: It is necessary to not only fulfill the literal functions, but also consider the rationality of business scenarios. For example:
  E-commerce system: Inventory deduction cannot be negative.
  Booking system: No duplicate bookings for the same time slot are allowed.
  Logical consistency: Data flow must be logically coherent, and there must not be situations where the front end displays success but the data is not stored in the backend.
3.5.2 Refuse mechanical translation
Scenario adaptation: Code implementation should align with the user scale and usage scenarios set by the Prompt, rather than blindly applying generic templates.

3.6 Aesthetics (only for frontend/full-stack/mobile-end questions)
Add some test data to facilitate feature verification.
Core principle: The interface should be clean, modern, and possess basic interactive usability.
3.6.1 Visual standards
Neat layout: Elements are aligned, with uniform spacing (reasonable margin/padding), and there is no content overflow, misalignment, or garbled text.
Color harmony: The color matching is consistent with the main color tone, with appropriate contrast and no glare.
Modernization: It is recommended to use mainstream UI frameworks (such as Ant Design, Material UI, Tailwind CSS, Bootstrap, etc.) to enhance aesthetics.
3.6.2 Interactive experience
Operational feedback: Button clicks should have feedback (loading status, disabled status), and mouse hovering should cause a change in style.
Smooth process: The page transition logic is clear, with no dead links, allowing users to smoothly complete core business operations.