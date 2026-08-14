# Implementation Prompt

Build a lightweight product layer on top of the existing ML observability backend without turning the project into a full production platform.

Scope:

1. Keep the current FastAPI backend, training flow, monitoring flow, and observability stack.
2. Add a basic frontend that can:
   - log in with existing credentials
   - submit prediction inputs
   - display prediction output, confidence, latency, and model version
   - show recent prediction logs from the database
   - show model monitoring metrics already computed by the backend
   - let an admin trigger the monitoring/retraining workflow manually
3. Do not expand scope into enterprise auth, full label-feedback pipelines, or advanced deployment orchestration.
4. Optimize for demoability, clarity, and interview value rather than full production completeness.
5. Keep the architecture honest:
   - this is a monitoring-and-retraining demo platform
   - not a fully autonomous production ML platform with true live-accuracy feedback

Definition of done:

- A user can open a basic dashboard in the browser.
- The user can authenticate and run predictions.
- The user can see metrics and recent logs.
- An admin can trigger monitoring/retraining from the UI.
- The UI clearly reflects the current backend capabilities.
