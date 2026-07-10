from common import ApiMode, env


def setup_observability():

    mode: ApiMode = env.api_mode()

    if mode != ApiMode.DEV:
        return

    try:
        from openinference.instrumentation.langchain import (
            LangChainInstrumentor,
        )
        from phoenix.otel import register

        tracer_provider = register(
            project_name="docx-converter",
            endpoint="http://localhost:6006/v1/traces",
        )

        LangChainInstrumentor().instrument(
            tracer_provider=tracer_provider
        )

        print("Phoenix enabled")

    except Exception as e:
        print("Phoenix not started:", e)