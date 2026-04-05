import ollama
from collections import Counter
from tqdm import tqdm

def start_embedding(embedding_model, graph):
    print('beginning embedding')
    vector_database = []
    for node_id, data in tqdm(graph.nodes(data=True), total=graph.number_of_nodes()):
        if data['type'] == 'product_id':
            #product node is connected to invoice number node with the edges for quantity and unit_price
            #get all the invoice number neighbors
            posCount = quantityTotal = priceTotal = returnCount = returnPrice = 0  # temporary variables
            countries = Counter()
            for neighbor in graph.neighbors(node_id):  # this will get neighboring invoice nodes
                edge_data = graph[neighbor][node_id]
                if edge_data.get('quantity') > 0:   #purchased
                    posCount += 1
                    quantityTotal += edge_data.get('quantity')
                    priceTotal += edge_data.get('unit_price')
                else:   #returned
                    returnCount += 1
                    returnPrice += edge_data.get('unit_price')

                for invoice_neighbors in graph.neighbors(neighbor): #from the invoice node find customer nodes
                    if graph.nodes[invoice_neighbors]['type'] == 'customer_id':
                        for customer_neighbors in graph.neighbors(invoice_neighbors): #from the customer node find country nodes
                            if graph.nodes[customer_neighbors]['type'] == 'country':
                                countries[customer_neighbors] += 1
                                break   #once country node is found we can go back because the same user ideally shouldn't be making invoices in different countries
                        break           #each invoice only has one customer so we can go back to

            if posCount > 0 and returnCount > 0:
                embed = f"""
                product id: {node_id} with the description: {data['description']}
                is on average purchased {quantityTotal/posCount:.2f} times per purchase
                at the average unit price of {priceTotal/posCount:.2f} and
                has been returned {returnCount} times
                at the average return price of {returnPrice/returnCount:.2f}
                from the countries: {', '.join(sorted(countries))}"""
            elif posCount > 0:
                embed = f"""
                product id: {node_id} with the description: {data['description']}
                is on average purchased {quantityTotal/posCount:.2f} times per purchase
                at the average unit price of {priceTotal/posCount:.2f}.
                from the countries: {', '.join(sorted(countries))}"""
            elif returnCount > 0:
                embed = f"""
                product id: {node_id} with the description: {data['description']}
                has been returned {returnCount} times
                at the average return price of {returnPrice/returnCount:.2f}.
                from the countries: {', '.join(sorted(countries))}"""
            else:
                continue
            embed = ' '.join(embed.split())
            response = ollama.embed(model = embedding_model, input = embed)
            vector_database.append({'id': node_id, 'text': embed, 'embedding': response['embeddings'][0], 'countries': list(countries.keys())})
    print('embedding done')
    return vector_database

def embed_query(query,vector_database, embedding_model, k=5):
    query_embedding = ollama.embed(model = embedding_model, input = query)['embeddings'][0]
    query_lower = query.lower()

    # check if any country in the database is mentioned in the query
    all_countries = set()
    for entry in vector_database:
        all_countries.update(entry['countries'])
    mentioned_countries = [c for c in all_countries if c.lower() in query_lower]

    # if a country is mentioned, only consider products sold in that country
    if mentioned_countries:
        print('country detected in query')
        filtered_db = [entry for entry in vector_database if any(c in entry['countries'] for c in mentioned_countries)]
    else:
        filtered_db = vector_database

    similarities = []
    for entry in filtered_db:
        similarity = cosine_similarity(query_embedding, entry['embedding'])
        similarities.append((entry, similarity))
    similarities.sort(key=lambda x:x[1], reverse = True)
    top_k = [s[0]['id'] for s in similarities[:k]]
    #print(f"closest nodes: {top_k}")
    return top_k

def cosine_similarity(a, b):
    dot_product = sum([x*y for x,y in zip(a,b)])
    norm_a = sum([x**2 for x in a]) ** .5
    norm_b = sum([x**2 for x in b]) ** .5
    return dot_product/(norm_a*norm_b)