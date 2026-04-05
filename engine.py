import pandas as pd
from graph import create_graph, traverse
from embedding import start_embedding, embed_query
from LLM import generate_response, select_models

def start_engine():
    df = read_data()                                                  #read data (df)
    graph = create_graph(df)                                          #build graph
    models = select_models()                                          #select models, [0] = language, [1] = embedding
    vector_database = start_embedding(models[1], graph)               #begin embedding process

    while True:
        query = input('Enter query (type exit to quit): ')
        if query == 'exit':
            exit(1)
        start_node = embed_query(query,vector_database, models[1], 20)        #embed query, returns: list of closest node

        graph_analysis = []
        for node_id in start_node:
            graph_analysis.append(traverse(graph, node_id))               #gets the traversal data from the start node to be sent to the llm
        print(generate_response(query, graph_analysis, models[0]))

def read_data():
    print('reading data')
    try:
        df = pd.read_csv('./data/online_retail.csv')
        print('data read successfully')
        return df
    except FileNotFoundError:
        print('data not found...ending')
        exit(0)