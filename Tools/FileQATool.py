import os
from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.chains import RetrievalQA

from Models.Factory import ChatModelFactory, EmbeddingModelFactory

# 文件大小阈值（字节），超过此值使用 RAG 方式，否则使用长上下文直接提问
# 1MB 以内的文档，提取的文本通常在长上下文模型的窗口范围内
FILE_SIZE_THRESHOLD = 1 * 1024 * 1024  # 1MB


class FileLoadFactory:
    @staticmethod
    def get_loader(filename: str):
        ext = get_file_extension(filename)
        if ext == "pdf":
            return PyMuPDFLoader(filename)
        elif ext == "docx" or ext == "doc":
            return UnstructuredWordDocumentLoader(filename)
        else:
            raise NotImplementedError(f"File extension {ext} not supported.")


def get_file_extension(filename: str) -> str:
    return filename.split(".")[-1]


def load_docs(filename: str) -> List[Document]:
    file_loader = FileLoadFactory.get_loader(filename)
    pages = file_loader.load_and_split()
    return pages


def _ask_with_long_context(docs: List[Document], query: str) -> str:
    """将文档全文直接发送给 LLM，利用长上下文能力回答问题"""
    full_text = "\n".join(str(doc.page_content) for doc in docs)
    llm = ChatModelFactory.get_default_model()
    prompt = f"""请根据以下文档内容回答用户的问题。如果文档中没有相关信息，请如实说明。

文档内容：
{full_text}

用户问题：{query}

请用中文回答："""
    response = llm.invoke(prompt)
    return response.content


def _ask_with_rag(docs: List[Document], query: str) -> str:
    """使用 RAG 方式：分块 → 向量化 → 检索 → 生成"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    documents = text_splitter.split_documents(docs)
    if documents is None or len(documents) == 0:
        return "无法读取文档内容"
    # 确保所有文档的 page_content 为字符串，并过滤空内容
    for doc in documents:
        doc.page_content = str(doc.page_content).strip()
    documents = [doc for doc in documents if doc.page_content]
    if len(documents) == 0:
        return "无法读取文档内容"
    db = Chroma.from_documents(documents, EmbeddingModelFactory.get_default_model())
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatModelFactory.get_default_model(),
        chain_type="stuff",  # 表示将所有检索到的文档块合并成一个 prompt，一次性发送给 LLM。
        retriever=db.as_retriever()  # 检索器
    )
    response = qa_chain.run(query + "(请用中文回答)")
    return response


def ask_docment(
        filename: str,
        query: str,
) -> str:
    """根据一个文档的内容，回答一个问题。
    小文件使用长上下文直接提问，大文件使用 RAG 方式。"""

    file_size = os.path.getsize(filename)
    raw_docs = load_docs(filename)
    if len(raw_docs) == 0:
        return "抱歉，文档内容为空"

    if file_size <= FILE_SIZE_THRESHOLD:
        # 文件较小，直接使用长上下文
        return _ask_with_long_context(raw_docs, query)
    else:
        # 文件较大，使用 RAG 方式
        return _ask_with_rag(raw_docs, query)


if __name__ == "__main__":
    filename = "../data/3.pdf"
    query = "销售额定义"
    print(ask_docment(filename, query))
