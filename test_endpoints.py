# Thử format OpenAI request
data_openai = {
    "model": "sonar-medium-chat",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
}

# Thử format Perplexity request theo tài liệu
data_perplexity = {
    "model": "sonar-medium-chat",
    "query": "Hello, how are you?"
} 