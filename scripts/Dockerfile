FROM python:3.12-slim

WORKDIR /app
COPY log_generator.py .

# Streams synthetic JSON logs to stdout so the Datadog Agent (which
# tails container stdout/stderr by default) picks them up automatically
# with zero extra config once log collection is enabled on the Agent.
ENTRYPOINT ["python3", "log_generator.py", "--stream", "--out", "/dev/stdout"]
CMD ["--error-rate", "0.08", "--interval", "2"]
