"""
open_analysis.py
----------------
A lightweight, multi-provider AI Data Analysis library using SQL reasoning on pandas DataFrames.

Supports:
- Google Gemini (via google-genai)
- Groq (via groq API)
- OpenAI (via openai API)

Author: Mohammad Abdullah
Version: 1.0.0
"""

import os
import sys
import subprocess
import warnings
warnings.filterwarnings("ignore")

# --- Auto dependency installer ---
def _ensure_dependencies():
    required_packages = [
        "pandas",
        "duckdb",
        "html2text",
        "python-dotenv",
        "streamlit",
    ]
    optional_packages = {
        "groq": "groq",
        "gemini": "google-genai",
        "openai": "openai"
    }

    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable,  "-m", "pip", "install","-U", pkg])

    for pkg in optional_packages.values():
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install","-U", pkg])



# --- Imports after ensuring ---
import duckdb
import pandas as pd
import html2text
from streamlit import html


def open_analysis(
    df: pd.DataFrame = None,
    model_provider: str = "openai",
    model: str = None,
    api_key: str = None,
    question: str = "Do a data analysis on the dataframe and give me insights?",
    html_output: bool = False,
    temperature_one: float = 0.2,
    temperature_two: float = 0.7,
    max_completion_tokens: int = 1024,
    query_view: bool = True,
    output_layer_context: str = None,
    query_context: str = None,
    logging: bool = True
):
    _ensure_dependencies()
    """
    Perform automated data analysis using an LLM provider (Gemini, Groq, or OpenAI).

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    model_provider : str
        One of ["gemini", "groq", "openai"].
    model : str
        Model name (depends on provider).
    api_key : str
        API key for the respective provider.
    question : str
        The analysis question.
    html_output : bool
        If True, prints HTML output instead of plain text.
    temperature_one : float
        Temperature for the SQL generation layer.
    temperature_two : float
        Temperature for the insights/summary layer.
    query_view : bool
        If True, displays the generated SQL.
    output_layer_context : str
        Optional context for the summarization step.
    query_context : str
        Optional KPI or calculation context.
    logging : bool
        Enable debug logs.

    Returns
    -------
    str
        Plain text or HTML analysis insights.
    """

    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("A valid pandas DataFrame must be provided.")

    # --- Import API clients dynamically ---
    client = None

    if model_provider.lower() == "gemini":
        from google import genai
        model = model or "gemini-2.0-flash"
        client = genai.Client(api_key=api_key)
    elif model_provider.lower() == "groq":
        from groq import Groq
        model = model or "llama-3.3-70b-versatile"
        client = Groq(api_key=api_key)
    elif model_provider.lower() == "openai":
        from openai import OpenAI
        model = model or "gpt-4o"
        client = OpenAI(api_key=api_key)
    else:
        raise ValueError("Invalid model_provider. Choose from: 'gemini', 'groq', or 'openai'.")

    plain_text, output_html = "", ""

    # --- First Layer: SQL Generation ---
    first_layer_prompt = (
        "Your job is to generate a valid SQL query only (no explanation, no formatting). "
        f"The dataframe preview is:\n{df.head().to_string()}\n"
        "Table Name: 'df'\n"
        f"User Question: {question}"
    )
    if query_context:
        first_layer_prompt += f"\nKPI Calculation: {query_context}"

    query_sql = ""
    df_result = None

    # --- Provider-specific handling ---
    if model_provider == "gemini":
        while True:
            first_layer = client.models.generate_content(
                model=model,
                contents=first_layer_prompt,
                config={"temperature": temperature_one}
            )
            query_sql = first_layer.text.strip()
            if query_view:
                print("\nGenerated SQL Query:\n", query_sql, "\n")

            try:
                duckdb.register("df", df)
                df_result = duckdb.query(query_sql).to_df()
                break
            except Exception as e:
                if logging:
                    print("❌ SQL execution failed:", e)

    elif model_provider == "groq":
        while True:
            first_layer = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": first_layer_prompt}],
                temperature=temperature_one,
                max_completion_tokens=max_completion_tokens,
                top_p=1,
                stream=True
            )
            query_sql = "".join(chunk.choices[0].delta.content or "" for chunk in first_layer)
            query_sql = query_sql.replace("```", "").replace("sql", "").strip()

            if query_view:
                print("\nGenerated SQL Query:\n", query_sql, "\n")

            try:
                duckdb.register("df", df)
                df_result = duckdb.query(query_sql).to_df()
                break
            except Exception as e:
                if logging:
                    print("❌ SQL execution failed:", e)

    elif model_provider == "openai":
        while True:
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
            query_sql = "".join(chunk.choices[0].delta.content or "" for chunk in first_layer)
            query_sql = query_sql.replace("```", "").replace("sql", "").strip()

            if query_view:
                print("\nGenerated SQL Query:\n", query_sql, "\n")

            try:
                duckdb.register("df", df)
                df_result = duckdb.query(query_sql).to_df()
                break
            except Exception as e:
                if logging:
                    print("❌ SQL execution failed:", e)

    # --- Second Layer: Analysis & Summary ---
    second_layer_prompt = (
        f"For the user question: '{question}', "
        f"the query result is:\n{df_result.to_string()}\n\n"
        "Please summarize this result in a clear, structured, and visually appealing HTML format. "
        "Explain the insights in detail."
    )
    if output_layer_context:
        second_layer_prompt += f"\nAdditional Knowledge: {output_layer_context}"

    # --- Generate Summary ---
    if model_provider == "gemini":
        second_layer = client.models.generate_content(
            model=model,
            contents=second_layer_prompt,
            config={"temperature": temperature_two}
        )
        output_html = second_layer.text.strip()

    elif model_provider in ["groq", "openai"]:
        second_layer = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": second_layer_prompt}],
            temperature=temperature_two,
            top_p=1,
            stream=True
        )
        output_html = "".join(chunk.choices[0].delta.content or "" for chunk in second_layer)
        output_html = output_html.replace("```", "").replace("html", "").strip()

    # --- Output Formatting ---
    try:
        if html_output:
            print(output_html)
            return output_html
        else:
            plain_text = html2text.html2text(output_html)
            print(plain_text)
            return plain_text
    except Exception as e:
        if logging:
            print("❌ HTML conversion failed:", e)
        return output_html or plain_text