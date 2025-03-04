# core/llm_optimizer.py
class LLMOptimizer:
    def __init__(self, chunk_size=16000):
        self.chunk_size = chunk_size

    def optimize_content(self, files, file_contents, include_metadata=True):
        """Splits content into LLM-friendly chunks with metadata."""
        chunks = []
        current_chunk = ""
        current_size = 0

        for rel_path, content in zip(files, file_contents):
            # Rough token estimation (1 token ~ 4 chars)
            content_size = len(content) // 4
            metadata = f"[FILE: {rel_path}]\n" if include_metadata else ""
            chunk_entry = metadata + content + "\n\n"

            if current_size + content_size > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = chunk_entry
                current_size = content_size
            else:
                current_chunk += chunk_entry
                current_size += content_size

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def set_chunk_size(self, size):
        self.chunk_size = size