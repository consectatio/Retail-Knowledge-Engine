import ollama

def generate_response(query, graph_analysis, language_model):
    '''uncomment to see input before it's sent to the llm
    print(f"Data:\n{'\n---\n'.join(graph_analysis)}\n\nQuestion: {query}")
    sentinel = True
    while sentinel:
        response = input("Does this prompt look good? (yes/no) : ")
        if response == "yes":
            sentinel = False
        elif response == "no":
            exit(1)
    '''
    default_prompt = ("You are a retail data analyst. Answer questions using only the provided data. "
                       "Respond in clear, natural English sentences. Do not copy raw data fields, "
                       "variable names, or formatting from the data. Instead, refer to products by "
                       "their description and summarize the relevant numbers conversationally.")
    output = ollama.chat (
        model = language_model,
        messages = [
            {'role': 'system', 'content': default_prompt},
            {"role": "user", "content": f"Data:\n{graph_analysis}\n\nQuestion: {query}"}
        ],
    )

    return output['message']['content']

def select_models():
    models = ollama.list()
    model_info = []
    language_models = []
    embedding_models = []

    model_index = 0
    print("Available Language Models:")
    for i, model in enumerate(models['models']):
        model_info.append(ollama.show(model['model']))
        if 'embedding' in model_info[i]['capabilities']: #most likely an embedding model don't append and save to different list
            embedding_models.append(model['model'])
        else:
            print(f"{model_index + 1}. {model['model']}")
            language_models.append(model['model'])
            model_index = model_index + 1
    answer = input('choose language model (input #): ')
    return_model = []
    try:
        return_model.append(language_models[int(answer) - 1])
    except (ValueError, IndexError):
        print('Invalid input')
        return select_models()

    print('Available Embeddings:')
    for i in range(len(embedding_models)):
        print(f'{i + 1}. {embedding_models[i]}')
    answer = input('choose embedding: ')
    try:
        return_model.append(embedding_models[int(answer) - 1])
        return return_model
    except (ValueError, IndexError):
        print('Invalid input')
        return select_models()