import os
import time
import json
import requests
import hashlib
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from platformdirs import user_cache_dir


def get_bourdieu_vector(
    event_name: str,
    event_context: str = "",
    skip_not_allowed_texts: bool = True,
    model: str = "bourdieuvectors",
    use_cached: bool = True,
    retries: int = 3,
):
    """
    Fetches the vector representation of a cultural event from the Bourdieu Vectors API.

    Parameters:
        event_name (str): Name of the cultural event.
        event_context (str, optional): Additional context to refine the vector. Defaults to empty string.
        skip_not_allowed_texts (bool, optional): If True, skip texts that fail validation (e.g., empty or disallowed content).
        model (str, optional): The embedding model to use. Defaults to "bourdieuvectors".
        use_cached (bool, optional): If True, reuse previously computed vectors from cache if available.
        retries (int, optional): Number of retry attempts in case of model or network errors.

    Returns:
        list or dict: The vector as a list if successful; an empty dict if the request fails.
    """

    cachedir = user_cache_dir("bourdieu-vectors", model)
    os.makedirs(cachedir, exist_ok=True)
    cache_path = os.path.join(
        cachedir,
        hashlib.md5(
            f"vector_{str(event_name)}-{str(event_context)}".encode()
        ).hexdigest()
        + ".json",
    )

    if use_cached and os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)["vector"]

    # API endpoint for fetching vectors
    url = f"https://api.bourdieuvectors.com/api/v1/vectors/{model}"

    # Send a POST request with event name and optional context as JSON
    response = requests.post(
        url,
        json={"cultural_event": event_name, "cultural_event_context": event_context},
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Return the vector from the API response
        res = response.json()

        res = {
            r: res[r]
            for r in res
            if r
            in [
                "vector",
                "cultural_event",
                "cultural_event_language",
                "model_name",
                "model_version",
                "cultural_event_language",
            ]
        }

        if use_cached:
            with open(cache_path, "w") as f:
                json.dump(res, f)
        return res["vector"]
    elif response.status_code == 503 and retries > 0:
        exception_text = f"Failed to fetch vector for event: {event_name} (status code: {response.status_code}) - {response.text} - Retry"
        time.sleep(3)
        return get_bourdieu_vector(
            event_name=event_name,
            event_context=event_context,
            skip_not_allowed_texts=skip_not_allowed_texts,
            model=model,
            use_cached=use_cached,
            retries=retries - 1,
        )
    else:
        exception_text = f"Failed to fetch vector for event: {event_name} (status code: {response.status_code}) - {response.text}"
        print(exception_text)

        if "not_allowed_input_" in response.text and skip_not_allowed_texts:
            if use_cached:
                with open(cache_path, "w") as f:
                    json.dump({"vector": {}}, f)
            return {}

        raise Exception(exception_text)


def get_bourdieu_vectors(
    title: list[str],
    event_context: str = "",
    skip_not_allowed_texts: bool = True,
    model: str = "bourdieuvectors",
    use_cached: bool = True,
    retries: int = 3,
    max_workers: int = 8,
):
    """
    Generate or retrieve Bourdieu-style embedding vectors for a list of textual titles.

    Args:
        title (list[str]): List of text titles or short phrases for which embeddings should be generated.
        event_context (str, optional): Additional contextual information to guide the embedding generation.
        skip_not_allowed_texts (bool, optional): If True, skip texts that fail validation (e.g., empty or disallowed content).
        model (str, optional): The embedding model to use. Defaults to "bourdieuvectors".
        use_cached (bool, optional): If True, reuse previously computed vectors from cache if available.
        retries (int, optional): Number of retry attempts in case of model or network errors.
        max_workers (int, optional): Maximum number of parallel threads used for vector generation.

    Returns:
        dict[str, np.ndarray]: A mapping from each input title to its corresponding embedding vector.

    Notes:
        - The function applies the concept of Pierre Bourdieu’s sociological space,
          embedding texts according to cultural, economic, and symbolic capital dimensions.
        - Parallel execution and caching improve performance on large batches.
    """
    features = [None] * len(title)
    embedding_dim_names = None

    dimension_vector = get_bourdieu_vector(
        "soccer", model=model
    )  # TODO: Implement method to get dimensions
    embedding_dim_names = list(dimension_vector.keys())

    def fetch_vector(title):
        vector = get_bourdieu_vector(
            title.strip(),
            event_context,
            model=model,
            skip_not_allowed_texts=skip_not_allowed_texts,
            use_cached=use_cached,
            retries=retries,
        )
        return list(vector.values()), list(vector.keys())

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_vector, title): idx for idx, title in enumerate(title)
        }

        with tqdm(total=len(futures), desc="Fetching Bourdieu vectors") as pbar:
            for f in as_completed(futures):
                idx = futures[f]
                try:
                    vec, dim_names = f.result()

                    if len(vec) == 0:
                        vec = [0.0] * len(embedding_dim_names)
                    elif len(vec) != len(embedding_dim_names):
                        raise Exception(
                            f"Vector len should be {len(embedding_dim_names)}, is {len(vec)}"
                        )

                    features[idx] = vec
                except Exception as e:
                    print(f"Error for {title[idx]}: {e}")
                pbar.update(1)
    return features, embedding_dim_names


def save_bourdieu_vector_cache(
    target_zip_file: str,
    model: str = "bourdieuvectors",
):
    cache_dir = user_cache_dir("bourdieu-vectors", model)
    print(f"Zipping cache dir {cache_dir}")

    with zipfile.ZipFile(target_zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        [
            zf.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), cache_dir))
            for r, _, files in os.walk(cache_dir)
            for f in files
        ]


def load_bourdieu_vector_cache(
    source_zip_file: str,
    model: str = "bourdieuvectors",
):
    cache_dir = user_cache_dir("bourdieu-vectors", model)
    print(f"Unzipping {source_zip_file} to {cache_dir}")

    os.makedirs(cache_dir, exist_ok=True)
    with zipfile.ZipFile(source_zip_file, "r") as zf:
        zf.extractall(cache_dir)

    print("Cache restored successfully.")
    return cache_dir
