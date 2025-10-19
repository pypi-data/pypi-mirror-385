# /mnt/24T/hugging_face/new_hugs/keybertManager/functions/module/keybert_module.py
from ..imports import *
DEFAULT_KEYBERT_PATH = "/mnt/24T/hugging_face/modules/all_minilm_l6_v2"

# ------------------------------------------------------------------------------
# 1. SENTENCE-BERT + KEYBERT LOADING & ENCODING
# ------------------------------------------------------------------------------
def load_sentence_bert_model(model_path: str = None):
    """
    Load a SentenceTransformer model that applies:
      1) Transformer (e.g. MiniLM-L6-v2) for token embeddings
      2) Mean pooling over token embeddings → one sentence vector
      3) L2-normalization → unit-length embeddings

    Args:
        model_path (str): Path to a local SBERT checkpoint (MiniLM-L6-v2).
                          Defaults to DEFAULT_KEYBERT_PATH.
    Returns:
        SentenceTransformer: A model that outputs normalized sentence embeddings.
    """
    models = get_models()
    SentenceTransformer = get_SentenceTransformer()

    path = model_path or DEFAULT_KEYBERT_PATH

    word_embedding_model = models.Transformer(
        model_name_or_path=str(path),
        max_seq_length=256,
        do_lower_case=False,
    )
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode="mean",
    )
    normalize_model = models.Normalize()
    return SentenceTransformer(modules=[word_embedding_model, pooling_model, normalize_model])

class nlpManager:
    def __init__(self):
        import importlib
        spacy = importlib.import_module("spacy")
        self.spacy = spacy
        self.nlp = self.spacy.load("en_core_web_sm")



class KeybertManager(metaclass=SingletonMeta):
    """
    Manages a SentenceTransformer-backed KeyBERT model.
    """
    
    def __init__(self, model_path: str = None):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.model_path = model_path or DEFAULT_KEYBERT_PATH
            self.lock = threading.Lock()
            self._sbert = load_sentence_bert_model(model_path=self.model_path)
            KeyBERT = get_KeyBERT()
            self._keybert = KeyBERT(self._sbert)
    def run_keybert_func(self,func,*args,**kwargs):
        return run_pruned_func(func, *args, **kwargs)
    @property
    def sbert(self):
        return self._sbert

    @property
    def keybert(self):
        return self._keyb


def get_keybert_model(model_path: str = None):
    """
    Convenience function to return the underlying SBERT model
    from a KeyBERTManager. If no manager exists, create one.

    Args:
        model_path (str): Optional override for the SBERT checkpoint path.

    Returns:
        SentenceTransformer: The SBERT model used by KeyBERT.
    """
    mgr = KeybertManager(model_path=model_path)
    return mgr.sbert
def encode_sentences(model=None, sentences: list[str] = None, model_path: str = None):
    """
    Encode a list of sentences (or documents) into normalized sentence embeddings.

    Args:
        model (SentenceTransformer): Pre-loaded SBERT model. If None, will load via get_keybert_model().
        sentences (list[str]): List of text strings to encode.
        model_path (str): Optional path override for SBERT.

    Returns:
        torch.Tensor: A [len(sentences) x D] tensor of embeddings, normalized to unit length.
    """
    torch = get_torch()
    m = model or get_keybert_model(model_path=model_path)
    return m.encode(
        sentences,
        convert_to_tensor=True,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

def compute_cosine_similarity(embeddings):
    """
    Given a batch of normalized embeddings, compute the full cosine similarity matrix.

    Args:
        embeddings (torch.Tensor): Tensor of shape [N, D], assumed L2-normalized.

    Returns:
        torch.Tensor: [N x N] matrix of cosine similarities.
    """
    cos_sim = get_cos_sim()
    return cos_sim(embeddings, embeddings)

def extract_keywords(
    text: str | list[str] = None,
    top_n: int = 5,
    diversity: float = 0.7,
    use_mmr: bool = True,
    stop_words: str = "english",
    keyphrase_ngram_range: tuple[int, int] = (1, 2),
    model=None,
    model_path: str = None,
):
    """
    Extract keywords using KeyBERT over SBERT embeddings.

    Args:
        text (str or list[str]): A document (string) or a list of documents.
        top_n (int): Number of keywords to return (per document if list). Defaults to 5.
        diversity (float): MMR diversity (0.0–1.0). Defaults to 0.7.
        use_mmr (bool): Whether to use Maximal Marginal Relevance. Defaults to True.
        stop_words (str): Language for stop words (e.g. 'english'). Defaults to 'english'.
        keyphrase_ngram_range (tuple): Range of n-gram lengths for candidate phrases (min_n, max_n).
        model (SentenceTransformer): Pre-loaded SBERT model to use. If None, loads default via model_path.
        model_path (str): Path to a local SBERT checkpoint if model is None.

    Returns:
        If text is a str: List[ (keyword, score) ].
        If text is a list[str]: List of lists, where each inner list is [ (keyword, score) ] for that document.
    """
    if text is None or (isinstance(text, (str, list)) and not text):
        raise ValueError("No content provided for keyword extraction.")

    sbert_model = model or get_keybert_model(model_path=model_path)
    KeyBERT = get_KeyBERT()
    kw = KeyBERT(sbert_model)

    docs = text if isinstance(text, list) else [text]
    return kw.extract_keywords(
        docs,
        keyphrase_ngram_range=keyphrase_ngram_range,
        stop_words=stop_words,
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=diversity,
    )
# ------------------------------------------------------------------------------
# 2. SPACY-BASED RULED KEYWORD + DENSITY
# ------------------------------------------------------------------------------



def extract_keywords_nlp(text: str, top_n: int = 5) -> list[str]:
    """
    A rule-based method to extract high-frequency nouns, proper nouns, and multi-word named entities.

    Args:
        text (str): Input text.
        top_n (int): Number of top keywords to return. Defaults to 5.

    Returns:
        list[str]: The top_n keywords (strings) sorted by frequency.
    """
    if not isinstance(text, str):
        raise ValueError(f"extract_keywords_nlp expects a string, got {type(text)}")
    nlp_mgr = nlpManager()

    doc = nlp_mgr.nlp(text)
    word_counts = Counter(
        token.text.lower()
        for token in doc
        if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop and len(token.text) > 3
    )
    entity_counts = Counter(
        ent.text.lower()
        for ent in doc.ents
        if len(ent.text.split()) >= 2 and ent.label_ in {"PERSON", "ORG", "GPE", "EVENT"}
    )
    combined = entity_counts + word_counts
    return [kw for kw, _ in combined.most_common(top_n)]



def calculate_keyword_density(text: str, keywords: list[str]) -> dict[str, float]:
    """
    Compute keyword density (%) for each keyword relative to total word count.

    Args:
        text (str): The full document text.
        keywords (list[str]): List of keywords (strings).

    Returns:
        dict[str, float]: Mapping from keyword → percentage of total words.
    """
    if not text:
        return {kw: 0.0 for kw in keywords}
    words = [w.strip(".,!?;:()\"'").lower() for w in re.split(r"\s+", text) if w.strip()]
    total_words = len(words)
    if total_words == 0:
        return {kw: 0.0 for kw in keywords}
    return {kw: (words.count(kw.lower()) / total_words) * 100 for kw in keywords}


def refine_keywords(
    text: str,
    top_n: int = 10,
    use_mmr: bool = True,
    diversity: float = 0.5,
    keyphrase_ngram_range: tuple[int, int] = (1, 3),
    stop_words: str = "english",
    model=None,
    model_path: str = None,
    info_data: dict = None,
) -> dict:
    """
    Combine rule-based (spaCy) and embedding-based (KeyBERT) keywords, plus density statistics.

    Args:
        full_text (str): The full document text.
        top_n (int): Number of top keywords from each method. Defaults to 10.
        use_mmr (bool): Whether KeyBERT uses MMR. Defaults to True.
        diversity (float): MMR diversity parameter. Defaults to 0.5.
        keyphrase_ngram_range (tuple): Range of n-grams for KeyBERT. Defaults to (1, 3).
        stop_words (str): Stop words language for KeyBERT. Defaults to 'english'.
        model (SentenceTransformer): SBERT model for KeyBERT. If None, loaded via model_path.
        model_path (str): Path to SBERT checkpoint if model is None.
        info_data (dict): Optional dict to populate with results. If None, a new dict is created.

    Returns:
        dict containing:
            - "keywords_nlp": list[str]   → top nouns/entities by frequency
            - "keywords_keybert": list[tuple[str, float]] → top KeyBERT keyphrases + scores
            - "combined_keywords": list[str] → deduplicated, lowercase set of keywords (max top_n)
            - "keyword_density": dict[str, float] → density % for each combined keyword
    """
    if info_data is None:
        info_data = {}
    nlp_kws = extract_keywords_nlp(text, top_n=top_n)
    info_data["keywords_nlp"] = nlp_kws

    keybert_kws = extract_keywords(
        text=text,
        top_n=top_n,
        diversity=diversity,
        use_mmr=use_mmr,
        stop_words=stop_words,
        keyphrase_ngram_range=keyphrase_ngram_range,
        model=model,
        model_path=model_path,
    )
    keybert_phrases = [phrase for phrase, _ in keybert_kws]
    info_data["keywords_keybert"] = keybert_kws

    merged_set = set([kw.lower() for kw in nlp_kws] + [kp.lower() for kp in keybert_phrases])
    combined = list(merged_set)[:top_n]
    info_data["combined_keywords"] = combined

    densities = calculate_keyword_density(text, combined)
    info_data["keyword_density"] = densities

    return info_data

def get_keybert_mgr(model_path=None):
    return KeybertManager(model_path=model_path)
def run_keybert_func(func,*args,model_path=None,**kwargs):
    keybert_mgr = get_keybert_mgr(model_path=model_path)
    return keybert_mgr.run_keybert_func(func,*args,**kwargs)







