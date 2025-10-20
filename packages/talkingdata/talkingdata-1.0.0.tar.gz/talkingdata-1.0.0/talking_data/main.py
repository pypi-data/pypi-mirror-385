"""
open_analysis.py
----------------
A lightweight, multi-provider AI Data Analysis library using SQL reasoning on pandas DataFrames.

Supports:
- Google Gemini (via google-genai)
- Groq (via groq API)
- OpenAI (via openai API)

Author: Mohammad Abdullah
Version: 1.5.0
"""

import importlib
import subprocess
import sys
import warnings
warnings.filterwarnings("ignore")


def _import_or_install(package_name: str, import_name: str = None):
    """
    Tries to import a package. Installs it via pip if missing.

    Parameters
    ----------
    package_name : str
        Name of the package to install (for pip).
    import_name : str, optional
        Name used in the import statement (default: same as package_name).

    Returns
    -------
    module
        The imported module object.
    """
    import_name = import_name or package_name
    try:
        return importlib.import_module(import_name)
    except ImportError:
        print(f"📦 Installing missing dependency: {package_name} ...")
        subprocess.check_call([sys.executable,"-u", "-m", "pip", "install", package_name])
        return importlib.import_module(import_name)


# --- Import core dependencies only once ---
pd = _import_or_install("pandas")
duckdb = _import_or_install("duckdb")
html2text = _import_or_install("html2text")
traceback = _import_or_install("traceback") if "traceback" in sys.modules else importlib.import_module("traceback")


def open_analysis(
    df: pd.DataFrame,
    model_provider: str = "openai",
    model: str = None,
    api_key: str = None,
    question: str = "Do a data analysis on the dataframe and give me insights?",
    temperature_one: float = 0.2,
    temperature_two: float = 0.7,
    max_completion_tokens: int = 1024,
    output_layer_context: str = None,
    query_context: str = None,
    log_level: str = "basic"  # "none", "basic", "detailed", "debug"
) -> dict:
    """
    Perform automated data analysis using an LLM provider (Gemini, Groq, or OpenAI).

    Returns
    -------
    dict
        {
            "provider": str,
            "model": str,
            "sql_query": str,
            "query_result": pd.DataFrame,
            "html_output": str,
            "plain_text_output": str,
            "logs": list[str] | None
        }
    """

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("A valid pandas DataFrame must be provided.")

    def log(message, level="basic"):
        """Internal helper for level-based logging."""
        levels = ["basic", "detailed", "debug"]
        if log_level == "none":
            return
        if levels.index(level) <= levels.index(log_level):
            logs.append(message)

    logs = []
    provider = model_provider.lower()
    log(f"Initializing provider: {provider}", "basic")

    # --- Lazy import provider SDKs only when needed ---
    try:
        if provider == "gemini":
            genai = _import_or_install("google-genai", "google.genai")
            model = model or "gemini-2.0-flash"
            client = genai.Client(api_key=api_key)
        elif provider == "groq":
            groq = _import_or_install("groq")
            model = model or "llama-3.3-70b-versatile"
            client = groq.Groq(api_key=api_key)
        elif provider == "openai":
            openai = _import_or_install("openai")
            model = model or "gpt-4o"
            client = openai.OpenAI(api_key=api_key)
        else:
            raise ValueError("Invalid model_provider. Choose from: 'gemini', 'groq', or 'openai'.")
    except Exception as e:
        log(f"Provider initialization failed: {e}", "basic")
        log(traceback.format_exc(), "debug")
        raise

    # --- Prompt for SQL generation ---
    first_layer_prompt = (
        "Your job is to generate a valid SQL query only (no explanation, no formatting). "
        f"The dataframe preview is:\n{df.head().to_string()}\n"
        "Table Name: 'df'\n"
        f"User Question: {question}"
    )
    if query_context:
        first_layer_prompt += f"\nKPI Calculation: {query_context}"

    sql_query = ""
    df_result = None
    html_summary = ""
    plain_text = ""

    log("Starting SQL generation...", "basic")
    log(f"Prompt: {first_layer_prompt}", "debug")

    # --- SQL generation phase ---
    try:
        if provider == "gemini":
            while True:
                try:
                    first_layer = client.models.generate_content(
                        model=model,
                        contents=first_layer_prompt,
                        config={"temperature": temperature_one}
                    )
                    sql_query = first_layer.text.strip()
                    log(f"Generated SQL: {sql_query}", "detailed")
                    duckdb.register("df", df)
                    df_result = duckdb.query(sql_query).to_df()
                    break
                except Exception as e:
                    log(f"SQL execution failed: {e}", "basic")
                    log(traceback.format_exc(), "debug")

        elif provider == "groq":
            while True:
                try:
                    first_layer = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": first_layer_prompt}],
                        temperature=temperature_one,
                        max_completion_tokens=max_completion_tokens,
                        top_p=1,
                        stream=True
                    )
                    sql_query = "".join(chunk.choices[0].delta.content or "" for chunk in first_layer)
                    sql_query = sql_query.replace("```", "").replace("sql", "").strip()
                    log(f"Generated SQL: {sql_query}", "detailed")
                    duckdb.register("df", df)
                    df_result = duckdb.query(sql_query).to_df()
                    break
                except Exception as e:
                    log(f"SQL execution failed: {e}", "basic")
                    log(traceback.format_exc(), "debug")

        elif provider == "openai":
            while True:
                try:
                    first_layer = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful Data Analysis assistant."},
                            {"role": "user", "content": first_layer_prompt}
                        ],
                        temperature=temperature_one,
                        top_p=1,
                        stream=True
                    )
                    sql_query = "".join(chunk.choices[0].delta.content or "" for chunk in first_layer)
                    sql_query = sql_query.replace("```", "").replace("sql", "").strip()
                    log(f"Generated SQL: {sql_query}", "detailed")
                    duckdb.register("df", df)
                    df_result = duckdb.query(sql_query).to_df()
                    break
                except Exception as e:
                    log(f"SQL execution failed: {e}", "basic")
                    log(traceback.format_exc(), "debug")
    except Exception as e:
        log(f"SQL generation failed: {e}", "basic")
        log(traceback.format_exc(), "debug")

    # --- Summarization ---
    log("Starting insights generation...", "basic")
    # second_layer_prompt = (
    #     f"For the user question: '{question}', "
    #     f"the query result is:\n{df_result.to_string()}\n\n"
    #     "Please summarize this result in a clear, structured, and visually appealing HTML format. "
    #     "Summarize the result in clear, concise, and well-formatted HTML. but dont include like Dataframe Summary or anything. "
    #     "Keep the answer natural and human-like — no unnecessary prefaces or repetition."
    #     "Answer the question directly and naturally in one or two concise sentences. "
    #     "If the result is numeric (like a count or total), just state the value clearly. "
    #     "Avoid any explanations, formatting, or phrases like 'here is' or 'summary'."
    # )
    # second_layer_prompt = (
    # f"For the user's question: '{question}', "
    # f"the query result is:\n{df_result.to_string()}\n\n"
    # "Write a concise, natural-language summary of this result in clean, minimal HTML. "
    # "Do not include any titles, labels, or sections like 'Summary' or 'Dataframe Info'. "
    # "Answer the question directly in one or two short sentences. "
    # "If the result is numeric (e.g., a total or count), state the value simply and clearly. "
    # "Avoid repeating the question or adding phrases like 'The result is' or 'Here is'. "
    # "Keep the tone natural, fluent, and human-like."
    # )
    # second_layer_prompt = (
    # f"For the user's question: '{question}', "
    # f"the query result is:\n{df_result.to_string()}\n\n"
    # "Summarize this result directly in clean, minimal HTML without any headings, titles, or markdown symbols. "
    # "Do not include sections, labels, or phrases like 'Dataframe Row Count', 'Summary', or similar. "
    # "Respond naturally in one or two concise sentences that directly answer the question. "
    # "If the result is numeric (e.g., a total or count), just state the value clearly and naturally. "
    # "Avoid repeating the question or adding phrases such as 'The result is' or 'Here is'. "
    # "Keep the tone human-like, fluent, and minimal."
    # )
#     second_layer_prompt = (
#     f"For the user's question: '{question}', "
#     f"the query result is:\n{df_result.to_string()}\n\n"
#     "Write a direct, natural-language answer in simple HTML. "
#     "Do not include any headings, titles, markdown symbols, or labels like 'Summary' or 'Dataframe Row Count'. "
#     "Do not add explanations, context, or commentary — only state the answer itself. "
#     "If the result is numeric (like a total, count, or average), express it naturally in one short sentence, then stop. "
#     "Avoid filler phrases like 'This indicates', 'The dataframe contains', or 'The result is'. "
#     "Keep the tone natural and concise, using only minimal inline HTML such as <p> or <b> if needed."
# )
    second_layer_prompt = (
    f"For the user's question: '{question}', "
    f"the query result is:\n{df_result.to_string()}\n\n"
    "Provide a concise, insightful, and human-like analysis of this data in clean, minimal HTML. "
    "Focus on key patterns, trends, or anomalies that directly address the user's question. "
    "Do not include any introductions, titles, headings, markdown symbols, or phrases like "
    "'Here’s an analysis', 'This report shows', or 'Overview'. "
    "Avoid using numbered sections or bullet headers unless absolutely necessary for readability. "
    "Keep the tone professional but natural — as if explaining insights conversationally. "
    "If the data allows for clear observations, express them in short paragraphs or bullet points in HTML. "
    "Do not summarize the dataframe structure — focus purely on meaningful insights. "
    "Keep it concise, relevant, and free of filler."
    )
    if output_layer_context:
        second_layer_prompt += f"\nAdditional Knowledge: {output_layer_context}"

    try:
        if provider == "gemini":
            second_layer = client.models.generate_content(
                model=model,
                contents=second_layer_prompt,
                config={"temperature": temperature_two}
            )
            html_summary = second_layer.text.strip()
            html_summary = html_summary.replace("```", "").replace("html", "").strip()
        else:
            second_layer = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": second_layer_prompt}],
                temperature=temperature_two,
                top_p=1,
                stream=True
            )
            html_summary = "".join(chunk.choices[0].delta.content or "" for chunk in second_layer)
            html_summary = html_summary.replace("```", "").replace("html", "").strip()
        log("Summary generated successfully.", "basic")
    except Exception as e:
        log(f"Summary generation failed: {e}", "basic")
        log(traceback.format_exc(), "debug")

    # --- Convert HTML to text ---
    try:
        plain_text = html2text.html2text(html_summary)
        log("Converted HTML to text.", "detailed")
    except Exception as e:
        log(f"HTML conversion failed: {e}", "basic")
        log(traceback.format_exc(), "debug")
        plain_text = html_summary

    # --- Final return ---
    return {
        "provider": provider,
        "model": model,
        "sql_query": sql_query,
        "query_result": df_result,
        "html_output": html_summary,
        "plain_text_output": plain_text,
        "logs": logs if log_level != "none" else None
    }