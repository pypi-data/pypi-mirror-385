#
# Copyright 2025 Tabs Data Inc.
#

import logging

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever, MultiQueryRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool, Tool
from langchain_core.vectorstores import VectorStore

from tabsdata_agent._core.constants import (
    faiss_index_folder,
    rag_prompt_file,
)

logger = logging.getLogger(__name__)


class RagToolFactory:
    def __init__(
        self,
        llm: BaseLanguageModel,
        embeddings: Embeddings,
        vectorstore: VectorStore = None,
        prompt: str = None,
        docs_retrieved: int = 5,
    ):
        self.llm = llm
        self.vectorstore = vectorstore or self._deserialize_vectorstore(embeddings)
        self.prompt = prompt or self._load_rag_prompt()
        self.docs_retrieved = docs_retrieved

    @staticmethod
    def _deserialize_vectorstore(embeddings: Embeddings) -> VectorStore:
        try:
            vectorstore = FAISS.load_local(
                faiss_index_folder,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            return vectorstore
        except Exception as e:
            logger.error(
                f"Error: could not load FAISS index from {faiss_index_folder}: {e}",
            )
            raise e

    @staticmethod
    def _load_rag_prompt():
        try:
            with open(rag_prompt_file, "r", encoding="utf-8") as _f:
                prompt = _f.read()
        except Exception as e:
            raise ValueError(f"Could not read RAG prompt file {rag_prompt_file}: {e}")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"RAG prompt file is empty: {rag_prompt_file}")
        return prompt

    def get_tool(self) -> BaseTool:
        rag_prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["context", "question"],
        )

        def retrieve_with_metadata(query, filters=None, fast_mode=True):
            search_kwargs = {"k": self.docs_retrieved}
            if filters:
                search_kwargs["filter"] = filters
            base_retriever = self.vectorstore.as_retriever(search_kwargs=search_kwargs)

            if fast_mode:
                # Fast path: use only the base retriever (FAISS)
                rag_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    retriever=base_retriever,
                    chain_type="stuff",
                    chain_type_kwargs={"prompt": rag_prompt},
                    # Care with this, as it can easily make the output too long
                    # return_source_documents=True
                )
            else:
                # Full path: MultiQuery + Compression
                multiquery_retriever = MultiQueryRetriever.from_llm(
                    retriever=base_retriever, llm=self.llm
                )
                compressor = LLMChainExtractor.from_llm(self.llm)
                compression_retriever = ContextualCompressionRetriever(
                    base_compressor=compressor,
                    base_retriever=multiquery_retriever,
                )
                rag_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    retriever=compression_retriever,
                    chain_type="stuff",
                    chain_type_kwargs={"prompt": rag_prompt},
                    # Care with this, as it can easily make the output too long
                    # return_source_documents=True
                )

            result = rag_chain.invoke(query)
            return result

        rag_tool = Tool(
            name="TabsdataCodeRetriever",
            description=(
                "Use when asked about any question that requires code. Supports"
                " optional metadata filters (e.g., tags) and fast_mode for speed. Call"
                " as func(query, filters=None, fast_mode=False)"
            ),
            func=retrieve_with_metadata,
        )

        return rag_tool
