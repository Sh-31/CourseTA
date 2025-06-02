from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
 

examples = [
    {
        "context": "Cloud computing services, AWS pricing, serverless architecture, microservices deployment",
        "question": "How much does AWS Lambda cost?",
        "classification": "Yes"
    },
    {
        "context": "Cloud computing services, AWS pricing, serverless architecture, microservices deployment",
        "question": "What's the weather like today?",
        "classification": "No"
    },
    {
        "context": "Python programming, machine learning algorithms, data preprocessing, model training",
        "question": "How do I implement a neural network in Python?",
        "classification": "Yes"
    },
    {
        "context": "Python programming, machine learning algorithms, data preprocessing, model training",
        "question": "What's the capital of France?",
        "classification": "No"
    },
    {
        "context": "Customer support policies, refund procedures, warranty information, technical troubleshooting",
        "question": "How do I return a defective product?",
        "classification": "Yes"
    },
    {
        "context": "Customer support policies, refund procedures, warranty information, technical troubleshooting",
        "question": "Tell me a joke about cats",
        "classification": "No"
    }
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages([
        ("user", "Context: {context}\nQuestion: {question}"),
        ("ai", "Classification: {classification}")
    ]),
    examples=examples
)

GradeQuestionPrompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a classifier that determines whether a user's question is related to the provided context topics. Respond with 'Yes' if related, 'No' if not related."),
        few_shot_prompt,
        ("user", "Context: {docs}\nQuestion: {question} \n Classification: ")
    ]
)